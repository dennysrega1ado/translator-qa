# Step 13: Reports View (Admin)

## Prompt

Create an admin-only reports view showing detailed quality analytics with filters.

### Context

Admins need to see comprehensive quality reports across all users and executions. This provides insights into translation quality trends and review progress.

### Requirements

**Reports View Components:**

1. **Filter Controls** (top):
   - Execution dropdown (filter by batch)
   - Prompt dropdown (filter by prompt type)
   - "Show only manual scores" checkbox
   - "Apply" button to apply filters
   - "Clear Filters" button

2. **Summary Statistics** (top cards):
   - Total translations
   - Translations with manual scores
   - Coverage percentage
   - Average overall score (automated + manual combined)

3. **Score Breakdown Tables**:
   - Automated Scores table:
     - Coherence average
     - Fidelity average
     - Naturalness average
     - Overall average
   - Manual Scores table (if any exist):
     - Coherence average
     - Fidelity average
     - Naturalness average
     - Overall average
   - Combined Averages table:
     - Average of automated + manual for each metric

4. **Contributors Section**:
   - List of users with manual scores
   - Review count per user
   - Percentage of total reviews
   - Most active reviewer highlighted

5. **Translations List** (filtered):
   - Paginated list of translations matching filters
   - Show translation ID, original/translated preview
   - Show scores (automated and manual if exists)
   - Click to view details

**Filtering Logic:**
- Filter by execution: only translations from that batch
- Filter by prompt: only translations using that prompt
- Manual only: only show translations with at least one manual score
- Filters combine (AND logic)
- Counts and averages update based on filters

**Data Visualization:**
- Score ranges color-coded (red/yellow/green)
- Progress bars for coverage
- Highlight outliers (very low or very high scores)

### Tasks

Please create/update:

1. **Update `frontend/index.html`**:
   - Add Reports view HTML structure:
     - Filter controls section
     - Summary statistics cards
     - Score breakdown tables (automated, manual, combined)
     - Contributors section
     - Translations list with pagination

2. **Update `frontend/app.js`**:
   - Reports view functions:
     - `loadReports()`: Fetch reports data from API
     - `applyReportFilters()`: Apply filters and reload data
     - `displayReportStats()`: Update summary statistics
     - `displayScoreTables()`: Render score breakdown tables
     - `displayReportContributors()`: Show contributors with counts
     - `displayFilteredTranslations()`: Show translations list
   - Filter management:
     - Track selected filters in state
     - Build query parameters for API
     - Clear filters function
   - Populate dropdowns:
     - Load execution list from API
     - Load prompt list from API
   - Color coding:
     - Apply colors based on score values
     - Highlight best/worst performers

3. **Update `frontend/styles.css`**:
   - Reports view styles:
     - Filter controls layout
     - Summary cards styling
     - Tables with proper spacing and borders
     - Score cells with color backgrounds
     - Contributors list styling
     - Translations list with hover effects
   - Color scheme for scores (red/yellow/green)
   - Professional data table design

4. **Populate filter dropdowns**:
   - Fetch execution list on view load
   - Fetch prompt list on view load
   - Dynamic dropdown population
   - "All" option as default

### Expected Output

After implementation:
- Reports view accessible only to admins
- Default view shows all translations and statistics
- Can filter by execution, prompt, or manual-only
- Applying filters updates:
  - Summary statistics
  - Score averages
  - Contributors list
  - Translations shown
- Score tables show automated vs manual vs combined averages
- Colors indicate score quality (red=poor, yellow=good, green=excellent)
- Contributors section shows who is most active
- Translations list shows preview of filtered results
- Professional analytics dashboard appearance
- Clear data visualization with proper formatting
