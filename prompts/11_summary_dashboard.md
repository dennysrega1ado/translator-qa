# Step 11: Summary Dashboard

## Prompt

Create a comprehensive summary dashboard with statistics, charts, and export functionality.

### Context

Users need to see aggregated quality metrics and review progress. Admins need to see contributor statistics and overall quality trends.

### Requirements

**Dashboard Components:**

1. **Statistics Cards** (top row):
   - Total Translations: Count of all translations
   - Reviewed: Count of translations with manual scores
   - Coverage: Percentage of translations reviewed
   - Cards with large numbers and icons

2. **Quality Score Chart** (left column):
   - Doughnut chart showing overall quality score
   - Color-coded segments (red <6, yellow 6-8, green >8)
   - Center text showing average score
   - Legend below chart
   - Uses Chart.js

3. **Contributors Panel** (right column):
   - List of users who have submitted reviews
   - Show username and review count
   - Show percentage of total reviews
   - Avatar or icon per user
   - Sorted by review count (descending)

4. **Average Manual Scores** (bottom section):
   - Grid of score cards:
     - Coherence average
     - Fidelity average
     - Naturalness average
     - Overall average
   - Large number display with metric name
   - Color-coded based on score

5. **Export Button** (top-right):
   - "Export My Reviews (Excel)" button with download icon
   - Downloads Excel file with user's reviews
   - Includes all review details and timestamps

**Data Flow:**
- Load summary data from `/api/reports/summary` endpoint
- Load contributors from `/api/reports/` endpoint
- Refresh data when view is shown
- Show loading state while fetching

**Chart Configuration:**
- Doughnut chart with cutout for "donut" effect
- Responsive sizing
- Tooltips on hover
- Smooth animations

### Tasks

Please create/update:

1. **Update `frontend/index.html`**:
   - Add Summary view HTML structure:
     - Statistics cards grid
     - Two-column layout for chart and contributors
     - Average scores grid
     - Export button in header
   - Include canvas element for Chart.js

2. **Update `frontend/app.js`**:
   - `loadSummary()`: Fetch summary data from API
   - `displaySummaryStats()`: Update statistics cards
   - `createQualityChart()`: Create Chart.js doughnut chart
   - `displayContributors()`: Render contributors list
   - `displayAverageScores()`: Update score cards
   - `exportReviews()`: Trigger Excel export download
   - Helper functions:
     - `calculateCoverage()`: Percentage of reviews
     - `getScoreColor()`: Color based on score value
     - `formatNumber()`: Format numbers with decimals

3. **Update `frontend/styles.css`**:
   - Summary view styles:
     - Stat card styles with icons
     - Chart container with proper sizing
     - Contributors list with user items
     - Average scores grid
     - Export button prominent styling
   - Color scheme for score ranges:
     - Red: 0-6 (poor)
     - Yellow: 6-8 (good)
     - Green: 8-10 (excellent)

4. **Chart.js Integration**:
   - Initialize chart with proper configuration
   - Update chart when data changes
   - Destroy and recreate on data refresh
   - Responsive options

### Expected Output

After implementation:
- Summary view shows:
  - Total translations count
  - Number reviewed by user
  - Coverage percentage (e.g., "45% reviewed")
- Quality chart displays overall score visually
- Contributors list shows who has reviewed and how many
- Average manual scores displayed in grid
- Export button downloads Excel file with user's reviews
- All numbers update dynamically from API
- Professional, dashboard-style layout
- Charts are responsive and animated
- Colors indicate quality levels (red/yellow/green)
