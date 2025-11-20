# Translation QA System

A full-stack application for managing and evaluating translation quality assessments.

![image](img/output_1.5x.gif)

## Features

- **Authentication System**: Secure login with JWT tokens
- **User Management**: Admin users can create evaluator users
- **Translation Viewing**: Browse translations with original and translated content
- **Manual Scoring**: Evaluate translations on coherence, fidelity, naturalness, and overall quality
- **Score Editing**: Users can edit their previous scores
- **Automated Scores**: Integration with automated QA scores from S3/MinIO
- **Comprehensive Reports**: View aggregated statistics by execution and prompt
- **S3 Storage**: MinIO for local S3-compatible storage
- **Docker Compose**: Fully containerized application

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- Uvicorn (ASGI server)
- SQLAlchemy (ORM)
- PostgreSQL
- MinIO (S3-compatible storage)
- JWT Authentication

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Nginx

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 15
- MinIO

## Project Structure

```
translator-qa/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── s3_service.py
│   │   ├── init_db.py
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── translations.py
│   │       ├── scores.py
│   │       ├── reports.py
│   │       └── prompts.py
│   ├── sample_data/
│   │   ├── en/
│   │   │   └── insights.json
│   │   └── es/
│   │       ├── insights.json
│   │       └── automated_qa.json
│   └── load_sample_data.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── index.html
    ├── styles.css
    └── app.js
```

## Database Schema

### Tables

1. **users**: User authentication and management
   - id, username, email, hashed_password, is_admin, is_active, created_at, updated_at

2. **prompts**: Translation prompts
   - id, prompt_id, name, description, created_at

3. **translations**: Translation records with automated scores
   - id, execution_id, prompt_id, original_content, translated_content
   - source_language, target_language
   - automated_coherence, automated_fidelity, automated_naturalness, automated_overall
   - s3_insights_path, s3_automated_qa_path, created_at

4. **manual_scores**: User evaluations of translations
   - id, translation_id, user_id
   - coherence, fidelity, naturalness, overall
   - notes, created_at, updated_at

## Setup and Installation

### Prerequisites

- Docker
- Docker Compose
- Git

### Quick Start

1. **Clone the repository**
```bash
cd ~/repo/ai/translator-qa
```

2. **Start the application**
```bash
docker compose up
```

This will start:
- PostgreSQL on port 5432
- MinIO on ports 9000 (API) and 9001 (Console)
- Backend API on port 8000
- Frontend on port 3000

3. **Wait for services to be ready**
```bash
docker-compose logs -f backend
```

Wait until you see "Default admin user created" message.

4. **Load sample data**
```bash
docker compose exec backend python load_sample_data.py
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### Default Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`

**MinIO:**
- Username: `minioadmin`
- Password: `minioadmin123`

## Usage

### Login
1. Navigate to http://localhost:3000
2. Login with admin credentials

### Create Users (Admin Only)
1. Click on "Admin" in the navigation
2. Fill in the user creation form
3. Check "Admin User" if the user should have admin privileges
4. Click "Create User"

### View Translations
1. Click on "Translations" in the navigation
2. Use filters to narrow down by execution or prompt
3. Click on a translation card to view details

### Score Translations
1. Click on a translation card
2. In the modal, scroll to "Add Your Score" section
3. Enter scores for coherence, fidelity, naturalness, and overall (0-10 scale)
4. Optionally add notes
5. Click "Submit Score"

### Edit Scores
1. Click on a translation you've already scored
2. Modify the scores in the "Edit Your Score" section
3. Click "Update Score"

### View Reports
1. Click on "Reports" in the navigation
2. Use filters to narrow down by execution or prompt
3. Toggle "Show only manual scores" to see only manually evaluated translations
4. View aggregated statistics including:
   - Total translations
   - Number and percentage of manual scores
   - Average automated scores
   - Average manual scores
   - Combined averages

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Create new user (admin only)
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/users` - List all users (admin only)

### Translations
- `GET /api/translations/` - List translations (with filters)
- `GET /api/translations/{id}` - Get translation details
- `GET /api/translations/executions/list` - List all executions
- `POST /api/translations/` - Create translation

### Scores
- `POST /api/scores/` - Create manual score
- `PUT /api/scores/{id}` - Update manual score
- `GET /api/scores/{id}` - Get manual score
- `DELETE /api/scores/{id}` - Delete manual score

### Reports
- `GET /api/reports/` - Get aggregated reports

### Prompts
- `GET /api/prompts/` - List prompts
- `GET /api/prompts/{id}` - Get prompt details
- `POST /api/prompts/` - Create prompt (admin only)

## Development

### Backend Development

The backend is configured with hot-reload enabled. Any changes to Python files will automatically restart the server.

```bash
# View backend logs
docker-compose logs -f backend

# Access backend container
docker-compose exec backend bash

# Run migrations (if needed)
docker-compose exec backend alembic upgrade head
```

### Frontend Development

Frontend files are mounted as volumes. Refresh the browser to see changes.

```bash
# Access frontend container
docker-compose exec frontend sh
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U translator_user -d translator_qa

# Common queries
SELECT * FROM users;
SELECT * FROM prompts;
SELECT * FROM translations;
SELECT * FROM manual_scores;
```

### MinIO Management

1. Access MinIO Console at http://localhost:9001
2. Login with minioadmin/minioadmin123
3. Browse the "translations" bucket
4. View uploaded JSON files

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This deletes all data)
docker-compose down -v
```

## Production Deployment

For production deployment:

1. **Change default passwords** in docker-compose.yml
2. **Update SECRET_KEY** in backend environment
3. **Configure CORS** in backend/app/main.py
4. **Use HTTPS** with proper SSL certificates
5. **Set up backup** for PostgreSQL and MinIO
6. **Configure proper nginx** with rate limiting
7. **Enable logging** and monitoring

## Troubleshooting

### Backend not starting
```bash
docker-compose logs backend
```

### Database connection issues
```bash
docker-compose restart postgres
docker-compose restart backend
```

### MinIO access issues
```bash
docker-compose restart minio
docker-compose exec backend python -c "from app.s3_service import s3_service; print(s3_service.list_objects())"
```

### Frontend not loading
```bash
docker-compose logs frontend
docker-compose restart frontend
```

## License

MIT

## Support

For issues and questions, please open an issue on the project repository.
