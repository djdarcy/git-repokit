# Directory Profiles and CLI Enhancement - Session Recovery Log

## Session Context and Objectives

This session focused on implementing a comprehensive directory profile system for RepoKit and enhancing the CLI with detailed help documentation. The user identified that while `DirectoryProfileManager` existed in the codebase, it wasn't integrated into the main workflow, and the CLI lacked detailed help similar to man pages.

## Key Requirements Identified

1. **Directory Profile Integration**: Make `DirectoryProfileManager` functional and accessible via CLI
2. **CLI Documentation Enhancement**: Restructure argparse to provide man-page-like help with recipes
3. **Config Examples**: Create reference configurations in a `configs/` directory  
4. **CLI-Config Parity**: Ensure everything configurable in config files is accessible via CLI
5. **Test Management**: Standardize test script locations and update documentation

## Implementation Details

### 1. CLI Restructuring (COMPLETED)

**File Modified**: `/mnt/c/code/git-repokit/repokit/cli.py`

Major changes:
- Converted from flat argument parser to subparser architecture
- Added `ArgumentParser` with `prog="repokit"` and comprehensive description
- Created subparsers for each command: create, analyze, migrate, adopt, publish, bootstrap, etc.
- Each subparser includes:
  - Detailed description with formatting
  - Examples section with practical use cases
  - Recipe section for common scenarios
  - `formatter_class=argparse.RawDescriptionHelpFormatter` for proper formatting

Key additions to create command:
```python
# Directory Configuration argument group
dir_group = create_parser.add_argument_group("Directory Configuration")
dir_group.add_argument("--dir-profile", choices=["minimal", "standard", "complete"])
dir_group.add_argument("--dir-groups", help="Comma-separated list of directory groups")
dir_group.add_argument("--directories", "-dir", help="Additional directories")
dir_group.add_argument("--private-dirs", "-pd", help="Directories to mark as private")
dir_group.add_argument("--private-set", choices=["standard", "enhanced"], default="standard")
```

Also updated `args_to_config()` to use `getattr()` for safer attribute access and handle new arguments.

### 2. DirectoryProfileManager Integration (COMPLETED)

**Files Modified**:
- `/mnt/c/code/git-repokit/repokit/config.py`
- `/mnt/c/code/git-repokit/repokit/repo_manager.py`

ConfigManager changes:
- Added `from .directory_profiles import DirectoryProfileManager`
- Added `self.directory_manager = DirectoryProfileManager(verbose=verbose)` in `__init__`
- Created `resolve_directory_profiles()` method to convert profiles to directory lists
- Called `resolve_directory_profiles()` in `set_cli_config()`

**Critical Bug Fixed**: In `resolve_directory_profiles()`, discovered that when using a profile, it was ADDING to the default directories instead of REPLACING them. Fixed by checking if directories come from CLI config vs defaults:

```python
# Bug was here - it was adding ALL config directories
if "directories" in self.config:
    existing_dirs = set(directories)
    for d in self.config["directories"]:
        if d not in existing_dirs:
            directories.append(d)

# Fixed to only add CLI-specified directories
if "directories" in self.cli_config:  # Changed from self.config
    existing_dirs = set(directories)
    for d in self.cli_config["directories"]:
        if d not in existing_dirs:
            directories.append(d)
```

RepoManager changes:
- Fixed duplicate .gitignore entries by checking existing content before appending
- Now reads .gitignore first and only adds entries that don't exist

### 3. Example Configurations (COMPLETED)

Created `/mnt/c/code/git-repokit/configs/` directory with:

1. **minimal-python.json** - Basic Python project with minimal profile
2. **standard-web.json** - Web application with custom directories
3. **complete-enterprise.json** - Full enterprise setup with custom profiles
4. **custom-ml-project.json** - Machine learning project with specialized directories
5. **README.md** - Comprehensive documentation of all options

Each config demonstrates different features:
- Directory profiles and groups
- Custom directory additions
- Branch strategies and flow
- Private directory sets
- Custom type mappings

### 4. Test Development (COMPLETED)

**Created Tests**:
- `/mnt/c/code/git-repokit/tests/test_directory_profiles.py` - Comprehensive unit tests
- `/mnt/c/code/git-repokit/tests/one-offs/test_directory_profiles_manual.py` - Manual test runner
- `/mnt/c/code/git-repokit/tests/one-offs/check_imports.py` - Import verification script

**Updated Documentation**:
- Added test guidelines to `/mnt/c/code/git-repokit/CLAUDE.md`
- Updated `/mnt/c/code/git-repokit/repokit/templates/ai/claude/CLAUDE.md.template`
- Standardized on `test_runs/` directory (not test-runs)
- Keep one-off scripts in `tests/one-offs/`

### 5. CHANGELOG Updates (COMPLETED)

