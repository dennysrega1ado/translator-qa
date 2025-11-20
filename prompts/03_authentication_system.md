# Step 3: Authentication System

## Prompt

Implement the JWT-based authentication system for the Translation QA application.

### Context

We have the database models ready. Now we need to build a secure authentication system with JWT tokens that supports both admin and regular users.

### Requirements

**Authentication Features:**
- User login with username/password
- JWT token generation and validation
- Password hashing with bcrypt
- Token-based authorization
- Role-based access control (admin vs regular user)
- Protected routes requiring authentication
- Get current user endpoint

**Security:**
- Passwords stored as bcrypt hashes
- JWT tokens with expiration (30 minutes default)
- HS256 algorithm for token signing
- Secure token validation on protected routes

**API Endpoints:**
- `POST /api/auth/login` - User login (returns access token)
- `GET /api/auth/me` - Get current user info (protected)
- `POST /api/auth/register` - Register new user (admin only)
- `GET /api/auth/users` - List all users (admin only)

### Tasks

Please create:

1. **`backend/app/auth.py`**:
   - Password hashing functions (hash_password, verify_password) using bcrypt
   - JWT token creation function (create_access_token)
   - JWT token verification function (verify_token)
   - Dependency for getting current user from token (get_current_user)
   - Dependency for requiring admin user (require_admin)
   - Token model with username and expiration

2. **`backend/app/routers/auth.py`**:
   - `POST /api/auth/login`:
     - Accept username and password as form data (OAuth2PasswordRequestForm)
     - Validate credentials
     - Return access token with token_type "bearer"
   - `GET /api/auth/me`:
     - Protected route (requires valid token)
     - Return current user info (username, email, is_admin)
   - `POST /api/auth/register`:
     - Admin only route
     - Accept UserCreate schema
     - Hash password
     - Create new user
     - Return created user info
   - `GET /api/auth/users`:
     - Admin only route
     - Return list of all users (without passwords)

3. **Update `backend/app/main.py`**:
   - Include auth router
   - Call init_database() on startup
   - Add CORS middleware for frontend access

### Environment Variables

Ensure these are configurable:
- `SECRET_KEY` - for JWT signing (generate secure random string)
- `ALGORITHM` - default "HS256"
- `ACCESS_TOKEN_EXPIRE_MINUTES` - default 30

### Expected Output

After implementation:
- Can login with admin/admin123 and receive JWT token
- Can access `/api/auth/me` with valid token
- Can create new users if admin
- Invalid tokens are rejected with 401
- Frontend can store token in localStorage and use for API calls
