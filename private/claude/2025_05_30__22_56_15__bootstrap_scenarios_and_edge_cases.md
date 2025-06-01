# Universal Bootstrap - Scenarios and Edge Cases
**Date**: 2025-05-30 22:56:15
**Task**: Comprehensive analysis of all scenarios for universal project migration

## Project State Scenarios

### Scenario 1: Empty Directory
```
c:\code\new-project\  (empty)
```
**Actions:**
- Initialize new RepoKit structure
- Apply chosen branch strategy
- Create basic templates for language
- Publish to remote

**Edge Cases:**
- Directory doesn't exist (create it)
- No write permissions
- Directory name conflicts with existing remote repo

### Scenario 2: Directory with Files, No Git
```
c:\code\fancy-tool\
├── main.py
├── requirements.txt
├── README.md
└── src/
    └── utils.py
```
**Actions:**
- Detect language from files
- Initialize Git repository
- Create RepoKit structure around existing files
- Preserve existing files, add templates where missing
- Create branch strategy
- Publish to remote

**Edge Cases:**
- Files conflict with template names (existing .gitignore vs template - merge or favor user's edits)
- Binary files or large assets (recommend lfs, ignore, or alternative storage?)
- Existing config files with different formats
- Sensitive files that shouldn't be committed (interactive, warn, or auto-ignore)

### Scenario 3: Existing Git Repo, Single Branch
```
c:\code\fancy-tool\  (git repo)
├── .git/
├── main.py
├── requirements.txt
└── (committed to master/main)
```
**Actions:**
- Preserve existing Git history
- Rename branch if needed for strategy
- Create additional branches per strategy
- Add RepoKit structure around existing
- Merge/integrate templates
- Update remote or create new one

**Edge Cases:**
- Branch name conflicts (user has 'staging' but different purpose - interactive rename or warn or let user issue command?)
- Uncommitted changes
- Existing remote origin
- Protected branches
- Large history size

### Scenario 4: Complex Git Repo, Multiple Branches
```
c:\code\fancy-tool\  (git repo)
├── .git/
├── main.py
├── requirements.txt
└── (branches: master, develop, feature/x, hotfix/y)
```
**Actions:**
- Analyze existing branch strategy
- Map to RepoKit strategy or warn about conflicts
- Preserve important branches
- Create missing branches for strategy
- Set up worktrees appropriately

**Edge Cases:**
- Conflicting branch strategies
- Orphaned branches
- Merge conflicts between branches
- Existing branch protection rules
- Submodules

### Scenario 5: Existing Remote Repository
```
c:\code\fancy-tool\  (git repo with origin)
├── .git/
├── main.py
└── (origin: https://github.com/user/old-repo)
```
**Actions:**
- Choose: migrate to new repo or update existing
- Handle existing GitHub/GitLab settings
- Preserve issues, PRs, etc. (manual migration)
- Update remote URL or create new remote

**Edge Cases:**
- Repository already has same name on target service
- Different authentication for old vs new remote
- Repository has collaborators
- Repository has CI/CD configured
- Repository has security settings

## Branch Strategy Scenarios

### Standard Strategy Migration
```
Source: master
Target: private → dev → main → test → staging → live
```
**Actions:**
- Create all required branches
- Set up worktrees for main and dev
- Preserve source content in all branches initially
- Set up proper merge flow

**Edge Cases:**
- Source already has conflicting branch names
- Different branch protection requirements

### Simple Strategy Migration  
```
Source: master, develop
Target: main, dev
```
**Actions:**
- Map existing branches
- Create worktrees
- Simpler structure

**Edge Cases:**
- Source has more branches than target supports

### GitFlow Strategy Migration
```
Source: any
Target: main, develop, feature/*, release/*, hotfix/*
```
**Actions:**
- Set up GitFlow structure
- Map existing branches to GitFlow model
- Create branch prefixes and rules

**Edge Cases:**
- Existing branches don't fit GitFlow model
- Conflicts with GitFlow naming conventions

## Language-Specific Scenarios

### Python Project
```
├── setup.py or pyproject.toml
├── requirements.txt
├── src/ or package/
└── tests/
```
**Actions:**
- Detect Python package structure
- Apply Python templates
- Set up Python-specific commands in CLAUDE.md
- Handle virtual environments

**Edge Cases:**
- Multiple Python versions
- Complex dependency management (pipenv, poetry, conda)
- Existing packaging configuration conflicts

### JavaScript/Node Project
```
├── package.json
├── node_modules/
├── src/
└── dist/
```
**Actions:**
- Detect Node.js project
- Apply JavaScript templates
- Handle npm/yarn differences
- Set up appropriate build commands

**Edge Cases:**
- Multiple package.json files (monorepo)
- Different package managers
- Complex build pipelines

### Generic/Unknown Project
```
├── misc files
└── unknown structure
```
**Actions:**
- Apply generic templates
- Prompt user for language/type
- Minimal assumptions
- Let user customize post-migration

**Edge Cases:**
- Mixed language projects
- Non-standard project structures
- Legacy or deprecated technologies

## Remote Service Scenarios

### GitHub Migration
**Actions:**
- Create repository via GitHub API
- Set repository settings (private/public, description)
- Push all branches
- Set default branch
- Configure branch protection if requested

**Edge Cases:**
- Name already taken
- Organization permissions
- API rate limits
- Two-factor authentication
- Enterprise GitHub

### GitLab Migration
**Actions:**
- Create project via GitLab API  
- Configure project settings
- Handle groups/namespaces
- Set up CI/CD templates

**Edge Cases:**
- GitLab.com vs self-hosted
- Different API versions
- Group permissions
- GitLab-specific features

### Multiple Remotes
**Actions:**
- Support multiple remote targets
- Different branch strategies per remote
- Synchronization strategies

**Edge Cases:**
- Conflicting remote requirements
- Authentication for multiple services
- Different branch policies per remote

## Authentication Scenarios

### Token-Based Auth
**Actions:**
- Support GitHub tokens, GitLab tokens
- Secure token storage
- Token validation before operations

**Edge Cases:**
- Expired tokens
- Insufficient permissions
- Token scopes don't match requirements

### SSH-Based Auth
**Actions:**
- Detect SSH key configuration
- Use SSH remotes where appropriate
- Validate SSH connectivity

**Edge Cases:**
- SSH keys not configured
- SSH agent not running
- Firewall blocking SSH

### Multi-Factor Authentication
**Actions:**
- Handle 2FA requirements
- Guide user through auth flow
- Cache authentication where possible

**Edge Cases:**
- 2FA token expires during operation
- Different 2FA methods per service
- Organization-required 2FA

## Data Preservation Scenarios

### Git History Preservation
**Actions:**
- Maintain commit history across migration
- Preserve author information
- Keep branch relationships

**Edge Cases:**
- Very large repositories
- Corrupted history
- Binary files in history
- Sensitive data in history

### File Preservation vs Template Override
**Actions:**
- Smart merging of existing files with templates
- Backup original files before modification
- Allow user to choose preservation strategy

**Edge Cases:**
- Existing files have same name as templates
- Files contain custom configuration
- Files are generated/derived

### Metadata Preservation
**Actions:**
- Preserve file timestamps where meaningful
- Maintain file permissions
- Keep custom Git attributes

**Edge Cases:**
- Cross-platform permission differences
- Symbolic links
- File attributes not supported on target system

## Error Recovery Scenarios

### Partial Migration Failure
**Actions:**
- Rollback capability
- Resume from checkpoint
- Clear error reporting

**Edge Cases:**
- Network failure during remote operations
- Disk space exhaustion
- Permission changes during operation

### Conflict Resolution
**Actions:**
- Interactive conflict resolution
- Automated resolution strategies
- Manual override options

**Edge Cases:**
- Multiple simultaneous conflicts
- Circular dependencies
- Unresolvable conflicts requiring user decision

## Performance Scenarios

### Large Repository Migration
**Actions:**
- Progress reporting
- Streaming operations
- Memory management

**Edge Cases:**
- Multi-gigabyte repositories
- Thousands of files
- Complex branch structures
- Network bandwidth limitations

### Concurrent Operations
**Actions:**
- Handle multiple simultaneous migrations
- Lock files to prevent conflicts
- Resource management

**Edge Cases:**
- Concurrent access to same source directory
- System resource exhaustion
- Process interruption