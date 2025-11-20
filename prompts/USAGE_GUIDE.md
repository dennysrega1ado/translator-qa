# How to Use These Prompts with Claude Code

This guide shows you how to effectively use these prompts with Claude Code CLI to build the Translation QA System (or similar projects).

## 🚀 Quick Start

### Option 1: Build the Complete System

Execute prompts sequentially from 01 to 15:

```bash
# Start Claude Code in your project directory
cd /path/to/new-project
claude

# Then copy-paste each prompt in order:
# 1. First, paste content from 01_project_initialization.md
# 2. Wait for completion and verify output
# 3. Then paste content from 02_database_models.md
# 4. Continue through all 15 prompts
```

### Option 2: Build Specific Components

If you only need certain features:

```bash
# For just authentication:
# Use prompts: 01, 02, 03

# For just frontend:
# Use prompts: 01, 09, 10, 11

# For deployment:
# Use prompts: 14, 15
```

## 📝 Detailed Usage Instructions

### Step-by-Step Process

#### 1. **Prepare Your Environment**

```bash
# Create project directory
mkdir my-translation-qa
cd my-translation-qa

# Initialize git (recommended)
git init

# Start Claude Code
claude
```

#### 2. **Use Each Prompt Systematically**

For each prompt file:

**a. Read the prompt first**
- Understand the context
- Review requirements
- Check expected output

**b. Customize if needed**
- Adjust tech stack
- Modify naming conventions
- Change specific requirements

**c. Submit to Claude Code**
- Copy the entire prompt content
- Paste into Claude Code chat
- Let it work through the tasks

**d. Verify the output**
- Check that files were created
- Test the functionality
- Run any verification commands

**e. Commit your progress**
```bash
git add .
git commit -m "Step 01: Project initialization complete"
```

### Example Session

Here's a complete example of using the first prompt:

```bash
$ claude

# Copy-paste from 01_project_initialization.md
You: [Paste the entire content of 01_project_initialization.md]

# Claude Code will:
# - Create directory structure
# - Create Dockerfile for backend
# - Create Dockerfile for frontend
# - Create docker-compose.yml
# - Create requirements.txt
# - Create basic README

# Verify the output
You: Let's verify everything works. Can you run docker-compose config to validate?

Claude: [Validates docker-compose.yml]

# Test it
You: Now let's start the services with docker-compose up

Claude: [Starts services and shows logs]

# Commit
You: Perfect! Let's commit this progress with git

Claude: [Creates git commit]
```

## 🎯 Tips for Success

### 1. **One Prompt at a Time**

Don't combine multiple prompts in a single conversation. Complete each step fully before moving to the next.

✅ **Good:**
```
Complete step 01 → Verify → Test → Commit
Then start step 02 → Verify → Test → Commit
```

❌ **Bad:**
```
Combine steps 01, 02, and 03 into one mega-prompt
```

### 2. **Verify Between Steps**

After each prompt, verify the output:

```bash
# Check files were created
ls -la

# Run tests
docker-compose config

# Start services
docker-compose up -d

# Check logs
docker-compose logs
```

### 3. **Use Git Commits**

Commit after each successful step:

```bash
git add .
git commit -m "Step 03: Authentication system complete"
```

This allows you to:
- Roll back if needed
- Track progress
- Resume later

### 4. **Customize Before Submitting**

Edit prompts to match your needs:

```markdown
# Original
- **Backend**: Python 3.11, FastAPI

# Customized for your stack
- **Backend**: Python 3.12, Flask
```

### 5. **Ask for Clarifications**

If Claude Code's output doesn't match expectations:

```
You: The authentication endpoint isn't working as expected.
     Can you verify the JWT token generation in auth.py?
```

## 🔧 Troubleshooting

### Issue: Prompt too long for Claude Code

**Solution**: Break it into smaller parts

```
# Instead of the full prompt, do:
You: Let's implement the authentication system. First, create the
     auth.py file with password hashing functions using bcrypt.

# Then after completion:
You: Now add the JWT token creation and verification functions.

# Then:
You: Finally, create the auth router with the login endpoint.
```

