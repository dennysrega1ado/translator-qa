#!/usr/bin/env python3
"""
Script to load sample data into the database and MinIO
"""
import json
import os
from pathlib import Path
from app.database import SessionLocal
from app import models
from app.s3_service import s3_service


def load_json_file(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def upload_to_minio(local_path, s3_path):
    """Upload JSON file to MinIO"""
    data = load_json_file(local_path)
    s3_service.upload_json(s3_path, data)
    return s3_path


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


def load_sample_data():
    """Load all sample data"""
    db = SessionLocal()

    try:
        # Create sample prompts
        prompts_data = [
            {
                "prompt_id": "prompt_001",
                "name": "Monthly Insights Translation",
                "description": "Translation of monthly financial insights and summaries"
            }
        ]

        prompts = {}
        for prompt_data in prompts_data:
            # Check if prompt exists
            existing = db.query(models.Prompt).filter(
                models.Prompt.prompt_id == prompt_data["prompt_id"]
            ).first()

            if not existing:
                prompt = models.Prompt(**prompt_data)
                db.add(prompt)
                db.commit()
                db.refresh(prompt)
                prompts[prompt_data["prompt_id"]] = prompt
                print(f"Created prompt: {prompt_data['name']}")
            else:
                prompts[prompt_data["prompt_id"]] = existing
                print(f"Prompt already exists: {prompt_data['name']}")

        # Load sample data files
        sample_data_dir = Path(__file__).parent / "sample_data"

        # Find all llm-output directories with the pattern llm-output/YYYY/MM/latest
        llm_output_dir = sample_data_dir / "llm-output"

        if not llm_output_dir.exists():
            print("Warning: llm-output directory not found")
            return

        # Find all 'latest' directories
        latest_dirs = list(llm_output_dir.glob("*/*/latest"))

        if not latest_dirs:
            print("Warning: No llm-output/YYYY/MM/latest directories found")
            return

        print(f"\nFound {len(latest_dirs)} llm-output directory(ies)")

        # Process each latest directory
        for latest_dir in latest_dirs:
            # Extract year and month from path
            month = latest_dir.parent.name
            year = latest_dir.parent.parent.name
            print(f"\nProcessing {year}/{month}/latest...")

            # Get all translation IDs from the en folder
            en_folder = latest_dir / "en"
            if not en_folder.exists():
                print(f"  Warning: en folder not found in {latest_dir}")
                continue

            translation_ids = [f.stem for f in en_folder.glob("*.json")]
            print(f"  Found {len(translation_ids)} translation files")

            # Upload to MinIO and create translations
            execution_id = f"exec_{year}_{month}"

            for idx, translation_id in enumerate(translation_ids):
                print(f"\n  Processing translation {idx + 1}/{len(translation_ids)}: {translation_id}")

                # Load English original
                en_file_path = en_folder / f"{translation_id}.json"
                en_data = load_json_file(en_file_path)
                en_text = extract_text_content(en_data)

                # Load Spanish translation
                es_folder = latest_dir / "es"
                es_file_path = es_folder / f"{translation_id}.json"
                es_data = load_json_file(es_file_path)
                es_text = extract_text_content(es_data)

                # Extract automated scores from the 'score' object in es file
                if 'score' in es_data:
                    score_data = es_data['score']
                    coherence = score_data.get('coherence', 0)
                    fidelity = score_data.get('fidelity', 0)
                    naturalness = score_data.get('naturalness', 0)
                    overall = score_data.get('overall', 0)
                    print(f"    Loaded scores: coherence={coherence}, fidelity={fidelity}, naturalness={naturalness}")
                else:
                    # Default scores if score object doesn't exist
                    coherence = fidelity = naturalness = overall = 0
                    print(f"    Warning: No score object found for {translation_id}, using defaults")

                # Upload to MinIO with the full path structure
                s3_en_path = upload_to_minio(en_file_path, f"llm-output/{year}/{month}/latest/en/{translation_id}.json")
                s3_es_path = upload_to_minio(es_file_path, f"llm-output/{year}/{month}/latest/es/{translation_id}.json")
                print(f"    Uploaded to MinIO: {translation_id}")

                # Create translation
                translation = models.Translation(
                    execution_id=execution_id,
                    prompt_id=prompts["prompt_001"].id,
                    original_content=en_text,
                    translated_content=es_text,
                    source_language="en",
                    target_language="es",
                    automated_coherence=coherence,
                    automated_fidelity=fidelity,
                    automated_naturalness=naturalness,
                    automated_overall=overall,
                    s3_insights_path=s3_en_path,
                    s3_automated_qa_path=s3_es_path
                )
                db.add(translation)
                db.commit()
                print(f"    Created translation for {translation_id}")

        print("\nSample data loaded successfully!")

        # Print summary
        total_prompts = db.query(models.Prompt).count()
        total_translations = db.query(models.Translation).count()
        print(f"\nDatabase Summary:")
        print(f"  Prompts: {total_prompts}")
        print(f"  Translations: {total_translations}")

    except Exception as e:
        print(f"Error loading sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Loading sample data...")
    load_sample_data()