Added new [Unreleased] section documenting:
- Directory Profile System features
- Enhanced CLI Documentation
- Configuration Examples
- Test Development Guidelines
- Bug fixes and changes

## Testing and Validation

### Manual Testing Performed

1. **Minimal Profile Test**:
```bash
cd test_runs && python3 -m repokit -v create test-minimal --dir-profile minimal
```
Result: Initially created 8 directories (bug), after fix created 3 directories ✓

2. **Config File Test**:
```bash
python3 -m repokit --config configs/minimal-python.json -v create test-runs/test-config
```
Result: Successfully used config file ✓

3. **Profile + Additional Directories**:
```bash
python3 -m repokit -v create test-runs/test-minimal-plus --dir-profile minimal --directories "data,models"
```
Result: Created 5 directories (3 from minimal + 2 additional) ✓

## Issues Encountered

### Python/Git Command Failures

Starting around 19:06, all Python and Git commands began failing with generic "Error" messages:
- `python3 --version` → Error
- `python --version` → Error  
- `git status` → Error
- `which python python3` → Error
- Even simple commands like `pwd` → Error

This prevented:
- Running the new unit tests
- Running existing test suite
- Checking git status
- Making commits
- Performing the merge workflow

### Workarounds Attempted

1. Created manual test scripts that could be run later
2. Used LS tool instead of bash ls commands
3. Documented all changes thoroughly for session recovery
4. Prepared complete git workflow instructions for manual execution

## Current State

### Completed Work
- ✅ CLI fully restructured with subparsers and detailed help
- ✅ Directory profiles fully integrated into ConfigManager
- ✅ All CLI arguments for profiles implemented
- ✅ Bug fixes for profile resolution and .gitignore duplication
- ✅ Example configurations created with documentation
- ✅ Comprehensive unit tests written
- ✅ CHANGELOG.md updated
- ✅ Test guidelines added to documentation

### Pending Work (Due to Tool Issues)
- ⏳ Run new unit tests to verify implementation
- ⏳ Run existing test suite to ensure no regressions
- ⏳ Commit changes to private branch
- ⏳ Merge through branch hierarchy (dev → main → test → staging → live)
- ⏳ Push to remote (dev, main, test, staging)

## Git Workflow to Execute

When tools are working again, execute:

1. **Commit to private**:
```bash
git add -A
git commit -m "feature(cli): add directory profiles and enhanced help system

- Add directory profile system with --dir-profile, --dir-groups, --private-set
- Restructure CLI with subparsers for detailed command-specific help  
- Create example configurations in configs/ directory
- Fix duplicate .gitignore entries for private directories
- Add comprehensive unit tests for directory profiles
- Update CLAUDE.md with test development guidelines"
```

2. **Test the implementation**:
```bash
# Run new tests
python3 tests/test_directory_profiles.py -v

# Run existing unit tests
python3 tests/run_tests.py --unit

# Test CLI manually
python3 -m repokit create --help
python3 -m repokit -v create test_runs/test-profile --dir-profile minimal
```

3. **Merge to dev**:
```bash
git checkout dev
git merge private --no-ff --no-commit
# Review with git status and git diff
git commit -m "merge: bring directory profiles and CLI enhancements to dev

Adds comprehensive directory profile system and improved CLI documentation
from private branch development."
```

4. **Continue merge cascade** through main, test, staging, live

5. **Push to remote** (excluding private and live)

## Future Enhancements to Consider

1. **Custom Profile Definition via CLI**: Allow users to define profiles on the fly
2. **Profile Inheritance**: Allow profiles to extend other profiles
3. **Interactive Mode**: Add `--interactive` to guide users through options
4. **Profile Validation**: Validate custom profiles in config files
5. **Directory Templates**: Associate templates with specific directories
6. **Profile Export**: Command to export current directory structure as a profile

## Key Implementation Details to Remember

1. **Profile Resolution Order**: Profile → Groups → Explicit directories
2. **Private Directory Handling**: Resolved separately and managed by private_set
3. **Source Directory Mapping**: "src" becomes package name when specified
4. **Backward Compatibility**: No profile = use default directory list
5. **Config Hierarchy**: CLI args override everything else

## Test Coverage Areas

The new test file covers:
- Default profile loading
- Profile directory resolution  
- Group-based directory selection
- Private directory sets
- Directory name mapping
- Config file loading/saving
- Directory validation
- Profile suggestion
- ConfigManager integration
- Backward compatibility

## Final Notes

This implementation provides a flexible, user-friendly system for managing directory structures in RepoKit. The enhanced CLI documentation makes the tool self-documenting, reducing the need for external documentation. The directory profile system allows for quick project setup while maintaining flexibility for custom configurations.

The session was productive despite tool failures at the end. All code changes are complete and ready for testing once the environment is restored.