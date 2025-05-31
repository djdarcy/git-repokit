# RepoKit Migration Guide

This guide gives a comprehensive explanation of how to migrate any existing project to the RepoKit structure and deploy it to GitHub with full automation.

## Overview

RepoKit's universal migration system should be able to handle **any type of project**, from empty directories to complex Git repositories with existing history. The system intelligently analyzes your project and recommends the best migration approach.

### What RepoKit Can Migrate

- **Empty directories** → New RepoKit projects with full structure
- **Source code without Git** → Projects with proper Git initialization and RepoKit structure  
- **Existing Git repositories** → Preserves history while adding RepoKit structure
- **Complex multi-branch projects** → Maintains existing branches and adds RepoKit workflow
- **Any programming language** → Python, JavaScript, Java, C#, Go, Rust, and generic projects

## Quick Start

### 1. Analyze Any Project

Before migration, analyze your project to understand what RepoKit will do:

```bash
# Analyze any directory or project
repokit analyze /path/to/your/project
```

**Example output:**
```
=== PROJECT ANALYSIS: /path/to/my-python-app ===
  Project type: source_no_git
  Detected language: python
  Migration complexity: low
  Recommended strategy: safe
  Recommended branch strategy: simple

  Git repository: No
  File counts: python: 15, markdown: 2, config: 3
  
  Migration steps:
    1. Backup existing project (recommended)
    2. Apply RepoKit directory structure
    3. Initialize Git repository with simple strategy
    4. Generate Python-specific templates
    5. Create remote repository if requested
```

### 2. Adopt Your Project

Use the `adopt` command to convert your project in-place:

```bash
# Dry run to see what would happen
repokit adopt /path/to/your/project --dry-run

# Actually adopt the project
repokit adopt /path/to/your/project

# Adopt and deploy to GitHub in one command
repokit adopt /path/to/your/project --publish-to github
```

## Migration Scenarios

### Scenario 1: Brand New Project

**Situation:** You have an empty directory or just a few files, no Git history.

```bash
mkdir my-new-app
cd my-new-app
echo 'print("Hello World")' > main.py

# Analyze first
repokit analyze .

# Adopt with auto-deployment
repokit adopt . --publish-to github --private-repo
```

**What happens:**
- Detects Python project
- Recommends "simple" branch strategy (main + dev)
- Creates full RepoKit structure
- Initializes Git with proper branches
- Generates Python templates (setup.py, requirements.txt, etc.)
- Creates private GitHub repository
- Pushes all branches to GitHub

### Scenario 2: Existing Code, No Git

**Situation:** You have a working project with source code but no version control.

```bash
# Your existing project structure:
my-python-app/
├── src/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── README.md

# Analyze the project
repokit analyze my-python-app

# Adopt with safe strategy (preserves all existing files)
repokit adopt my-python-app --strategy safe --publish-to github
```

**What happens:**
- Detects Python project with existing structure
- Uses "safe" strategy (no file overwrites)
- Adds missing RepoKit directories (docs, tests, private, etc.)
- Preserves your existing files exactly as they are
- Initializes Git and creates branch structure
- Publishes to GitHub with your existing code intact

### Scenario 3: Existing Git Repository

**Situation:** You have a Git repository with history that you want to enhance with RepoKit.

```bash
# Your existing Git project
my-git-project/
├── .git/           # Existing Git history
├── src/
├── tests/
└── README.md

# Analyze first
repokit analyze my-git-project

# Adopt preserving all Git history
repokit adopt my-git-project --strategy safe --branch-strategy auto
```

**What happens:**
- Detects existing Git repository and branch strategy
- Preserves all Git history and existing branches
- Adds RepoKit structure around existing files
- Sets up worktrees for branch isolation
- Optionally publishes to GitHub with full history preserved

### Scenario 4: Complex Multi-Branch Project

**Situation:** You have a sophisticated Git repository with multiple branches, remotes, and development workflow.

```bash
# Complex existing project
my-complex-app/
├── .git/           # Complex Git history
├── branches: main, develop, feature/new-ui, hotfix/security
├── existing remote: origin
└── multiple developers working

# Analyze to understand complexity
repokit analyze my-complex-app

# Adopt with merge strategy for template integration
repokit adopt my-complex-app --strategy merge --branch-strategy auto
```

**What happens:**
- Detects complex Git structure and existing branch strategy
- Preserves all existing branches and remotes
- Maps existing branches to RepoKit workflow if compatible
- Merges RepoKit templates with existing configuration files
- Maintains compatibility with existing development workflow

