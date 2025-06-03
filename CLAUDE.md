# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RepoKit is a Git repository template generator that creates standardized repository structures with complex branching strategies and worktree-based workflows. It automates repository setup with consistent structures, branch configurations, and GitHub/GitLab integration.

## Common Development Commands

```bash
# Run tests
pytest

# Format code
black .

# Lint code
flake8

# Type checking
mypy repokit/

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run comprehensive test suite
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --unit        # Fast unit tests
python tests/run_tests.py --integration # CLI integration tests  
python tests/run_tests.py --github      # GitHub API tests (requires token)
```

## Test Development Guidelines

### Test Script Management
- **One-off test scripts**: Store in `tests/one-offs/` directory
- **Test runs**: Always use `test_runs/` directory (not test-runs)
- **Keep test artifacts**: Don't delete one-off scripts - they may be useful later (use later to brainstorm unit tests or integration tests)

Example:
```bash
# Create test script
mkdir -p tests/one-offs
vim tests/one-offs/test_directory_profiles.py

# Run tests that create artifacts
cd test_runs  # Standardized location
python -m repokit create test-project --dir-profile minimal
```

## Development Workflow

### Branch Strategy
Follow this workflow for all development:

```
private → dev → main → test → staging → live
```

### Proper Git Workflow

1. **Always start development in private branch or a new feature branch "feat/description"**:
   ```bash
   git checkout private
   # Make your changes here
   git add .
   git commit -m "feat: description of changes"
   ```

**IMPORTANT**: Never include attribution lines like "Co-Authored-By" or "Generated with" in commit messages. All attributions are handled via git config user settings.

2. **Merge to dev using --no-ff --no-commit**:
   ```bash
   git checkout dev
   git merge private --no-ff --no-commit
   # Resolve any conflicts
   git commit -m "merge: bring private changes to dev
   
   Brief description of what was merged and why."
   ```

3. **Test thoroughly in dev**, then merge to main:
   ```bash
   git checkout main  
   git merge dev --no-ff --no-commit
   git commit -m "merge: tested changes from dev to main"
   ```

### Conversation Logging
**IMPORTANT**: Always create conversation logs in `private/claude/` following this format:
```
private/claude/YYYY_MM_DD__HH_MM_SS__topic.md
```

Example: `private/claude/2025_05_31__09_38_11__branch_conditional_excludes_and_workflow_badges.md`

### Branch-Conditional Files
Files tracked in `private` but ignored in public branches:
- `CLAUDE.md` - AI integration instructions
- `private/claude/` - Conversation logs and development notes
- `private/docs/` - Development documentation  
- `private/notes/` - Development notes
- `private/temp/` - Temporary development files

