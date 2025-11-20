# Step 9: Frontend Structure & Authentication UI

## Prompt

Build the frontend structure with login screen and navigation system.

### Context

Backend API is complete. Now we need to create the frontend user interface with authentication, navigation, and state management.

### Requirements

**Frontend Architecture:**
- Single-page application (SPA) using vanilla JavaScript
- No frameworks - pure HTML/CSS/JS
- Modern responsive design with Tailwind CSS
- State management using JavaScript object
- JWT token stored in localStorage
- Material Icons for UI elements

**UI Structure:**
1. Login Screen - shown by default
2. Main Application Screen - shown after login with:
   - Navigation bar with user info and logout
   - Multiple views (Translations, Summary, Reports, Admin)
   - View switching without page reload

**Login Screen Features:**
- Username and password inputs
- Login button
- Error message display
- "Powered by" footer with logo
- Smooth transition to main app after login

**Navigation Bar:**
- Brand/logo ("Translation QA")
- Navigation links: Translations, Summary, Reports (admin only), Admin (admin only)
- User info display (username)
- Logout button

**State Management:**
- Global state object with: token, user, currentView, translations, etc.
- API request helper with automatic token injection
- Automatic logout on 401 responses

### Tasks

Please create:

1. **`frontend/index.html`**:
   - HTML structure with two main sections:
     - Login screen (visible by default)
     - Main app screen (hidden, shown after login)
   - Include Tailwind CSS from CDN
   - Include Material Icons
   - Include Chart.js for summary charts
   - Semantic HTML structure
   - Modal containers for dialogs
   - Success/error overlays

2. **`frontend/app.js`**:
   - State management object
   - API helper function with token injection
   - Authentication functions:
     - `login(username, password)`: Call API, store token, show main screen
     - `logout()`: Clear token, show login screen
     - `checkAuth()`: Verify token on page load
   - Screen management:
     - `showLoginScreen()`: Display login, hide main app
     - `showMainScreen()`: Display main app, hide login, setup user
   - View management:
     - `showView(viewName)`: Switch between different views
   - Initialization:
     - Check for existing token on load
     - Setup event listeners
     - Show appropriate screen

3. **`frontend/styles.css`**:
   - Login screen styles:
     - Centered container
     - Modern form design
     - Smooth animations
   - Navigation bar styles:
     - Fixed top navigation
     - Active link highlighting
   - Global styles:
     - Color scheme (professional blue/gray)
     - Typography
     - Button styles (primary, secondary, danger)
     - Form elements
     - Utility classes

4. **`frontend/nginx.conf`**:
   - Serve static files
   - Proxy API requests to backend
   - SPA routing (all routes serve index.html)
   - Proper CORS headers

### Expected Output

After implementation:
- Opening app shows login screen
- Can login with admin/admin123
- After login, shows navigation bar with username
- Can click navigation links (views are empty placeholders for now)
- Admin users see Reports and Admin links
- Regular users don't see admin-only links
- Can logout and return to login screen
- Token persists in localStorage (survives page refresh)
- Professional, modern UI design