### Issue: Output doesn't match expected results

**Solution**: Reference the expected output section

```
You: According to the prompt, I should be able to login with
     admin/admin123 and receive a JWT token. Can you verify
     the authentication is working correctly?
```

### Issue: Dependencies missing

**Solution**: Ask Claude to install them

```
You: The bcrypt import is failing. Can you add bcrypt to
     requirements.txt and reinstall dependencies?
```

## 📊 Progress Tracking

Use this checklist to track your progress:

```markdown
## Project Progress

- [ ] 01 - Project Initialization
- [ ] 02 - Database Models
- [ ] 03 - Authentication System
- [ ] 04 - Translations API
- [ ] 05 - Manual Scores API
- [ ] 06 - Reports API
- [ ] 07 - S3 Service
- [ ] 08 - Prompts API
- [ ] 09 - Frontend Structure
- [ ] 10 - Translation Review Interface
- [ ] 11 - Summary Dashboard
- [ ] 12 - Admin Panel
- [ ] 13 - Reports View
- [ ] 14 - Docker Deployment
- [ ] 15 - Documentation
```

## 🎓 Advanced Techniques

### Parallel Development

If you have multiple Claude Code sessions:

```bash
# Terminal 1: Backend development
cd backend
claude
# Use prompts 03-08

# Terminal 2: Frontend development
cd frontend
claude
# Use prompts 09-13
```

### Iterative Refinement

After completing all prompts, refine:

```
You: Now that the basic system is working, let's add these enhancements:
     1. Add real-time validation for score inputs
     2. Improve loading states with skeleton screens
     3. Add keyboard shortcuts for navigation
```

### Testing Integration

Add testing after each major section:

```
You: Before we move to step 05, let's add pytest tests for the
     authentication system we just built. Include tests for:
     - Password hashing
     - Token generation
     - Login endpoint
     - Protected routes
```

## 📈 Expected Timeline

With Claude Code, following these prompts sequentially:

| Phase | Prompts | Estimated Time |
|-------|---------|----------------|
| Foundation | 01-02 | 30-60 minutes |
| Backend API | 03-08 | 2-3 hours |
| Frontend | 09-13 | 3-4 hours |
| Deployment | 14-15 | 1-2 hours |
| **Total** | **15 prompts** | **~8 hours** |

**Note**: This assumes familiarity with the tech stack and prompt engineering.

## 🎯 Success Criteria

You'll know you're successful when:

✅ Each prompt produces working code on first try
✅ Features match the expected output
✅ No major debugging needed between steps
✅ Application runs end-to-end after final step
✅ Docker compose starts all services cleanly
✅ Can login and use all features

## 🤝 Getting Help

If you get stuck:

1. **Re-read the prompt**: Ensure you used it correctly
2. **Check the Expected Output**: Compare with what you got
3. **Review previous steps**: May have missed something
4. **Ask Claude to debug**: Provide error messages
5. **Consult the main README**: May have setup issues

## 🎬 Video Tutorial Outline

If creating a video tutorial, follow this structure:

1. **Introduction** (2 min)
   - Show the finished application
   - Overview of the 15-step process

2. **Setup** (3 min)
   - Create project directory
   - Start Claude Code
   - Show the prompts folder

3. **Demo Steps 01-03** (10 min)
   - Show how to use first 3 prompts
   - Demonstrate verification
   - Show git commits

4. **Fast-forward Remaining Steps** (5 min)
   - Quickly show executing other prompts
   - Highlight key features being built

5. **Final Demo** (5 min)
   - Show complete working application
   - All features working
   - Docker logs clean

6. **Summary** (2 min)
   - Metrics (time saved, lines of code)
   - Benefits of prompt-driven development

**Total**: ~27 minutes

---

**Happy Building! 🚀**

These prompts have been battle-tested and optimized. Follow them systematically, and you'll have a production-ready application in no time.
