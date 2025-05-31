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

### Merge Strategy Guidelines

When merging branches, use the following flags to maintain clear history and verify changes:

- **Always use `--no-ff`** (no fast-forward): Preserves merge commit history to track where changes originated
- **Use `--no-commit`** when appropriate: Allows review of changes before finalizing the merge
- This strategy helps:
  - Track the source of all changes
  - Review merge results before committing
  - Avoid complicated reverts by catching issues early
  - Maintain a clear project history

Example:
```bash
git merge dev --no-ff --no-commit
# Review changes with git status and git diff
git commit -m "Descriptive merge message"
```

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