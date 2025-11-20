# Step 6: Reports & Summary API

## Prompt

Create the reporting API that aggregates translation quality data for summary dashboards.

### Context

Users can now view translations and submit scores. We need reporting endpoints that aggregate this data for analytics and summary views.

### Requirements

**API Endpoints:**

1. `GET /api/reports/` - Get aggregated quality reports
   - Query parameters:
     - `execution_id`: Filter by execution (optional)
     - `prompt_id`: Filter by prompt (optional)
     - `manual_only`: Boolean, if true show only manually scored translations (optional)
   - Return aggregated statistics:
     - Total translations count
     - Number of translations with manual scores
     - Percentage of manual scores
     - Average automated scores (coherence, fidelity, naturalness, overall)
     - Average manual scores (coherence, fidelity, naturalness, overall)
     - Combined averages
     - List of contributors with their review counts
   - Protected route

2. `GET /api/reports/summary` - Get summary for current user
   - Return statistics specific to current user:
     - Total translations available
     - Number reviewed by current user
     - Coverage percentage
     - User's average manual scores
     - Breakdown by execution
   - Protected route

3. `GET /api/reports/export` - Export user's reviews to Excel
   - Generate Excel file with user's manual scores
   - Include columns: Translation ID, Original Text, Translated Text, Coherence, Fidelity, Naturalness, Overall, Notes, Timestamp
   - Return downloadable file
   - Protected route

**Aggregation Logic:**

For averages:
- Calculate mean of all automated scores
- Calculate mean of all manual scores
- Calculate combined average (automated + manual) / 2
- Group by execution_id for execution-level stats
- Count distinct users who submitted scores (contributors)

For contributors:
- List users who have submitted manual scores
- Count number of reviews per user
- Calculate percentage of total they've reviewed

### Tasks

Please create:

1. **`backend/app/routers/reports.py`**:
   - Implement all 3 endpoints
   - Use SQL aggregation functions (AVG, COUNT, etc.)
   - Proper joins between translations, manual_scores, and users
   - Filter by execution/prompt if provided
   - For manual_only: only include translations with at least one manual score
   - Contributors query: group by user_id, count scores

2. **Add Excel export functionality**:
   - Install `openpyxl` or `xlsxwriter` package
   - Generate Excel file in memory
   - Include proper headers and formatting
   - Filter to current user's scores only
   - Return as downloadable file with proper headers

3. **Update `backend/app/main.py`**:
   - Include reports router with prefix `/api`

4. **Optimize queries**:
   - Use subqueries for complex aggregations
   - Add indexes if needed for performance

### Expected Output

After implementation:
- Can get overall reports: `GET /api/reports/`
- Can filter reports: `GET /api/reports/?execution_id=batch-001&manual_only=true`
- Can get user summary: `GET /api/reports/summary`
- Can export to Excel: `GET /api/reports/export` returns downloadable file
- Statistics are accurate with proper averaging
- Contributors list shows who has reviewed and how many
