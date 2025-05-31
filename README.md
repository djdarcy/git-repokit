# RepoKit

RepoKit is a tool for creating standardized Git repositories with complex branching strategies and worktree-based workflows. It automates the setup of consistent repository structures, branch configurations, and GitHub integration.

## Features

- **Standardized Repository Structure**: Creates a consistent directory layout with standard folders
- **Multi-Branch Strategy**: Automatically sets up main, dev, staging, test, live, and private branches
- **Worktree Management**: Creates Git worktrees for efficient branch isolation
- **Private Content Protection**: Prevents private content from being committed/pushed
- **GitHub Integration**: Generates standard GitHub files (.github directory with workflows, issue templates)
- **Template Customization**: Supports language-specific templates (Python, JavaScript, etc.)
- **Configuration System**: Flexible configuration through JSON files and command-line options

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/repokit.git
cd repokit

# Install as a development package
pip install -e .
```

## Basic Usage

```bash
# Create a new repository
repokit create my-project --language python

# List available templates
repokit list-templates

# Initialize a configuration file
repokit init-config
```

## Advanced Usage

### Command-Line Options

```bash
# Specify Git user information
repokit create my-project --user-name "Your Name" --user-email "your.email@example.com"

# Customize branches and worktrees
repokit create my-project --branches main,dev,prod --worktrees main,dev

# Customize directories
repokit create my-project --directories docs,src,tests,scripts

# Use a configuration file
repokit create my-project --config my-config.json

# Increase verbosity for debugging
repokit create my-project -vvv
```

### Configuration File

Create a JSON configuration file (`.repokit.json`):

```json
{
  "name": "my-project",
  "description": "A new project repository",
  "language": "python",
  "branches": ["main", "dev", "staging", "test", "live"],
  "worktrees": ["main", "dev"],
  "directories": [
    "convos", "docs", "logs", "private", "revisions", "scripts", "tests"
  ],
  "private_dirs": ["private", "convos", "logs"],
  "private_branch": "private",
  "github": true,
  "user": {
    "name": "Your Name",
    "email": "your.email@example.com"
  }
}
```

## Directory Structure

RepoKit creates repositories with the following structure:

```
my-project/
├── local/          # Main repository (private branch)
│   ├── .git/       # Git repository data
│   ├── .github/    # GitHub configuration
│   ├── convos/     # Private conversations (not committed)
│   ├── docs/       # Documentation
│   ├── logs/       # Local logs (not committed)
│   ├── private/    # Private files (not committed)
│   ├── revisions/  # Revision history
│   ├── scripts/    # Utility scripts
│   └── tests/      # Test files
├── github/         # GitHub worktree (main branch)
├── main/           # Main branch worktree (optional)
├── dev/            # Dev branch worktree
└── ... other worktrees for feature branches
```

## Customizing Templates

RepoKit uses templates for generating repository files. You can use custom templates by specifying a templates directory:

```bash
repokit create my-project --templates-dir /path/to/templates
```

The templates directory should have the following structure:

```
templates/
├── common/
│   ├── README.md.template
│   ├── CONTRIBUTING.md.template
│   ├── gitignore.template
│   └── launch.json.template
├── github/
│   ├── CODEOWNERS.template
│   ├── workflows/
│   │   └── main.yml.template
│   └── ISSUE_TEMPLATE/
│       ├── bug-report.md.template
│       └── feature-request.md.template
├── languages/
│   ├── python/
│   │   ├── setup.py.template
│   │   └── requirements.txt.template
│   └── javascript/
│       └── package.json.template
└── hooks/
    └── pre-commit.template
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
