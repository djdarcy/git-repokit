# RepoKit GitHub Deployment Demo

This is a complete, step-by-step demonstration of how to use RepoKit's universal bootstrap system to create, migrate, and deploy projects to GitHub.

## Prerequisites

1. **Install RepoKit**: Ensure RepoKit is installed and working
2. **GitHub Token**: Get a GitHub personal access token with `repo` permissions
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full repository access)
   - Copy the token (you'll only see it once!)

## Demo 1: Brand New Project

Let's create a Python project from scratch and deploy it to GitHub:

```bash
# Step 1: Create a new project directory
mkdir awesome-calculator
cd awesome-calculator

# Step 2: Add some initial code
cat > main.py << 'EOF'
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b

def main():
    print("Awesome Calculator!")
    print("2 + 3 =", add(2, 3))
    print("5 - 2 =", subtract(5, 2))

if __name__ == "__main__":
    main()
EOF

# Step 3: Add requirements
echo "# No external dependencies yet" > requirements.txt

# Step 4: Analyze what RepoKit will do
repokit analyze .

# Output should show:
# Project type: source_no_git
# Detected language: python
# Migration complexity: low
# Recommended strategy: safe
# Recommended branch strategy: simple

# Step 5: Store your GitHub token
repokit store-credentials --publish-to github --token "YOUR_GITHUB_TOKEN_HERE"

# Step 6: Adopt and deploy in one command!
repokit adopt . --publish-to github --private-repo --ai claude

# This will:
# - Create RepoKit directory structure
# - Initialize Git with main and dev branches
# - Generate Python-specific templates
# - Add Claude AI integration
# - Create a private GitHub repository
# - Push all branches to GitHub
```

**Expected Results:**
- New GitHub repository: `awesome-calculator`
- Branches: `main`, `dev`, `private` (private not pushed)
- Complete RepoKit structure with Python templates
- Claude AI integration files
- All code preserved and properly organized

## Demo 2: Existing Python Project

Let's migrate an existing Python project with some history:

```bash
# Step 1: Create a project with some Git history
mkdir weather-app
cd weather-app

# Initialize Git and create initial structure
git init
git config user.name "Demo User"
git config user.email "demo@example.com"

# Add some code
cat > weather.py << 'EOF'
import requests

def get_weather(city):
    """Get weather for a city (mock implementation)."""
    return f"Weather in {city}: Sunny, 25°C"

if __name__ == "__main__":
    city = input("Enter city: ")
    print(get_weather(city))
EOF

cat > requirements.txt << 'EOF'
requests>=2.28.0
EOF

# Create initial commits
git add .
git commit -m "Initial weather app"

# Add more features
mkdir tests
cat > tests/test_weather.py << 'EOF'
import unittest
from weather import get_weather

class TestWeather(unittest.TestCase):
    def test_get_weather(self):
        result = get_weather("London")
        self.assertIn("London", result)
        self.assertIn("°C", result)

if __name__ == "__main__":
    unittest.main()
EOF

git add tests/
git commit -m "Add basic tests"

# Step 2: Analyze the existing project
repokit analyze .

# Output should show:
# Project type: git_with_history
# Detected language: python
# Migration complexity: medium
# Recommended strategy: safe
# Recommended branch strategy: simple

# Step 3: Adopt preserving all Git history
repokit adopt . --strategy safe --publish-to github --organization "your-org"

# This will:
# - Preserve all existing Git history and commits
# - Add RepoKit structure around existing files
# - Create proper branch strategy
# - Deploy to your organization on GitHub
```

**Expected Results:**
- GitHub repository with full Git history preserved
- All existing commits and files intact
- Enhanced with RepoKit structure
- Professional organization-level deployment

## Demo 3: Complex Multi-Branch Project

Let's work with a more complex existing project:

```bash
# Step 1: Create a complex project
mkdir api-service
cd api-service

# Initialize with complex branch structure
git init
git config user.name "Demo User"
git config user.email "demo@example.com"

# Create main application
cat > app.py << 'EOF'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/version')
def version():
    return jsonify({'version': '1.0.0'})

if __name__ == '__main__':
    app.run(debug=True)
EOF

cat > requirements.txt << 'EOF'
Flask>=2.0.0
gunicorn>=20.0.0
EOF

# Initial commit on main
git add .
git commit -m "Initial API service"

# Create development branch with new features
git checkout -b develop
cat > auth.py << 'EOF'
def authenticate(token):
    """Simple token authentication."""
    return token == "valid-token"

def get_user_info(token):
    """Get user information from token."""
    if authenticate(token):
        return {"user": "demo", "role": "admin"}
    return None
EOF

git add auth.py
git commit -m "Add authentication module"

# Create feature branch
git checkout -b feature/user-management
mkdir models
cat > models/user.py << 'EOF'
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email
        }
EOF

git add models/
git commit -m "Add user model"

# Go back to develop
git checkout develop

# Step 2: Analyze this complex project
repokit analyze .

# Output should show:
# Project type: git_with_history
# Detected language: python
# Migration complexity: high (due to multiple branches)
# Recommended strategy: safe
# Recommended branch strategy: gitflow (detected existing pattern)

# Step 3: Adopt with intelligent branch mapping
repokit adopt . --strategy safe --branch-strategy auto --publish-to github

# This will:
# - Detect existing GitFlow-like pattern
# - Preserve all branches and their relationships
# - Add RepoKit structure while maintaining workflow
# - Map to appropriate RepoKit branch strategy
```

**Expected Results:**
- All existing branches preserved
- Complex Git history maintained
- RepoKit structure added intelligently
- Branch strategy detected and enhanced

## Demo 4: Legacy Project Migration

Migrate a legacy project with potential conflicts:

```bash
# Step 1: Create a "legacy" project with potential conflicts
mkdir legacy-tool
cd legacy-tool

# Create files that might conflict with RepoKit templates
cat > setup.py << 'EOF'
# Legacy setup.py with custom configuration
from setuptools import setup, find_packages

setup(
    name="legacy-tool",
    version="0.1.0",
    packages=find_packages(),
    # Custom legacy configuration here
    custom_legacy_setting=True,
)
EOF

mkdir .github
cat > .github/workflows/old-ci.yml << 'EOF'
# Legacy CI configuration
name: Old CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run legacy tests
        run: echo "Legacy testing approach"
EOF

# Add source code
mkdir src
cat > src/legacy_app.py << 'EOF'
"""Legacy application with old patterns."""

class LegacyProcessor:
    def __init__(self):
        self.data = []
    
    def process(self, item):
        # Old processing logic
        self.data.append(item.upper())
        return self.data

def main():
    processor = LegacyProcessor()
    processor.process("hello")
    processor.process("world")
    print("Processed:", processor.data)

if __name__ == "__main__":
    main()
EOF

# Step 2: Initialize Git
git init
git config user.name "Demo User"
git config user.email "demo@example.com"
git add .
git commit -m "Legacy codebase"

# Step 3: Analyze for migration conflicts
repokit analyze .

# Output should show:
# Project type: git_with_history  
# Detected language: python
# Migration complexity: medium
# Has template conflicts: Yes
# Recommended strategy: safe (due to conflicts)

# Step 4: Migrate with safe strategy to preserve existing files
repokit adopt . --strategy safe --publish-to github --dry-run

# See what would happen first
repokit adopt . --strategy safe --publish-to github

# This will:
# - Backup existing setup.py as setup.py.backup
# - Backup existing .github/workflows/ as .github_backup/
# - Add new RepoKit templates alongside
# - Preserve all legacy functionality
```

**Expected Results:**
- Legacy files preserved with `.backup` extensions
- New RepoKit templates added
- No existing functionality broken
- Clear migration path provided

## Authentication Methods Demo

### Method 1: Environment Variable
```bash
# Set token in environment
export GITHUB_TOKEN="your_token_here"

# Deploy using environment token
repokit adopt my-project --publish-to github
```

### Method 2: Stored Credentials
```bash
# Store token securely (one time)
repokit store-credentials --publish-to github --token "your_token_here"

# Deploy using stored credentials (no token needed)
repokit adopt my-project --publish-to github
```

### Method 3: Password Manager Integration
```bash
# Using pass password manager
repokit adopt my-project --publish-to github --token-command "pass show github/token"

# Using 1Password CLI
repokit adopt my-project --publish-to github --token-command "op read op://Personal/GitHub/token"

# Using LastPass CLI
repokit adopt my-project --publish-to github --token-command "lpass show --password github-token"
```

### Method 4: Organization Deployment
```bash
# Store organization credentials
repokit store-credentials --publish-to github --token "org_token" --organization "my-company"

# Deploy to organization
repokit adopt my-project --publish-to github --organization "my-company"
```

## Advanced Deployment Options

### Private Repository with Description
```bash
repokit adopt my-project \
  --publish-to github \
  --private-repo \
  --description "My awesome project built with RepoKit"
```

### Full Automation with All Options
```bash
repokit adopt my-project \
  --strategy auto \
  --branch-strategy auto \
  --publish-to github \
  --private-repo \
  --organization "my-company" \
  --ai claude \
  --description "Production-ready application"
```

### Multiple Projects Batch Deployment
```bash
# Deploy multiple projects
for project in project1 project2 project3; do
  echo "Deploying $project..."
  repokit adopt $project --publish-to github --strategy safe
done
```

## Troubleshooting Common Issues

### Issue 1: Token Authentication Fails
```bash
# Verify token is stored
cat ~/.repokit/credentials.json

# Test token manually
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Re-store credentials if needed
repokit store-credentials --publish-to github --token "new_token"
```

### Issue 2: Repository Already Exists
```bash
# RepoKit will show an error like:
# "Repository already exists at https://github.com/user/project"

# Solutions:
# 1. Use a different name
repokit adopt my-project --publish-to github --name "my-project-v2"

# 2. Delete existing repository first (careful!)
# 3. Push to existing repository (if you own it)
```

### Issue 3: Uncommitted Changes
```bash
# RepoKit detects uncommitted changes and warns you
# Commit changes first:
git add .
git commit -m "Save work before RepoKit adoption"

# Then proceed with adoption
repokit adopt . --publish-to github
```

### Issue 4: Template Conflicts
```bash
# Use safe strategy to preserve existing files
repokit adopt my-project --strategy safe --publish-to github

# Or use merge strategy to combine configurations  
repokit adopt my-project --strategy merge --publish-to github

# Check backup files created
ls -la *.backup
```

## Success Verification

After deployment, verify everything worked:

```bash
# Check GitHub repository was created
# Visit: https://github.com/your-username/your-project

# Verify local repository
git remote -v
git branch -a

# Check RepoKit structure
ls -la
# Should see: docs/, private/, scripts/, tests/, etc.

# Verify branches were pushed
git ls-remote origin

# Test the application still works
python main.py  # or your app's entry point
```

## Next Steps After Deployment

1. **Review Generated Templates**: Check and customize the generated files
2. **Set Up CI/CD**: Configure GitHub Actions workflows  
3. **Add Collaborators**: Invite team members to the repository
4. **Configure Branch Protection**: Set up branch protection rules
5. **Update Documentation**: Customize README and docs for your project

## Complete Example Script

Here's a complete script you can run to test RepoKit deployment:

```bash
#!/bin/bash
# RepoKit Deployment Test Script

set -e  # Exit on any error

echo "=== RepoKit GitHub Deployment Demo ==="

# Cleanup any existing test
rm -rf repokit-demo-test
rm -f ~/.repokit/credentials.json

# Create test project
mkdir repokit-demo-test
cd repokit-demo-test

# Add sample code
cat > calculator.py << 'EOF'
def calculate(operation, a, b):
    """Simple calculator function."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b if b != 0 else "Cannot divide by zero"
    else:
        return "Unknown operation"

def main():
    print("RepoKit Demo Calculator")
    print("2 + 3 =", calculate("add", 2, 3))
    print("10 - 4 =", calculate("subtract", 10, 4))
    print("5 * 6 =", calculate("multiply", 5, 6))
    print("15 / 3 =", calculate("divide", 15, 3))

if __name__ == "__main__":
    main()
EOF

echo "# RepoKit Demo Calculator" > README.md
echo "# No external dependencies" > requirements.txt

echo "1. Analyzing project..."
repokit analyze .

echo "2. Testing dry run..."
repokit adopt . --dry-run

echo "3. Ready for GitHub deployment!"
echo "   Run: repokit store-credentials --publish-to github --token YOUR_TOKEN"
echo "   Then: repokit adopt . --publish-to github --private-repo"
echo ""
echo "Demo project created in: $(pwd)"
```

Save this as `demo.sh`, make it executable with `chmod +x demo.sh`, and run it to test RepoKit's capabilities!

## Summary

RepoKit's universal bootstrap system provides:

✅ **Intelligent Analysis**: Understands any project type and complexity  
✅ **Safe Migration**: Preserves existing code and Git history  
✅ **Automated Deployment**: One-command GitHub deployment  
✅ **Flexible Authentication**: Multiple secure token methods  
✅ **Professional Structure**: Industry-standard repository organization  
✅ **AI Integration**: Optional Claude AI development assistance

Whether you're starting fresh or migrating complex legacy projects, RepoKit makes professional repository setup and deployment effortless.