This should be handled automatically by RepoKit's local exclude setup (but check if necessary).
```

## Architecture Overview

### Core Components

1. **CLI Interface (`repokit/cli.py`)**: Entry point handling commands like `create`, `bootstrap`, `migrate`, `analyze`, and `publish`. Uses argparse with hierarchical configuration support.

2. **Repository Manager (`repokit/repo_manager.py`)**: Central orchestrator that:
   - Creates standardized directory structures
   - Initializes Git with multi-branch strategy
   - Sets up worktrees for branch isolation
   - Implements private content protection via pre-commit hooks
   - Manages template generation

3. **Template Engine (`repokit/template_engine.py`)**: Handles template loading and rendering from:
   - `repokit/templates/common/` - README, .gitignore, CONTRIBUTING
   - `repokit/templates/github/` - Workflows, CODEOWNERS, issue templates
   - `repokit/templates/languages/` - Language-specific files
   - Custom template directories via `--template-dir`

4. **Configuration System (`repokit/config.py`)**: Hierarchical config management:
   - Default values → Global config (`~/.repokit/config.json`) → Project config (`./.repokit.json`) → Environment variables (`REPOKIT_*`) → CLI arguments
   - Manages branch strategies and Git user configuration

5. **Remote Integration (`repokit/remote_integration.py`)**: Handles GitHub/GitLab API interactions for repository creation and pushing.

### Key Workflows

**Branching Structure**:
```
private → feature-* → dev → main → test → staging → live
```

**Worktree Layout**:
```
project/
├── local/     # Main repo (private branch)
├── github/    # Worktree for main branch
└── dev/       # Worktree for dev branch
```

**Private Content Protection**: Pre-commit hooks prevent commits from `private/`, `convos/`, and `logs/` directories.

## Important Implementation Notes

- Python 3.7+ required (3.6+ in setup.py but 3.7+ in pyproject.toml)
- No runtime dependencies - pure Python implementation
- Uses `pkg_resources` for template resource loading
- Console entry point: `repokit` → `repokit.cli:main`
- Version management in both `setup.py` and `pyproject.toml` (currently 0.1.1)

## Private Branch Guidelines

### Documentation Requirements

- **ALWAYS** document all work performed in timestamped files under `./private/claude/`
- Use filename format: `YYYY_MM_DD__HH_MM_SS__(TOPIC).md`
- Include all commands executed, their outputs, and summaries

### Version Control Practices

- The `private` branch is LOCAL ONLY - never push to remote repositories
- Commit frequently to track all changes and edits
- Make minimal edits to preserve diff readability:
  - Avoid unnecessary variable/function/class name changes
  - Avoid changing comments unless they clarify intent
  - Only rename when truly warranted for clarity or correctness
  - Preserve existing code structure when possible (unless refactoring improves design)

### Private Content Structure

```
private/
├── claude/         # All Claude-assisted work documentation
│   └── YYYY_MM_DD__HH_MM_SS__(TOPIC).md
├── convos/         # Conversation logs (protected from commits)
├── logs/           # System logs (protected from commits)
└── CLAUDE.md       # This guidance file
```

### Excluded Content

The `revisions/` folder should NOT exist in these branches:
- live
- staging
- test
- main/github
- dev

It should only be tracked in the `private` branch for local version control.

### CASCADE Protocol - Cascading Branch Updates

RepoKit uses the CASCADE Protocol (Cascading Automated Sync for Continuous And Dependable Evolution) for systematic branch management:

```
private → dev → main → test → staging → live
         ↑_______________________________|
                  (fix cascade back)
```

#### Key CASCADE Rules:
1. **Always merge with `--no-ff --no-commit`** to review changes before committing
2. **Test at every step** - run full test suite after each merge
3. **Fix cascade back** - fixes flow backward through hierarchy to maintain consistency
4. **Never push private branch** - it contains sensitive AI documentation
5. **Use guardrails** - run `repokit check-guardrails` before all commits

#### CASCADE Implementation:
```bash
# 1. Check current state
repokit check-guardrails
git status

# 2. Merge with review
git checkout dev
git merge private --no-ff --no-commit
# Review and remove any private files if needed
git status
git commit -m "cascade: merge private to dev"

# 3. Test thoroughly
python tests/run_tests.py --all

# 4. If tests fail, fix and cascade back:
# Fix in dev → merge to private → re-test → re-merge forward

