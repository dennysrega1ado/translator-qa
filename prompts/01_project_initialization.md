# Step 1: Project Initialization & Architecture Design

## Prompt

I need to build a **Translation QA System** - a full-stack web application for managing and evaluating translation quality assessments. This system will allow users to review AI-generated translations and provide manual quality scores.

### Requirements

**Core Functionality:**
- User authentication (admin and evaluator roles)
- View translations with original and translated text side-by-side
- Manual scoring system for translation quality (coherence, fidelity, naturalness, overall)
- Automated scores from AI evaluation (already generated, stored in S3)
- Summary dashboard with statistics and charts
- Admin panel to load translations from S3 and manage users
- Filter translations by execution batch and review status
- Pagination for efficient navigation

**Technical Stack:**
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (no frameworks), Nginx
- **Storage**: S3-compatible storage (MinIO for local dev, AWS S3 for production)
- **Authentication**: JWT tokens
- **Deployment**: Docker Compose

**Architecture:**
- 3 main containers: Frontend (Nginx), Backend (FastAPI), Database (PostgreSQL)
- Optional 4th container: MinIO (for local S3 simulation)
- RESTful API design
- Responsive, modern UI

**Database Schema (4 tables):**
1. `users`: id, username, email, hashed_password, is_admin, is_active, timestamps
2. `prompts`: id, prompt_id, name, description, created_at
3. `translations`: id, execution_id, prompt_id, original_content, translated_content, source_language, target_language, automated scores (coherence, fidelity, naturalness, overall), s3_paths, created_at
4. `manual_scores`: id, translation_id, user_id, manual scores (coherence, fidelity, naturalness, overall), notes, timestamps

**Data Flow:**
1. Admin loads translations from S3 (JSON files with English originals and Spanish translations)
2. S3 structure: `prefix/en/insights.json` and `prefix/es/insights.json` + `prefix/es/automated_qa.json`
3. System matches translations by ID and stores in PostgreSQL
4. Users review translations and submit manual scores
5. Summary view aggregates both automated and manual scores

### Tasks

Please create:

1. **Project structure** with proper directories:
   ```
   translator-qa/
   ├── docker-compose.yml
   ├── backend/
   │   ├── Dockerfile
   │   ├── requirements.txt
   │   └── app/
   │       ├── __init__.py
   │       ├── main.py
   │       ├── config.py
   │       ├── database.py
   │       ├── models.py
   │       ├── schemas.py
   │       ├── auth.py
   │       └── routers/
   └── frontend/
       ├── Dockerfile
       ├── nginx.conf
       ├── index.html
       ├── styles.css
       └── app.js
   ```

2. **Backend Dockerfile** with:
   - Python 3.11-slim base image
   - Non-root user (appuser)
   - Proper dependency installation
   - Working directory setup

3. **Frontend Dockerfile** with:
   - Nginx alpine base image
   - Proper static file serving
   - Configuration for API proxy

4. **docker-compose.yml** with:
   - PostgreSQL service with health checks
   - MinIO service for local S3
   - Backend service depending on database
   - Frontend service
   - Proper networking and volumes

5. **backend/requirements.txt** with essential packages

6. **Basic project README** with setup instructions

### Expected Output

A working project skeleton that can start with `docker-compose up` and shows a basic "API is running" message when accessing the backend.
