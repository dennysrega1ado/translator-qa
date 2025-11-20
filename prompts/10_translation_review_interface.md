# Step 10: Translation Review Interface

## Prompt

Build the core translation review interface with filters, pagination, and scoring functionality.

### Context

Users need to review translations side-by-side and submit quality scores. This is the main feature of the application.

### Requirements

**UI Components:**

1. **Filter Section** (always visible at top):
   - Execution dropdown filter (populated from API)
   - Status filter buttons: All | Unreviewed | Reviewed
   - Search by translation ID input
   - Pagination info and controls (Previous/Next buttons)

2. **Metrics Dashboard**:
   - Overall LLM Score card (prominent, top-right)
   - Individual metric cards showing automated scores:
     - Coherence
     - Fidelity
     - Naturalness
   - Color-coded based on score ranges

3. **Side-by-Side Translation Display**:
   - Left panel: Original text (English) with gray header
   - Right panel: Translated text (Spanish) with blue header
   - Large, readable text
   - Responsive layout (stacks on mobile)

4. **Comments Section**:
   - Textarea for optional notes
   - Placeholder text
   - Character counter (optional)

5. **Submit Button**:
   - Large, prominent button
   - Success animation on submit
   - Auto-advance to next unreviewed translation

6. **Empty State**:
   - Shown when no translations available
   - Icon and message
   - Helpful text

7. **All Done Modal**:
   - Celebration animation (🎉)
   - "All Done!" message
   - Button to continue (switches to "All" filter)

**User Flow:**

1. User logs in
2. Selects execution from dropdown
3. Clicks "Unreviewed" filter to see pending work
4. Reviews translation side-by-side
5. Reads automated scores for reference
6. Adds optional comments
7. Clicks Submit Review
8. Sees success animation
9. Automatically advances to next unreviewed translation
10. When all done, sees celebration modal

**Pagination:**
- Use API parameters: skip and limit
- Track current page in state
- Update pagination info "X of Y"
- Disable Previous/Next buttons at boundaries
- Maintain filter state during pagination

### Tasks

Please create/update:

1. **Update `frontend/index.html`**:
   - Add Translations view HTML structure:
     - Filters section
     - Metrics dashboard
     - Side-by-side translation panels
     - Comments textarea
     - Submit button
     - Empty state
   - Add success overlay with checkmark animation
   - Add "All Done" celebration modal

2. **Create `frontend/app_pagination.js`**:
   - Pagination state management
   - `loadTranslationsPaginated()`: Fetch translations with pagination
   - `navigateTranslation(direction)`: Move to prev/next translation
   - `searchTranslationById()`: Jump to specific translation
   - `updatePaginationUI()`: Update buttons and info
   - `handleExecutionFilterChange()`: Reload when execution changes
   - Maintain filter state (execution, status) during navigation

3. **Update `frontend/app.js`**:
   - Add translations view functions:
     - `loadTranslations()`: Fetch and display translations
     - `displayTranslation(translation)`: Render translation in UI
     - `submitReview()`: Submit manual score to API
     - `showSuccessAnimation()`: Show checkmark animation
     - `checkIfAllDone()`: Show celebration modal if no more unreviewed
   - Filter management:
     - Handle filter button clicks
     - Apply filters to API requests
   - Execution filter:
     - Load execution list on view load
     - Populate dropdown
     - Apply filter on change

4. **Update `frontend/styles.css`**:
   - Translation review styles:
     - Filter buttons with active state
     - Side-by-side panels with proper spacing
     - Metric cards with hover effects
     - Success animation keyframes
     - Modal styles for celebration
   - Responsive design for mobile
   - Professional color scheme

### Expected Output

After implementation:
- User can select execution from dropdown
- Clicking "Unreviewed" shows only translations user hasn't scored
- Clicking "Reviewed" shows only translations user has scored
- Can navigate with Previous/Next buttons
- Can search by translation ID
- Side-by-side display is clear and readable
- Automated scores are visible for reference
- Can add comments (optional)
- Clicking Submit Review:
  - Shows success animation
  - Advances to next unreviewed translation
  - Updates the translation count
- When all pending reviews are done:
  - Shows "All Done!" celebration modal
  - Clicking "Continue Reviewing" switches to "All" filter
- Responsive on mobile devices