## GitHub Deployment with Tokens

### Setting Up GitHub Authentication

RepoKit supports multiple authentication methods for GitHub deployment:

#### Method 1: Environment Variable
```bash
export GITHUB_TOKEN="your_github_token_here"
repokit adopt my-project --publish-to github
```

#### Method 2: Store Credentials
```bash
# Store token securely
repokit store-credentials --publish-to github --token "your_token"

# Now you can deploy without specifying token
repokit adopt my-project --publish-to github
```

#### Method 3: Token Command
```bash
# Use password manager or secure command
repokit adopt my-project --publish-to github --token-command "pass show github/token"
```

### GitHub Deployment Options

```bash
# Private repository
repokit adopt my-project --publish-to github --private-repo

# Organization repository
repokit adopt my-project --publish-to github --organization "my-company"

# Public repository with description
repokit adopt my-project --publish-to github --description "My awesome project"

# Complete deployment with all options
repokit adopt my-project \
  --publish-to github \
  --private-repo \
  --organization "my-company" \
  --strategy safe \
  --branch-strategy standard
```

### Full Automation Example

Here's a complete workflow from project creation to GitHub deployment:

```bash
# Create a new Python project
mkdir awesome-python-tool
cd awesome-python-tool

# Add some initial code
echo 'def main():' > main.py
echo '    print("Hello from my awesome tool!")' >> main.py
echo '' >> main.py
echo 'if __name__ == "__main__":' >> main.py
echo '    main()' >> main.py

# Create basic requirements
echo 'requests>=2.28.0' > requirements.txt

# Analyze what RepoKit will do
repokit analyze .

# Adopt and deploy in one command
repokit adopt . \
  --publish-to github \
  --private-repo \
  --strategy safe \
  --ai claude
```

This single command will:
1. Detect it's a Python project
2. Apply RepoKit structure safely
3. Initialize Git with appropriate branch strategy
4. Generate Python-specific templates
5. Add Claude AI integration files
6. Create a private GitHub repository
7. Push all branches to GitHub
8. Set up proper branch protection and settings

## Migration Strategies Explained

### Auto Strategy (Recommended)
```bash
repokit adopt my-project --strategy auto
```
- RepoKit analyzes your project and chooses the best strategy
- Safe for uncommitted changes
- Intelligent decision-making based on project complexity

### Safe Strategy
```bash
repokit adopt my-project --strategy safe
```
- **Never overwrites existing files**
- Creates backups of any conflicts
- Preserves all existing Git history
- **Best for production projects**

### Merge Strategy
```bash
repokit adopt my-project --strategy merge
```
- Intelligently merges RepoKit templates with existing files
- Combines configuration files when possible
- **Best for projects that want full RepoKit integration**

### Replace Strategy
```bash
repokit adopt my-project --strategy replace
```
- Replaces existing template files with RepoKit versions
- Keeps your source code untouched
- **Use when you want fresh RepoKit configuration**

## Branch Strategies

RepoKit supports multiple branching workflows:

### Simple Strategy (Recommended for small projects)
- Branches: `main`, `dev`
- Worktrees: `main`, `dev`
- **Best for**: Personal projects, small teams

### Standard Strategy (RepoKit default)  
- Branches: `private`, `dev`, `main`, `test`, `staging`, `live`
- Worktrees: `main`, `dev`
- **Best for**: Professional projects, CI/CD workflows

### GitFlow Strategy
- Branches: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`
- **Best for**: Large teams, complex release cycles

### Auto Strategy
```bash
repokit adopt my-project --branch-strategy auto
```
RepoKit detects your existing branch strategy and adapts accordingly.

## Command Reference

### Analysis Commands
```bash
# Basic analysis
repokit analyze /path/to/project

# Verbose analysis with detailed Git information
repokit analyze /path/to/project --verbose

# Analyze current directory
repokit analyze .
```

### Adoption Commands
```bash
# Basic adoption
repokit adopt /path/to/project

# Adoption with specific strategies
repokit adopt /path/to/project --strategy safe --branch-strategy simple

# Dry run (see what would happen)
repokit adopt /path/to/project --dry-run

# Adopt current directory
repokit adopt .

# Adopt and deploy to GitHub
repokit adopt /path/to/project --publish-to github

