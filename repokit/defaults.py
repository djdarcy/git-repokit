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
DEFAULT_SENSITIVE_PATTERNS = [
    "Clipboard Text*",
    "nul",
    "*.tmp",
    "*.log",
    ".env*",
    "*.backup",
    "*.bak"
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

# Default branch configurations
DEFAULT_BRANCH_STRATEGIES = {
    "simple": ["private", "dev", "main"],
    "standard": ["private", "dev", "main", "test", "staging", "live"],
    "gitflow": ["private", "develop", "main"],
    "github-flow": ["private", "main"],
    "minimal": ["main"]
}

# Default directory profiles
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