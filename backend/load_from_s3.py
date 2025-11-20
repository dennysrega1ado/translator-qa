#!/usr/bin/env python3
"""
Script to load data directly from AWS S3 into the database
Usage: python load_from_s3.py <s3_prefix> <description>
"""
import sys
import hashlib
import uuid
from pathlib import Path
from app.database import SessionLocal
from app import models
from app.s3_service import s3_service


def extract_text_content(data):
    """Extract summary and insight texts from JSON"""
    texts = []

    # Add summary
    if 'summary' in data:
        texts.append(data['summary'])

    # Add insight texts
    for i in range(1, 4):
        insight_key = f'insight{i}'
        if insight_key in data and 'text' in data[insight_key]:
            texts.append(data[insight_key]['text'])

    return '\n\n'.join(texts)


def load_from_s3(prefix, description):
    """Load all translations from S3 with given prefix and description"""
    db = SessionLocal()

    # Remove trailing slash for consistency
    prefix = prefix.strip().rstrip('/')

    try:
        # Generate execution_id from prefix + description (deterministic UUID)
        combined = f"{prefix}|{description}"
        combined_hash = hashlib.md5(combined.encode()).hexdigest()
        execution_id = str(uuid.UUID(combined_hash))

        print(f"\n📋 Execution ID: {execution_id}")
        print(f"   (generated from prefix + description hash)")

        # Check if this execution_id already exists
        existing_count = db.query(models.Translation).filter(
            models.Translation.execution_id == execution_id
        ).count()

        if existing_count > 0:
            print(f"\n⚠️  Translations from this prefix already loaded!")
            print(f"   Execution ID: {execution_id}")
            print(f"   Existing translations: {existing_count}")
            print(f"\n   Skipping load to avoid duplicates.")
            return

        # List all objects in S3 for the given prefix
        print(f"\n🔍 Scanning S3 for prefix: {prefix}")
        all_objects = s3_service.list_objects(prefix=prefix)

        # Get English and Spanish files separately
        en_files = [obj for obj in all_objects if '/en/' in obj and obj.endswith('.json')]
        es_files = [obj for obj in all_objects if '/es/' in obj and obj.endswith('.json')]

        # Create a set of translation IDs that have Spanish translations
        es_ids = set()
        for es_path in es_files:
            translation_id = es_path.split('/')[-1].replace('.json', '')
            es_ids.add(translation_id)

        # Filter English files to only those with Spanish translations
        en_files_with_translation = []
        for en_path in en_files:
            translation_id = en_path.split('/')[-1].replace('.json', '')
            if translation_id in es_ids:
                en_files_with_translation.append(en_path)

        print(f"✓ Found {len(en_files)} English files")
        print(f"✓ Found {len(es_files)} Spanish files")
        print(f"✓ Found {len(en_files_with_translation)} complete translation pairs\n")

        if not en_files_with_translation:
            print("⚠️  No complete translation pairs found in S3.")
            print("   Make sure you have matching files in:")
            print("   s3://your-bucket/base-path/llm-output/2025/10/latest/en/*.json")
            print("   s3://your-bucket/base-path/llm-output/2025/10/latest/es/*.json")
            return

        # Process each translation
        loaded_count = 0
        prompts_created = set()

        for idx, en_path in enumerate(en_files_with_translation):
            try:
                # Extract translation ID
                translation_id = en_path.split('/')[-1].replace('.json', '')

                # Construct ES path
                es_path = en_path.replace('/en/', '/es/')

                print(f"[{idx + 1}/{len(en_files_with_translation)}] Processing: {translation_id}")

                # Load English original from S3
                en_data = s3_service.get_json(en_path)
                if not en_data:
                    print(f"  ⚠️  Could not load English file, skipping...")
                    continue

                # Load Spanish translation from S3
                es_data = s3_service.get_json(es_path)
                if not es_data:
                    print(f"  ⚠️  Could not load Spanish file, skipping...")
                    continue

                # Extract fields from JSON
                original_content = en_data.get('original_content') or en_data.get('original') or extract_text_content(en_data)
                translated_content = es_data.get('translated_content') or es_data.get('translation') or extract_text_content(es_data)
                prompt_id_str = en_data.get('prompt_id', 'default')
                prompt_name = en_data.get('prompt_name', prompt_id_str)

                # Get or create prompt
                prompt = db.query(models.Prompt).filter(
                    models.Prompt.prompt_id == prompt_id_str
                ).first()

                if not prompt:
                    prompt = models.Prompt(
                        prompt_id=prompt_id_str,
                        name=prompt_name,
                        description=f"Auto-created from S3 import: {prefix}"
                    )
                    db.add(prompt)
                    db.flush()
                    prompts_created.add(prompt_id_str)
                    print(f"  ✓ Created prompt: {prompt_name}")

                # Extract automated scores
                automated_scores = en_data.get('automated_scores') or es_data.get('automated_scores') or es_data.get('score', {})
                coherence = automated_scores.get('coherence', 0)
                fidelity = automated_scores.get('fidelity', 0)
                naturalness = automated_scores.get('naturalness', 0)
                overall = automated_scores.get('overall', 0)

                if coherence or fidelity or naturalness:
                    print(f"  ✓ Scores: coherence={coherence}, fidelity={fidelity}, naturalness={naturalness}")
                else:
                    print(f"  ⚠️  No scores found, using defaults")

                # Create translation
                translation = models.Translation(
                    execution_id=execution_id,
                    execution_description=description,
                    prompt_id=prompt.id,
                    original_content=original_content,
                    translated_content=translated_content,
                    source_language="en",
                    target_language="es",
                    automated_coherence=coherence,
                    automated_fidelity=fidelity,
                    automated_naturalness=naturalness,
                    automated_overall=overall,
                    s3_insights_path=en_path,
                    s3_automated_qa_path=es_path
                )
                db.add(translation)
                db.commit()
                print(f"  ✓ Created translation for {translation_id}")
                loaded_count += 1

            except Exception as e:
                print(f"  ❌ Error processing {en_path}: {e}")
                db.rollback()
                continue

        print(f"\n{'='*60}")
        print(f"✅ Successfully loaded {loaded_count} translation(s) from S3!")
        print(f"{'='*60}")

        # Print summary
        total_translations = db.query(models.Translation).count()
        print(f"\n📊 Summary:")
        print(f"   Execution ID: {execution_id}")
        print(f"   Translations loaded: {loaded_count}")
        print(f"   Prompts created: {len(prompts_created)}")
        print(f"\n📊 Database Totals:")
        print(f"   Total Prompts: {db.query(models.Prompt).count()}")
        print(f"   Total Translations: {total_translations}")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ Error loading from S3: {e}")
        print(f"{'='*60}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n❌ Usage: python load_from_s3.py <s3_prefix> <description>")
        print("\nExample:")
        print("   docker compose exec backend python load_from_s3.py 'translations/batch-01' 'October 2024 batch'")
        print("   docker compose exec backend python load_from_s3.py 'translations/llm-output/2025/10/latest' 'Latest translations'")
        sys.exit(1)

    prefix = sys.argv[1]
    description = sys.argv[2]

    print("="*60)
    print("Loading translations from AWS S3...")
    print("="*60)
    print(f"Prefix: {prefix}")
    print(f"Description: {description}")

    load_from_s3(prefix, description)
