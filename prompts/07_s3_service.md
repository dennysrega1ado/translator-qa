# Step 7: S3 Storage Service

## Prompt

Implement the S3 service for loading translation data from S3-compatible storage (MinIO locally, AWS S3 in production).

### Context

We need to load translation data from S3 buckets. The data is stored in JSON format with a specific structure:
- `prefix/en/insights.json` - Original English text
- `prefix/es/insights.json` - Spanish translations
- `prefix/es/automated_qa.json` - Automated quality scores

### Requirements

**Data Structure:**

English insights.json:
```json
[
  {
    "id": "uuid-string",
    "content": "English text here..."
  }
]
```

Spanish insights.json:
```json
[
  {
    "id": "uuid-string",
    "content": "Texto en español aquí..."
  }
]
```

Automated QA JSON:
```json
[
  {
    "id": "uuid-string",
    "coherence": 8.5,
    "fidelity": 9.0,
    "naturalness": 8.0,
    "overall": 8.5
  }
]
```

**S3 Service Features:**
- Connect to S3-compatible storage (MinIO or AWS S3)
- List objects in bucket
- Download JSON files
- Parse and match translations by ID
- Create prompt records if they don't exist
- Bulk insert translations into database
- Support for both MinIO (local) and AWS S3 (production)

**Configuration:**
- Support `STORAGE_BACKEND` env var: "s3" or "minio"
- For MinIO: MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
- For S3: AWS_S3_BUCKET, AWS_REGION, use IAM role or credentials

### Tasks

Please create:

1. **`backend/app/s3_service.py`**:
   - S3Service class with methods:
     - `__init__()`: Initialize boto3 client based on STORAGE_BACKEND
     - `list_objects(prefix)`: List objects with given prefix
     - `download_json(key)`: Download and parse JSON file
     - `load_translations(prefix, execution_id, execution_description)`:
       - Download en/insights.json, es/insights.json, es/automated_qa.json
       - Match by ID
       - Create/update prompt records
       - Bulk insert translations
       - Return count of loaded translations
     - `validate_prefix(prefix)`: Check if prefix has required structure
   - Error handling for missing files or invalid JSON
   - Logging for debugging

2. **`backend/app/routers/admin.py`**:
   - `POST /api/admin/validate-prefix`:
     - Validate S3 prefix has required files
     - Return validation result with file counts
   - `POST /api/admin/load-translations`:
     - Accept prefix and execution_description
     - Generate execution_id (timestamp-based)
     - Call s3_service.load_translations()
     - Return success message with count
   - `POST /api/admin/clean-tables`:
     - Delete all manual_scores, translations, and prompts (WARNING!)
     - Return success message
   - All admin-only routes

3. **Update `backend/app/config.py`**:
   - Add S3/MinIO configuration
   - Storage backend selection logic

4. **Update `backend/requirements.txt`**:
   - Add `boto3` for S3 access

### Expected Output

After implementation:
- Can validate S3 prefix: `POST /api/admin/validate-prefix` with {"prefix": "translations/batch-01"}
- Can load translations: `POST /api/admin/load-translations` with {"prefix": "...", "execution_description": "October 2024 batch"}
- Translations are matched by ID and stored in database
- Automated scores are preserved
- Works with both MinIO (local) and AWS S3 (production)
- Proper error handling for missing files
