# Step 8: Prompts Management API

## Prompt

Create a simple API for managing translation prompts.

### Context

Prompts represent different translation instructions or configurations used to generate translations. We need basic CRUD operations for prompts.

### Requirements

**API Endpoints:**

1. `GET /api/prompts/` - List all prompts
   - Return list of all prompts with count of associated translations
   - Protected route

2. `GET /api/prompts/{id}` - Get single prompt details
   - Return prompt with associated translations
   - Protected route

3. `POST /api/prompts/` - Create new prompt
   - Admin only
   - Accept PromptCreate schema
   - Validate prompt_id uniqueness
   - Return created prompt

4. `PUT /api/prompts/{id}` - Update prompt
   - Admin only
   - Update name or description
   - Return updated prompt

5. `DELETE /api/prompts/{id}` - Delete prompt
   - Admin only
   - Check for associated translations (prevent delete if translations exist)
   - Return success message

**Validation:**
- prompt_id must be unique
- Cannot delete prompt with associated translations
- Only admins can create/update/delete

### Tasks

Please create:

1. **`backend/app/routers/prompts.py`**:
   - Implement all 5 endpoints
   - Validation logic for uniqueness
   - Check for associated translations before delete
   - Proper error handling (404, 400, 403)
   - All routes protected (create/update/delete admin-only)

2. **Update `backend/app/main.py`**:
   - Include prompts router with prefix `/api`

### Expected Output

After implementation:
- Can list prompts: `GET /api/prompts/`
- Can create prompt: `POST /api/prompts/` (admin only)
- Can update prompt: `PUT /api/prompts/1` (admin only)
- Cannot delete prompt with translations (400 error)
- Proper error messages and validation