# Full automation
repokit adopt /path/to/project \
  --strategy auto \
  --branch-strategy auto \
  --publish-to github \
  --private-repo \
  --organization "my-org" \
  --ai claude
```

### Legacy Migration Commands
```bash
# Traditional migration (still supported)
repokit migrate /path/to/project --migration-strategy safe

# Migration with specific language
repokit migrate /path/to/project --language python
```

## Troubleshooting

### Uncommitted Changes Warning
If RepoKit detects uncommitted changes:
```
WARNING: Uncommitted changes detected!
Continue with adoption? Changes should be committed first. [y/N]:
```

**Solution:** Commit your changes first, or use `--strategy safe` which handles uncommitted changes carefully.

### GitHub Authentication Issues
```bash
# Test your GitHub token
repokit store-credentials --publish-to github --token "your_token"

# Verify stored credentials
repokit analyze . --publish-to github  # Will validate token
```

### Template Conflicts
When RepoKit finds existing files that match template names:
- **Safe strategy**: Creates backups with `.backup` extension
- **Merge strategy**: Attempts to merge content intelligently  
- **Replace strategy**: Replaces with RepoKit templates

### Permission Errors
```bash
# Ensure you have write permissions
ls -la /path/to/project

# For GitHub deployment, ensure token has repo permissions
# Check token scopes at: https://github.com/settings/tokens
```

## Best Practices

### 1. Always Analyze First
```bash
repokit analyze my-project  # Understand what will happen
repokit adopt my-project --dry-run  # Preview changes
repokit adopt my-project  # Execute adoption
```

### 2. Use Safe Strategy for Production
```bash
repokit adopt production-app --strategy safe --publish-to github
```

### 3. Backup Important Projects
```bash
cp -r my-important-project my-important-project-backup
repokit adopt my-important-project
```

### 4. Test Deployment on Personal Repos First
```bash
# Test on personal account first
repokit adopt test-project --publish-to github

# Then deploy to organization
repokit adopt real-project --publish-to github --organization "company"
```

### 5. Use AI Integration for Enhanced Development
```bash
repokit adopt my-project --ai claude --publish-to github
```

This adds Claude AI integration with:
- CLAUDE.md configuration file
- Development workflow process documentation  
- Context management tools
- Private instruction files

## Migration vs. Adoption

| Feature | `migrate` (Legacy) | `adopt` (New) |
|---------|-------------------|---------------|
| **Intelligence** | Basic directory analysis | Full project analysis with Git state |
| **Git Integration** | Limited | Complete Git history preservation |
| **Auto-deployment** | Separate command | Integrated with `--publish-to` |
| **Strategy Selection** | Manual only | Auto-detection available |
| **Branch Strategy** | Not handled | Full branch strategy management |
| **Language Detection** | Manual specification | Automatic detection |
| **Recommendation Engine** | None | Smart recommendations |

**Recommendation:** Use `adopt` for all new migrations. The `migrate` command is maintained for compatibility but `adopt` provides a superior experience.

## What's New in Universal Bootstrap

RepoKit's universal bootstrap system represents a major advancement:

### Enhanced Intelligence
- **Project Type Detection**: Empty, source code, Git repos, RepoKit projects
- **Language Detection**: Automatic detection of Python, JavaScript, Java, C#, Go, Rust
- **Git State Analysis**: Branch detection, uncommitted changes, remotes
- **Complexity Assessment**: Low/medium/high migration complexity scoring

### Smart Recommendations  
- **Auto Strategy Selection**: Recommends best migration approach
- **Branch Strategy Mapping**: Detects and preserves existing workflows
- **Step-by-Step Guidance**: Contextual migration steps for each project type

### Integrated Deployment
- **One-Command Deployment**: From analysis to GitHub in single command
- **Multiple Auth Methods**: Environment variables, stored credentials, commands
- **Organization Support**: Deploy to personal or organization repositories  
- **AI Integration**: Optional Claude AI integration for enhanced development

### Preserved Functionality
All previous migration capabilities are preserved and enhanced:
- ✅ **Safe/Replace/Merge strategies** → Now with auto-selection
- ✅ **Template conflict handling** → Enhanced with intelligent merging
- ✅ **Language-specific templates** → Automatic detection and application  
- ✅ **Git repository preservation** → Enhanced with branch strategy detection
- ✅ **Dry run capabilities** → Available in both migrate and adopt commands

The new system doesn't remove functionality ("migrate" may be deprecated though in the future) - for now though it makes it smarter, more automated, and more comprehensive.