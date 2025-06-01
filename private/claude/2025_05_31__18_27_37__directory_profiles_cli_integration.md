# Directory Profiles CLI Integration - Development Plan

## Overview
This document outlines the development work to:
1. Fully integrate DirectoryProfileManager into RepoKit's workflow
2. Expose directory profiles through CLI arguments
3. Improve CLI help documentation with detailed subcommands
4. Create example config files for user reference

## The Dev Workflow Process

### 🔁 Stage 1: Problem Analysis

**Core Problem**: DirectoryProfileManager exists but isn't integrated into the main workflow. Users can only specify directories via comma-separated lists, not profiles.

**Sub-problems**:
1. **Integration Gap**: DirectoryProfileManager is implemented but not connected to repo_manager.py
2. **CLI Limitations**: No way to specify profiles via CLI (only explicit directory lists)
3. **Documentation Gap**: Help pages lack detailed information about subcommands and usage recipes
4. **Config Examples**: No reference config files for users to understand options

**Dimensions to Consider**:
- **User Experience**: Users must manually list directories instead of using convenient profiles
- **Maintainability**: Hardcoded directory lists in multiple places vs centralized profiles
- **Flexibility**: Can't mix profiles with custom additions easily
- **Discovery**: Users don't know about available options without external docs

**Short-term vs Long-term**:
- Short-term: Users struggle to understand directory options
- Long-term: Technical debt from duplicated directory definitions

### 🔁 Stage 2: Conceptual Exploration

**Why the problem exists**:
- DirectoryProfileManager appears to be a planned feature that wasn't fully implemented
- Development may have prioritized MVP functionality over profile system
- The simple list approach was "good enough" for initial release

**Mental Models**:
- Think of profiles like IDE workspace templates - predefined configurations for common use cases
- Similar to how branch strategies work (standard, gitflow, etc.)

**Relationships**:
- Directory profiles parallel branch strategies conceptually
- Both provide predefined configurations for common patterns
- Config system already supports hierarchical merging

### 🔁 Stage 3: Brainstorming Solutions

#### Solution 1: Full Profile Integration
**Approach**: Integrate DirectoryProfileManager throughout the stack
- Add `--dir-profile` CLI argument
- Modify repo_manager to use DirectoryProfileManager
- Allow combining profiles with custom directories

**Pros**:
- Clean, consistent implementation
- Leverages existing DirectoryProfileManager code
- Extensible for future profile additions

**Cons**:
- More extensive changes required
- Need to handle profile + custom directory merging

**Edge Cases**:
- What if user specifies both profile and explicit directories?
- How to handle unknown profile names?

#### Solution 2: Simple Profile Mapping
**Approach**: Add profile support without DirectoryProfileManager
- Map profile names to directory lists in CLI
- Keep current repo_manager implementation

**Pros**:
- Minimal changes to existing code
- Quick to implement

**Cons**:
- Duplicates profile definitions
- Doesn't leverage existing DirectoryProfileManager
- Technical debt

#### Solution 3: Hybrid Approach
**Approach**: Use DirectoryProfileManager in config layer
- Add profile support to ConfigManager
- Translate profiles to directory lists before repo_manager

**Pros**:
- Incremental migration path
- Doesn't break existing code
- Can enhance later

**Cons**:
- Partial use of DirectoryProfileManager capabilities
- Some feature loss (groups, private sets)

#### Solution 4: Complete Redesign
**Approach**: Refactor directory handling entirely
- Make DirectoryProfileManager the primary interface
- Deprecate direct directory lists
- Full feature implementation

**Pros**:
- Most feature-rich
- Best long-term design

**Cons**:
- Breaking changes
- Extensive refactoring
- Risk to stability

### 🔁 Stage 4: Synthesis and Recommendation

**Recommended Solution**: Solution 1 - Full Profile Integration

**Reasoning**:
- Leverages existing code that's already been written
- Provides best user experience
- Maintains backward compatibility
- Sets foundation for future enhancements

**Key Design Decisions**:
1. Add `--dir-profile` argument (minimal, standard, complete, custom)
2. Support `--dir-groups` for group-based selection
3. Allow `--directories` to add/override specific directories
4. Profile → Groups → Explicit directories (in that precedence)

**CLI Examples**:
```bash
# Use standard profile
repokit create myproject --dir-profile standard

# Use complete profile with additional directories
repokit create myproject --dir-profile complete --directories "data,analysis"

# Use groups
repokit create myproject --dir-groups "development,documentation"
```

### 🔁 Stage 5: Implementation Plan

