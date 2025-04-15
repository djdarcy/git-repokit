# RepoKit Migration Guide

This guide explains how to migrate existing projects to the RepoKit structure.

## Overview

RepoKit now includes tools to help you convert existing directories into properly structured repositories. This is useful when:

- You have existing code that you want to organize according to RepoKit's standardized structure
- You want to add RepoKit's branching strategy to an existing project
- You need to publish an existing project to GitHub or GitLab with proper configuration

## Migration Process

The migration process consists of two main steps:

1. **Analysis**: RepoKit analyzes your directory to understand its structure and contents
2. **Migration**: RepoKit adapts your directory to the RepoKit structure, preserving your files

## Migration Commands

### Analyzing a Directory

To analyze a directory without making any changes:

```bash
repokit analyze /path/to/your/project
```

This shows:
- Standard directories that exist or are missing
- Special directories (.git, .github, .vscode)
- Potential template conflicts
- A breakdown of file types
- The suggested primary language

### Migrating a Directory

To migrate a directory to the RepoKit structure:

```bash
repokit migrate /path/to/your/project
```

By default, this uses the "safe" strategy, which:
- Creates missing standard directories
- Backs up any existing template files that would conflict
- Preserves existing special directories

### Migration Strategies

You can control how RepoKit handles existing files with different strategies:

```bash
# Safe strategy (default): backup existing files, keep special directories
repokit migrate /path/to/your/project --migration-strategy safe

# Replace strategy: replace existing files with RepoKit templates
repokit migrate /path/to/your/project --migration-strategy replace

# Merge strategy: attempt to intelligently merge existing files with templates
repokit migrate /path/to/your/project --migration-strategy merge
```

### Dry Run

If you want to see what would happen during migration without making any changes:

```bash
repokit migrate /path/to/your/project --dry-run
```

## Working with Existing Git Repositories

When migrating a directory that already contains a `.git` repository:

### Safe Strategy (Default)
- Keeps the existing repository intact
- Adds new directories according to the RepoKit structure
- Creates backups of any conflicting files

### Replace Strategy
- Replaces existing configuration files with RepoKit templates
- Keeps the existing `.git` directory and history
- Adds new directories according to the RepoKit structure

### Merge Strategy
- Attempts to merge existing configuration with RepoKit templates
- Keeps the existing `.git` directory and history
- Adds new directories according to the RepoKit structure

## Example: Migrating and Publishing

A common workflow is to migrate an existing project and then publish it:

```bash
# First analyze the project
repokit analyze my-project

# Migrate the project
repokit migrate my-project

# Publish to GitHub
repokit publish my-project --publish-to github
```

## Next Steps After Migration

After migrating a project:

1. Review the changes made to ensure everything is as expected
2. Check any backup files created during migration
3. Test that the repository still works correctly
4. If you're using Git worktrees, set them up with:
   ```bash
   git worktree add ../github main
   git worktree add ../dev dev
   ```
5. Configure any additional branches or worktrees as needed

## Troubleshooting

### Template Conflicts

If you see template conflicts during analysis:
- These are files that exist both in your project and in RepoKit's templates
- The migration strategy determines how these are handled

### Git Repository Issues

If you encounter issues with an existing Git repository:
- Consider creating a backup before migration
- Use `--dry-run` to see potential changes without executing them
- Consider using the "safe" strategy which keeps your existing Git repository intact

### Multiple Migration Passes

You can run the migration command multiple times with different strategies:
- First with `--dry-run` to see what would change
- Then with `--migration-strategy safe` to make minimal changes
- Finally with `--migration-strategy merge` to integrate RepoKit templates

## Advanced Usage

### Customizing Templates Before Migration

You can customize RepoKit's templates before migration:
1. Run `repokit init-config` to create a config file
2. Modify the templates in the RepoKit templates directory
3. Run the migration with your customized templates

### Language-Specific Migration

RepoKit will attempt to detect the primary language of your project:

```bash
# Let RepoKit auto-detect the language
repokit migrate my-project

# Or specify the language explicitly
repokit migrate my-project --language javascript
```
