# Step 4: Translations API

## Prompt

Build the translations management API that allows viewing and filtering translations.

### Context

We have authentication working. Now we need to create the core API for managing translations - viewing, filtering, and retrieving translation data.

### Requirements

**API Endpoints:**

1. `GET /api/translations/` - List translations with filters and pagination
   - Query parameters:
     - `execution_id`: Filter by execution batch (optional)
     - `prompt_id`: Filter by prompt (optional)
     - `reviewed`: Filter by review status (optional, boolean)
       - If true: only show translations the current user has scored
       - If false: only show translations the current user hasn't scored
     - `skip`: Pagination offset (default 0)
     - `limit`: Page size (default 100)
   - Returns: List of translations with automated scores and review status
   - Protected route (requires authentication)

2. `GET /api/translations/{id}` - Get single translation details
   - Returns: Full translation with automated scores and user's manual score (if exists)
   - Protected route

3. `GET /api/translations/executions/list` - List all unique execution IDs
   - Returns: List of unique execution_id and execution_description pairs
   - Used for dropdown filter
   - Protected route

4. `POST /api/translations/` - Create new translation
   - Admin only
   - Accept translation data
   - Return created translation

**Response Format:**

Translation list response should include:
- Translation ID
- Original content
- Translated content
- Source and target languages
- Automated scores (coherence, fidelity, naturalness, overall)
- Whether current user has reviewed it (boolean)
- Prompt information

Translation detail response should additionally include:
- User's manual score (if exists)
- S3 paths for reference

### Tasks

Please create:

1. **`backend/app/routers/translations.py`**:
   - Implement all 4 endpoints
   - Use proper SQLAlchemy queries with joins
   - Implement filtering logic:
     - For `reviewed=true`: join with manual_scores where user_id = current_user
     - For `reviewed=false`: left join and filter where manual_score is null
   - Include pagination with skip/limit
   - Return proper error messages (404 for not found, etc.)
   - All routes require authentication

2. **Update `backend/app/main.py`**:
   - Include translations router with prefix `/api`

3. **Optimize queries**:
   - Use eager loading for relationships (joinedload)
   - Add indexes on execution_id for performance
   - Efficient counting for pagination

### Expected Output

After implementation:
- Can list all translations: `GET /api/translations/`
- Can filter by execution: `GET /api/translations/?execution_id=batch-001`
- Can filter unreviewed: `GET /api/translations/?reviewed=false`
- Can get translation details: `GET /api/translations/1`
- Can get execution list for dropdown: `GET /api/translations/executions/list`
- All endpoints properly authenticated
