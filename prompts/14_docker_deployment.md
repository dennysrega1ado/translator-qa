# Step 14: Docker Deployment & Configuration

## Prompt

Finalize the Docker configuration for development and production deployment.

### Context

We have a complete application. Now we need to ensure proper Docker configuration for both local development and production deployment.

### Requirements

**Docker Compose Configuration:**

1. **PostgreSQL Service**:
   - Image: postgres:15-alpine
   - Environment variables for database, user, password
   - Volume for data persistence
   - Health check using pg_isready
   - Port 5432 exposed

2. **MinIO Service** (local development):
   - Image: minio/minio:latest
   - Command: server /data --console-address ":9001"
   - Environment variables for access/secret keys
   - Volume for data persistence
   - Ports 9000 (API) and 9001 (Console)
   - Health check

3. **Backend Service**:
   - Build from ./backend/Dockerfile
   - Environment variables:
     - DATABASE_URL
     - MINIO or S3 settings
     - SECRET_KEY
     - ALGORITHM
     - ACCESS_TOKEN_EXPIRE_MINUTES
   - Port 8000 exposed
   - Depends on postgres and minio (with health checks)
   - Volume mount for hot-reload in development
   - Restart policy: unless-stopped (production)

4. **Frontend Service**:
   - Build from ./frontend/Dockerfile
   - Port 80 or 3000 exposed
   - Depends on backend
   - Volume mount for hot-reload in development
   - Nginx configuration for API proxy

**Backend Dockerfile:**
- Multi-stage build for production
- Python 3.11-slim base
- Non-root user (appuser)
- Install dependencies
- Copy application code
- Expose port 8000
- Health check endpoint
- CMD: uvicorn with proper workers

**Frontend Dockerfile:**
- Nginx alpine base
- Copy nginx.conf
- Copy static files (HTML, CSS, JS)
- Expose port 80
- Health check

**Nginx Configuration:**
- Serve static files from /usr/share/nginx/html
- Proxy /api requests to backend:8000
- SPA routing (all routes serve index.html)
- CORS headers
- Gzip compression
- Security headers

**Environment Configuration:**
- Create .env.example file with all required variables
- Document each variable
- Provide sensible defaults
- Production-specific settings commented

### Tasks

Please create/update:

1. **Update `docker-compose.yml`**:
   - All four services properly configured
   - Health checks for postgres and minio
   - Service dependencies (depends_on with condition)
   - Volume definitions for persistence
   - Network configuration (optional explicit network)
   - Environment variable support (.env file)
   - Development and production profiles (optional)

2. **Update `backend/Dockerfile`**:
   - Use Python 3.11-slim
   - Create non-root user
   - Install system dependencies if needed
   - Copy requirements.txt and install
   - Copy application code with proper permissions
   - Set working directory
   - Expose port 8000
   - Health check using curl or python
   - CMD for production: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

3. **Update `frontend/Dockerfile`**:
   - Use nginx:alpine
   - Copy nginx.conf to /etc/nginx/conf.d/default.conf
   - Copy static files to /usr/share/nginx/html
   - Expose port 80
   - No additional configuration needed (nginx handles everything)

4. **Update `frontend/nginx.conf`**:
   - Server block listening on port 80
   - Root directory /usr/share/nginx/html
   - Location / serves static files, try_files with index.html fallback
   - Location /api proxy to http://backend:8000
   - Proxy headers (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
   - Gzip compression enabled
   - Client max body size (for file uploads)

5. **Create `.env.example`**:
   - Document all environment variables:
     - DATABASE_URL
     - MINIO_ENDPOINT / AWS_S3_BUCKET
     - STORAGE_BACKEND (s3 or minio)
     - SECRET_KEY
     - ALGORITHM
     - ACCESS_TOKEN_EXPIRE_MINUTES
   - Provide example values
   - Add comments explaining each variable

6. **Create sample data script** `backend/load_sample_data.py`:
   - Create sample prompts
   - Create sample translations with automated scores
   - Use for testing/demo purposes
   - Can be run with: docker-compose exec backend python load_sample_data.py

### Expected Output

After implementation:
- Can start entire stack with: `docker-compose up`
- All services start in correct order (wait for health checks)
- Database automatically creates tables on first run
- Default admin user created automatically
- Can access:
  - Frontend: http://localhost:3000
  - Backend API: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - MinIO Console: http://localhost:9001
- Can load sample data for testing
- Data persists between restarts (volumes)
- Hot-reload works in development (volume mounts)
- Production-ready with proper:
  - Health checks
  - Restart policies
  - Resource limits (optional)
  - Security settings
- Clean logs showing startup progress
- No errors in docker-compose logs
