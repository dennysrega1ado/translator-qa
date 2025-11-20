# Step 5: Manual Scores API

## Prompt

Implement the manual scoring system that allows users to submit and edit their quality assessments of translations.

### Context

Users can now view translations. We need to build the API for submitting manual quality scores.

### Requirements

**API Endpoints:**

1. `POST /api/scores/` - Create a manual score
   - Request body: ManualScoreCreate schema
     - translation_id: Integer (required)
     - coherence: Float 0-10 (required)
     - fidelity: Float 0-10 (required)
     - naturalness: Float 0-10 (required)
     - overall: Float 0-10 (required)
     - notes: String (optional)
   - Automatically set user_id from current authenticated user
   - Validate that translation exists
   - Check for duplicate score (one per user per translation)
   - Return created score
   - Protected route

2. `PUT /api/scores/{id}` - Update existing manual score
   - Can only update own scores
   - Request body: ManualScoreUpdate schema (same fields as create)
   - Update timestamps
   - Return updated score
   - Protected route

3. `GET /api/scores/{id}` - Get a specific manual score
   - Return score details
   - Protected route

4. `DELETE /api/scores/{id}` - Delete a manual score
   - Can only delete own scores (unless admin)
   - Protected route

**Validation:**
- Score values must be between 0 and 10
- Translation must exist
- User cannot submit duplicate scores for same translation
- User can only edit/delete their own scores (unless admin)

**Business Logic:**
- When creating score: set created_at and updated_at
- When updating score: update updated_at only
- Calculate average scores for summary views

### Tasks

Please create:

1. **`backend/app/routers/scores.py`**:
   - Implement all 4 endpoints
   - Validation logic:
     - Check score values are in range [0, 10]
     - Verify translation exists
     - Check for duplicate scores on create
     - Verify ownership on update/delete
   - Error handling:
     - 404 if translation not found
     - 400 if duplicate score
     - 403 if trying to modify someone else's score
   - Use proper SQL queries with error handling

2. **Update `backend/app/schemas.py`**:
   - Add validation for score ranges (0-10) using Pydantic validators
   - Optional notes field with max length

3. **Update `backend/app/main.py`**:
   - Include scores router with prefix `/api`

### Expected Output

After implementation:
- User can submit score: `POST /api/scores/` with translation_id and scores
- User can update their score: `PUT /api/scores/123`
- User cannot submit duplicate scores (400 error)
- User can only edit their own scores (403 if trying to edit others)
- Admins can delete any score
- Score values validated to be 0-10 range
