# Step 2: Database Models & Configuration

## Prompt

Now let's implement the database layer for the Translation QA System.

### Context

We have the project structure set up with FastAPI backend and PostgreSQL database. Now we need to define the SQLAlchemy models and database configuration.

### Requirements

**Database Models (4 tables):**

1. **User Model** (`users` table):
   - id: Integer, primary key
   - username: String(50), unique, indexed
   - email: String(100), unique, indexed
   - hashed_password: String(255)
   - is_admin: Boolean, default False
   - is_active: Boolean, default True
   - created_at: DateTime with timezone
   - updated_at: DateTime with timezone
   - Relationship: one-to-many with manual_scores

2. **Prompt Model** (`prompts` table):
   - id: Integer, primary key
   - prompt_id: String(100), unique, indexed
   - name: String(200)
   - description: Text, nullable
   - created_at: DateTime with timezone
   - Relationship: one-to-many with translations

3. **Translation Model** (`translations` table):
   - id: Integer, primary key
   - execution_id: String(100), indexed (for batch filtering)
   - execution_description: String(500), nullable (human-readable batch name)
   - prompt_id: Integer, foreign key to prompts
   - original_content: Text
   - translated_content: Text
   - source_language: String(10), default 'en'
   - target_language: String(10), default 'es'
   - Automated scores (Float, nullable):
     - automated_coherence
     - automated_fidelity
     - automated_naturalness
     - automated_overall
   - s3_insights_path: String(500), nullable
   - s3_automated_qa_path: String(500), nullable
   - created_at: DateTime with timezone
   - Relationships:
     - many-to-one with prompt
     - one-to-many with manual_scores

4. **ManualScore Model** (`manual_scores` table):
   - id: Integer, primary key
   - translation_id: Integer, foreign key to translations
   - user_id: Integer, foreign key to users
   - coherence: Float (0-10)
   - fidelity: Float (0-10)
   - naturalness: Float (0-10)
   - overall: Float (0-10)
   - notes: Text, nullable
   - created_at: DateTime with timezone
   - updated_at: DateTime with timezone
   - Unique constraint: (translation_id, user_id) - one score per user per translation
   - Relationships:
     - many-to-one with translation
     - many-to-one with user

**Configuration:**

- Database connection from environment variable `DATABASE_URL`
- Connection pooling with proper settings
- UTC timezone for all timestamps
- Proper indexes for performance

### Tasks

Please create:

1. **`backend/app/config.py`**:
   - Load environment variables (DATABASE_URL, SECRET_KEY, etc.)
   - Configuration class with proper defaults
   - Support for both MinIO and AWS S3

2. **`backend/app/database.py`**:
   - SQLAlchemy engine setup with connection pooling
   - SessionLocal factory
   - Base declarative class
   - Dependency for getting database sessions

3. **`backend/app/models.py`**:
   - All 4 models with proper relationships
   - Indexes on frequently queried fields
   - Timestamps with UTC timezone
   - Proper constraints

4. **`backend/app/schemas.py`**:
   - Pydantic schemas for request/response validation
   - UserCreate, UserResponse, UserLogin
   - PromptCreate, PromptResponse
   - TranslationCreate, TranslationResponse, TranslationDetail
   - ManualScoreCreate, ManualScoreUpdate, ManualScoreResponse
   - Token schema for JWT

5. **`backend/app/init_db.py`**:
   - Function to create all tables
   - Function to create default admin user (username: admin, password: admin123)
   - Function to seed initial data if needed

### Expected Output

When the backend starts, it should:
- Create all database tables automatically
- Create a default admin user on first run
- Log "Default admin user created" message
