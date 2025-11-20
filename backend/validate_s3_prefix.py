#!/usr/bin/env python3
"""
Script to validate S3 prefix for translation loading
Usage: docker compose exec backend python validate_s3_prefix.py <prefix>
"""
import sys
from app.s3_service import s3_service


def validate_prefix(prefix: str):
    """Validate S3 prefix and show structure"""
    print(f"\n{'='*70}")
    print(f"Validating S3 prefix: {prefix}")
    print(f"{'='*70}\n")

    # Remove trailing slash for consistency
    prefix = prefix.strip().rstrip('/')

    if not prefix:
        print("❌ Error: Prefix cannot be empty")
        return False

    try:
        # List all objects with the prefix
        print(f"🔍 Scanning S3 bucket for prefix: {prefix}")
        objects = s3_service.list_objects(prefix=prefix)

        if not objects:
            print(f"\n❌ No objects found at prefix: {prefix}")
            print(f"\n💡 Tips:")
            print(f"   - Check that the prefix path is correct")
            print(f"   - Verify you have access to the S3 bucket")
            print(f"   - Make sure the prefix doesn't start with '/'")
            return False

        print(f"✓ Found {len(objects)} objects\n")

        # Check for en/ and es/ folders
        en_files = [obj for obj in objects if '/en/' in obj or obj.startswith('en/')]
        es_files = [obj for obj in objects if '/es/' in obj or obj.startswith('es/')]
        json_files = [obj for obj in objects if obj.endswith('.json')]

        has_en = len(en_files) > 0
        has_es = len(es_files) > 0

        print(f"📂 Folder Structure:")
        print(f"   {'✓' if has_en else '✗'} en/ folder: {len(en_files)} files")
        print(f"   {'✓' if has_es else '✗'} es/ folder: {len(es_files)} files")
        print(f"   📄 JSON files: {len(json_files)} files")

        # Show validation result
        print(f"\n{'='*70}")
        if has_en and has_es:
            print(f"✅ VALID PREFIX - Contains both en/ and es/ folders")
        else:
            missing = []
            if not has_en:
                missing.append("en/")
            if not has_es:
                missing.append("es/")
            print(f"❌ INVALID PREFIX - Missing required folders: {', '.join(missing)}")

        print(f"{'='*70}")

        # Show sample files
        if json_files:
            print(f"\n📋 Sample JSON files (first 10):")
            for i, file_path in enumerate(json_files[:10], 1):
                # Show relative path from prefix
                display_path = file_path
                if file_path.startswith(prefix):
                    display_path = file_path[len(prefix):].lstrip('/')
                print(f"   {i:2}. {display_path}")

        # Show detailed breakdown
        print(f"\n📊 File Breakdown:")
        print(f"   English JSON files: {len([f for f in en_files if f.endswith('.json')])}")
        print(f"   Spanish JSON files: {len([f for f in es_files if f.endswith('.json')])}")

        # Check for matching pairs
        if has_en and has_es:
            en_json = [f for f in en_files if f.endswith('.json')]
            es_json = [f for f in es_files if f.endswith('.json')]

            # Extract file IDs
            en_ids = set()
            for f in en_json:
                filename = f.split('/')[-1]
                en_ids.add(filename)

            es_ids = set()
            for f in es_json:
                filename = f.split('/')[-1]
                es_ids.add(filename)

            matching = en_ids & es_ids
            en_only = en_ids - es_ids
            es_only = es_ids - en_ids

            print(f"\n🔗 Translation Pairs:")
            print(f"   Matching pairs: {len(matching)}")
            if en_only:
                print(f"   ⚠️  English only: {len(en_only)}")
            if es_only:
                print(f"   ⚠️  Spanish only: {len(es_only)}")

        # Show next steps
        if has_en and has_es:
            print(f"\n✨ Next Steps:")
            print(f"   You can now load translations using the Admin panel or:")
            print(f"   docker compose exec backend python load_from_s3_prefix.py '{prefix}'")
        else:
            print(f"\n💡 Please ensure your S3 structure looks like:")
            print(f"   {prefix}/")
            print(f"   ├── en/")
            print(f"   │   ├── file1.json")
            print(f"   │   └── file2.json")
            print(f"   └── es/")
            print(f"       ├── file1.json")
            print(f"       └── file2.json")

        print(f"\n{'='*70}\n")
        return has_en and has_es

    except Exception as e:
        print(f"\n❌ Error validating prefix: {e}")
        print(f"\n💡 Common issues:")
        print(f"   - AWS credentials not configured")
        print(f"   - No access to the S3 bucket")
        print(f"   - Network connectivity problems")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ Usage: python validate_s3_prefix.py <prefix>")
        print("\nExample:")
        print("   docker compose exec backend python validate_s3_prefix.py 'translations/batch-01'")
        print("   docker compose exec backend python validate_s3_prefix.py 'translations/llm-output/2025/10/latest'")
        sys.exit(1)

    prefix = sys.argv[1]
    is_valid = validate_prefix(prefix)

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)