# 5. Continue cascade
git checkout main
git merge dev --no-ff --no-commit
# ... repeat process through test → staging → live
```

#### Private Content Protection:
With RepoKit guardrails installed:
- Private files (CLAUDE.md, private/claude/) remain in working directory
- They are automatically ignored in public branches via .gitignore
- Post-checkout hooks restore them when switching branches
- Pre-commit hooks prevent accidental commits

See `private/claude/2025_05_31__22_45_00__cascade_protocol_documentation.md` for full details.

## Additional Instructions

**IMPORTANT**: Refer to the detailed instructions in `./private/claude/instructions/` for advanced workflows:

1. **Step1 - CONTEXT REBUILDER**: How to reconstruct and clarify conversational context (use notes in `.\private\claude` as pointers)
2. **Step2 - THE DEV WORKFLOW PROCESS**: The core 5-stage process for complex problem solving (see below)
3. **Step3 - SUMMARIZE IT! CONTEXT-BRIDGE**: How to create detailed conversation summaries for handoffs

### The Dev Workflow Process (The Process)

When tackling complex problems or making significant decisions, use **THE PROCESS** - a 5-stage systematic approach:

#### 🔁 The 5 Stages:

1. **Problem Analysis**
   - Define the core problem with precision
   - Break into sub-problems/dimensions
   - Explore pros, cons, edge cases, risks, surrounding factors, future considerations, extenuating considerations, etc.
   - Consider short-term vs long-term implications

2. **Conceptual Exploration**
   - Understand WHY the problem exists
   - Explore mental models and analogies
   - Consider multiple approach types
   - Examine relationships between elements

3. **Brainstorming Solutions**
   - Generate 3-5 possible solutions
   - Analyze pros/cons/neutral elements/edge cases/etc for each
   - Evaluate feasibility, scalability, complexity, trade-offs, and alignment with long-term goals
   - Consider hybrid approaches

4. **Synthesis and Recommendation**
   - Combine best elements from various solutions
   - Select optimal approach based on:
     - Core problem resolution
     - Edge case handling
     - Long-term alignment
     - Time/complexity/risks/other factors balance
   - Justify with evidence from previous steps

5. **Implementation Plan**
   - Define step-by-step roadmap
   - Include milestones, feedback loops, and brief time considerations (which helps establish complexity)
   - Outline resources/tools/technologies needed
   - Identify contingency plans
   - Define success criteria

**When to use "The Process"**: For any complex problem, design decision, bug investigation, or strategic choice. Always enumerate multiple possibilities rather than jumping to a single solution.

## History Protection

RepoKit now includes advanced history protection to prevent sensitive commit details from leaking to public branches.

### Safe Merge Dev Command

Use `repokit safe-merge-dev` to merge development branches with automatic history protection:

```bash
# Merge a prototype branch (auto-squashes)
repokit safe-merge-dev prototype/new-feature

# Merge a feature branch (interactive)
repokit safe-merge-dev feature/oauth-integration

# Force squash with custom message
repokit safe-merge-dev feature/api --squash --message "Add REST API"

# Preview without merging
repokit safe-merge-dev experiment/ml-model --preview
```

### Branch Categories

Default behaviors by branch pattern:
- `prototype/*`, `experiment/*`, `spike/*`: Always squash (development/exploration)
- `feature/*`: Interactive mode (asks whether to squash)
- `bugfix/*`, `hotfix/*`: Preserve full history (important for tracking)

### Configuration

Add to `.repokit.json`:
```json
{
  "history_protection": {
    "branch_rules": {
      "prototype/*": {"action": "squash", "auto": true},
      "feature/*": {"action": "interactive", "auto": false}
    },
    "sensitive_patterns": ["private/", "secret", "TODO: hack"]
  }
}
```

See `configs/history-protection.json` for a complete example.

## History Cleaning

RepoKit includes tools to clean sensitive data from existing repository history using git filter-repo.

### Analyze History

Check your repository for sensitive data before cleaning:

```bash
# Analyze current repository
repokit analyze-history

# Shows: private paths, Windows issues, branch structure
```

### Clean History

Remove sensitive data with pre-built recipes:

```bash
# Remove common private files (private/, CLAUDE.md, logs/, etc.)
repokit clean-history --recipe pre-open-source

# Fix Windows compatibility issues (nul, con, aux files)
repokit clean-history --recipe windows-safe

# Preview changes without modifying repository
repokit clean-history --recipe pre-open-source --dry-run

# Remove specific paths
repokit clean-history --remove-paths private/ secrets/ .env
```

### Safety Features

- **Automatic backup** before any changes
- **Dry-run mode** to preview impact
- **Confirmation prompts** for destructive operations
- **Clear warnings** about history rewriting

### Complete Protection Strategy

1. **Prevention**: Use `safe-merge-dev` for new development
2. **Analysis**: Use `analyze-history` to find issues
3. **Remediation**: Use `clean-history` to fix past problems
4. **Verification**: Re-analyze to confirm cleaning

**Note**: History cleaning requires `git filter-repo`. Install with:
```bash
pip install git-filter-repo
```