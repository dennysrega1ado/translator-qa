#!/usr/bin/env python3
"""
Script to load data directly from AWS S3 into the database
"""
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


def load_from_s3():
    """Load all translations from S3"""
    db = SessionLocal()

    try:
        # Create sample prompt
        prompt_data = {
            "prompt_id": "prompt_001",
            "name": "Monthly Insights Translation",
            "description": "Translation of monthly financial insights and summaries"
        }

        # Check if prompt exists
        existing_prompt = db.query(models.Prompt).filter(
            models.Prompt.prompt_id == prompt_data["prompt_id"]
        ).first()

        if not existing_prompt:
            prompt = models.Prompt(**prompt_data)
            db.add(prompt)
            db.commit()
            db.refresh(prompt)
            print(f"✓ Created prompt: {prompt_data['name']}")
        else:
            prompt = existing_prompt
            print(f"✓ Prompt already exists: {prompt_data['name']}")

        # List all objects in S3 for specific period: 2025/10/latest
        print("\n🔍 Scanning S3 for 2025/10/latest files...")
        all_objects = s3_service.list_objects(prefix="translations/llm-output/2025/10/latest/")

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
        for idx, en_path in enumerate(en_files_with_translation):
            try:
                # Extract translation ID and construct paths
                # Format: llm-output/2025/10/latest/en/52fa10a0f67541a98ce0c2ccba458f9c.json
                parts = en_path.split('/')
                translation_id = parts[-1].replace('.json', '')
                year = parts[1]
                month = parts[2]

                # Construct ES path
                es_path = en_path.replace('/en/', '/es/')

                print(f"[{idx + 1}/{len(en_files_with_translation)}] Processing: {translation_id}")

                # Load English original from S3
                en_data = s3_service.get_json(en_path)
                if not en_data:
                    print(f"  ⚠️  Could not load English file, skipping...")
                    continue
                en_text = extract_text_content(en_data)

                # Load Spanish translation from S3
                es_data = s3_service.get_json(es_path)
                if not es_data:
                    print(f"  ⚠️  Could not load Spanish file, skipping...")
                    continue
                es_text = extract_text_content(es_data)

                # Extract automated scores from Spanish file
                if 'score' in es_data:
                    score_data = es_data['score']
                    coherence = score_data.get('coherence', 0)
                    fidelity = score_data.get('fidelity', 0)
                    naturalness = score_data.get('naturalness', 0)
                    overall = score_data.get('overall', 0)
                    print(f"  ✓ Scores: coherence={coherence}, fidelity={fidelity}, naturalness={naturalness}")
                else:
                    coherence = fidelity = naturalness = overall = 0
                    print(f"  ⚠️  No scores found, using defaults")

                # Create execution ID based on year/month
                execution_id = f"exec_{year}_{month}"

                # Check if translation already exists
                existing_trans = db.query(models.Translation).filter(
                    models.Translation.execution_id == execution_id,
                    models.Translation.original_content == en_text
                ).first()

                if existing_trans:
                    print(f"  ℹ️  Translation already exists, skipping...")
                    continue

                # Create translation
                translation = models.Translation(
                    execution_id=execution_id,
                    prompt_id=prompt.id,
                    original_content=en_text,
                    translated_content=es_text,
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
        print(f"\n📊 Database Summary:")
        print(f"   Prompts: {db.query(models.Prompt).count()}")
        print(f"   Translations: {total_translations}")

    except Exception as e:
        print(f"❌ Error loading from S3: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Loading translations from AWS S3...")
    print("="*60)
    load_from_s3()