#### Phase 1: CLI Enhancement (Est: 2 hours)
1. Restructure argparse with subparsers for each command
2. Add detailed help text with examples and recipes
3. Add directory profile arguments:
   - `--dir-profile` (choice: minimal, standard, complete)
   - `--dir-groups` (comma-separated groups)
   - `--private-set` (standard, enhanced)
4. Document all edge cases in help text

#### Phase 2: Config Integration (Est: 1 hour)
1. Add DirectoryProfileManager to ConfigManager
2. Handle profile → directory list conversion
3. Support merging profiles with explicit directories
4. Add profile info to config validation

#### Phase 3: RepoManager Integration (Est: 1 hour)
1. Inject DirectoryProfileManager into RepoManager
2. Replace hardcoded directory creation with profile manager
3. Maintain backward compatibility for direct directory lists
4. Update logging for profile usage

#### Phase 4: Documentation (Est: 2 hours)
1. Create example config files in `configs/` directory:
   - `configs/minimal-python.json`
   - `configs/standard-web.json`
   - `configs/complete-enterprise.json`
   - `configs/custom-ml-project.json`
2. Add recipes to help text for common scenarios
3. Document profile system in help pages

#### Phase 5: Testing (Est: 1 hour)
1. Test profile selection via CLI
2. Test profile + explicit directory merging
3. Test backward compatibility
4. Test edge cases (invalid profiles, conflicts)

**Total Estimated Time**: 7 hours

**Milestones**:
- [ ] CLI accepts profile arguments
- [ ] Profiles create correct directories
- [ ] Help shows detailed documentation
- [ ] Example configs created
- [ ] All tests passing

**Success Criteria**:
- Users can specify directory profiles via CLI
- Help pages provide sufficient detail without external docs
- Example configs demonstrate various use cases
- Backward compatibility maintained

## Next Steps

1. Create detailed help structure with subparsers
2. Implement profile arguments in CLI
3. Wire up DirectoryProfileManager through the stack
4. Create comprehensive example configurations
5. Test thoroughly with various scenarios

## Commands and Implementation Notes

### Current Directory Creation Flow:
```
CLI (--directories) → args_to_config() → ConfigManager → RepoManager._create_directory_structure()
```

### New Directory Creation Flow:
```
CLI (--dir-profile/--dir-groups/--directories) → args_to_config() → ConfigManager w/DirectoryProfileManager → RepoManager._create_directory_structure()
```

### Key Files to Modify:
1. `repokit/cli.py` - Add arguments, restructure help
2. `repokit/config.py` - Integrate DirectoryProfileManager
3. `repokit/repo_manager.py` - Use profile manager
4. `configs/` - New directory with examples

## Implementation Summary

### Completed Tasks:

1. **CLI Restructuring** ✓
   - Converted to subparser architecture with detailed help for each command
   - Added comprehensive descriptions, examples, and recipes
   - Improved user experience with man-page-like documentation

2. **Directory Profile Arguments** ✓
   - Added `--dir-profile` (minimal, standard, complete)
   - Added `--dir-groups` for group-based directory selection
   - Added `--private-set` for private directory configuration
   - Maintained backward compatibility with `--directories`

3. **ConfigManager Integration** ✓
   - Integrated DirectoryProfileManager into ConfigManager
   - Added resolve_directory_profiles() method
   - Fixed bug where profiles were adding to defaults instead of replacing
   - Proper merging of profiles, groups, and explicit directories

4. **RepoManager Updates** ✓
   - Already used config directories, so minimal changes needed
   - Fixed duplicate gitignore entries for private directories
   - Now properly uses resolved directories from ConfigManager

5. **Example Configurations** ✓
   - Created `configs/` directory with 5 examples:
     - minimal-python.json - Basic Python setup
     - standard-web.json - Web application setup
     - complete-enterprise.json - Full enterprise configuration
     - custom-ml-project.json - Machine learning project
     - README.md - Comprehensive documentation

6. **Testing** ✓
   - Verified minimal profile creates only 3 directories
   - Tested profile + additional directories combination
   - Confirmed backward compatibility
   - Fixed discovered bugs during testing

### Key Achievements:

- **Full CLI-Config Parity**: Everything configurable in config files is now accessible via CLI
- **Improved Documentation**: Users can understand all features without external docs
- **Flexible Directory Management**: Profiles, groups, and explicit directories can be combined
- **Backward Compatibility**: Existing workflows continue to work unchanged
- **Better User Experience**: Clear help text with examples and recipes

### Usage Examples:

```bash
# Minimal Python project
repokit create myapp --dir-profile minimal --language python

# Standard web project with extras
repokit create webapp --dir-profile standard --directories "public,static"

# Using directory groups
repokit create devtool --dir-groups "development,operations"

# Complete enterprise setup
repokit create enterprise --config configs/complete-enterprise.json
```