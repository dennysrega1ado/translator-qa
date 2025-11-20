# Step 12: Admin Panel

## Prompt

Build the admin panel for user management and S3 data loading.

### Context

Admins need to create users, load translations from S3, and manage the database. This is a restricted area only accessible to admin users.

### Requirements

**Admin Panel Sections:**

1. **Create New User**:
   - Form with fields:
     - Username (required)
     - Email (required)
     - Password (required)
     - Is Admin checkbox
   - Submit button
   - Success/error message display
   - Form clears after successful creation

2. **Users List**:
   - Table or list showing all users:
     - Username
     - Email
     - Role (Admin/User)
     - Status (Active/Inactive)
     - Created date
   - Refresh button
   - (Optional) Delete user button

3. **Load Translations from S3**:
   - S3 Bucket display (read-only, from config)
   - S3 Prefix input with example
   - Description input (required) - human-readable name for this batch
   - Validation workflow:
     - Step 1: Click "Validate Prefix" button
     - System checks if prefix has en/, es/ folders and required files
     - Shows validation result (success/error with details)
     - Step 2: If valid, "Load Translations" button becomes enabled
     - Click to load translations
   - Loading overlay while loading
   - Success message with count of loaded translations
   - Error handling with clear messages

4. **Clean Database Tables** (danger zone):
   - Warning box with red border:
     - Clear warning text
     - List of tables that will be cleaned
     - "This cannot be undone" message
   - "Clean All Tables" button (red/danger style)
   - Confirmation dialog before executing
   - Success message after cleaning

**Security:**
- All admin functions require admin role
- Show 403 error if non-admin tries to access
- Validate all inputs
- Show loading states during operations

**User Experience:**
- Clear workflow for loading translations (validate first, then load)
- Helpful error messages
- Loading indicators for async operations
- Success feedback with counts/details
- Warning for destructive operations

### Tasks

Please create/update:

1. **Update `frontend/index.html`**:
   - Add Admin view HTML structure:
     - Create User form section
     - Users list section
     - Load Translations from S3 section with two-step process
     - Clean Tables section with warning box
   - Add loading overlay for S3 operations
   - Add confirmation dialogs

2. **Update `frontend/app.js`**:
   - Admin view functions:
     - `loadUsers()`: Fetch and display user list
     - `createUser()`: Submit new user form
     - `validateS3Prefix()`: Validate S3 prefix structure
     - `loadTranslationsFromS3()`: Load translations after validation
     - `cleanDatabaseTables()`: Delete all data (with confirmation)
   - Form handling:
     - Clear form after success
     - Show inline error messages
     - Enable/disable buttons based on state
   - Loading states:
     - Show overlay during S3 operations
     - Disable buttons during operations
     - Show progress messages

3. **Update `frontend/styles.css`**:
   - Admin panel styles:
     - Section containers with borders
     - Form styles (consistent with login)
     - Users list/table styles
     - Warning box (red border, warning icon)
     - Danger button (red background)
     - Loading overlay styles
     - Success/error message styles
   - Form layout and spacing
   - Responsive design

4. **Validation logic**:
   - Frontend validation for required fields
   - S3 prefix format validation
   - Enable "Load Translations" only after successful validation
   - Confirmation dialog for clean tables operation

### Expected Output

After implementation:
- Admin panel visible only to admin users
- Can create new users with username, email, password, and admin role
- Users list displays all users with their info
- S3 loading workflow:
  1. Enter S3 prefix (e.g., "translations/llm-output/2025/10/latest")
  2. Enter description (e.g., "October 2024 Marketing Batch")
  3. Click "Validate Prefix"
  4. See validation result (success with file counts or error with missing files)
  5. If valid, "Load Translations" button enabled
  6. Click "Load Translations"
  7. Loading overlay appears
  8. Success message with count (e.g., "Loaded 150 translations")
- Clean tables:
  - Shows prominent warning
  - Requires confirmation
  - Executes and shows success message
- All operations show proper loading states and error handling
- Forms reset after successful operations
- Professional admin interface design
