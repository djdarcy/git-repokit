#!/usr/bin/env python3
"""
Default configuration values for RepoKit.

This module provides centralized default values to prevent duplication
and ensure consistency across the codebase.
"""

# Default private directories that should not appear in public branches
DEFAULT_PRIVATE_DIRS = [
    "private",
    "revisions", 
    "logs",
    "convos"
]

# Default sensitive files that should not appear in public branches
DEFAULT_SENSITIVE_FILES = [
    "CLAUDE.md",
    ".repokit.json"
]

# Default sensitive file patterns (supports glob patterns)
# Cross-platform compatible patterns using Python's fnmatch/pathlib
DEFAULT_SENSITIVE_PATTERNS = [
    "Clipboard Text*",
    "nul",           # Windows reserved name
    "*.tmp",
    "*.log", 
    ".env*",
    "*.backup",
    "*.bak",
    "*.*~",          # Vim backup files (primary pattern for files like listall.cmd~)
    "*~",            # Vim backup files (fallback for single extension)
    "logs/*",        # All files in logs directory
    "logs/**/*",     # All files in logs subdirectories  
    "revisions/*",   # All files in revisions directory
    "revisions/**/*", # All files in revisions subdirectories
]

# Default branch configurations for BranchContext
DEFAULT_PRIVATE_BRANCHES = [
    "private",
    "local"
]

DEFAULT_PUBLIC_BRANCHES = [
    "main", 
    "master", 
    "dev", 
    "test", 
    "staging", 
    "live", 
    "prod", 
    "production"
]

# Files/directories that should only exist in private branches
DEFAULT_PRIVATE_PATTERNS = [
    "CLAUDE.md",
    "private/",
    "convos/",
    "logs/",
    "credentials/",
    "secrets/",
    ".env.local",
    ".env.private",
    "**/__private__*",
    "**/private_*",
    "*~",  # Vim backup files
    "*.*~",  # Vim backup files (multiple extensions)
]

# Files that should be excluded from public branches during merges
DEFAULT_EXCLUDE_FROM_PUBLIC = [
    "CLAUDE.md",
    "private/claude/",
    "private/docs/",
    "private/notes/",
    "private/temp/",
    "revisions/",
    "test-runs/",
    "test_runs/",
]

# Branch-specific excludes - files that should only exist in certain branches
BRANCH_SPECIFIC_EXCLUDES = {
    "private": [],  # Private branch can contain everything
    "dev": DEFAULT_PRIVATE_DIRS + DEFAULT_SENSITIVE_FILES,
    "main": DEFAULT_PRIVATE_DIRS + DEFAULT_SENSITIVE_FILES,
    "staging": DEFAULT_PRIVATE_DIRS + DEFAULT_SENSITIVE_FILES,
    "test": DEFAULT_PRIVATE_DIRS + DEFAULT_SENSITIVE_FILES,
    "live": DEFAULT_PRIVATE_DIRS + DEFAULT_SENSITIVE_FILES,
}

# Default branch configurations - centralized from directory_analyzer.py
DEFAULT_BRANCH_STRATEGIES = {
    "simple": ["private", "dev", "main"],
    "standard": ["private", "dev", "main", "test", "staging", "live"],
    "gitflow": ["private", "develop", "main"],
    "github-flow": ["private", "main"],
    "minimal": ["main"]
}

# Default directory profiles - centralized from directory_profiles.py
DEFAULT_DIRECTORY_PROFILES = {
    "minimal": ["src", "tests", "docs"],
    "standard": [
        "src", "tests", "docs", "scripts", "config", 
        "logs", "private", "convos", "revisions"
    ],
    "complete": [
        "src", "tests", "docs", "scripts", "config", "logs", 
        "private", "convos", "revisions", "data", "examples", 
        "tools", "resources", "assets"
    ]
}

# Directory groups by purpose - centralized from directory_profiles.py
DEFAULT_DIRECTORY_GROUPS = {
    "development": ["src", "tests", "scripts", "tools"],
    "documentation": ["docs", "examples", "resources"],
    "operations": ["config", "logs", "data"],
    "privacy": ["private", "convos", "credentials"],
}

# Directory type mapping (conceptual → actual name) - from directory_profiles.py
DEFAULT_DIRECTORY_TYPE_MAPPING = {
    "src": "src",  # Will be customized for each project (e.g., "repokit")
    "tests": "tests",
    "docs": "docs",
    "config": "config",
    "scripts": "scripts",
    "private": "private",
    "convos": "convos",
    "logs": "logs",
}

# Enhanced private directory sets - from directory_profiles.py
DEFAULT_PRIVATE_DIR_SETS = {
    "standard": DEFAULT_PRIVATE_DIRS.copy(),
    "enhanced": DEFAULT_PRIVATE_DIRS + ["credentials", "secrets", "local"],
}