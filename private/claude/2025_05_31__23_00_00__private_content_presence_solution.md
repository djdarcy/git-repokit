# Private Content Presence Solution - Using THE PROCESS

## Date: 2025-05-31 23:00:00

## 🔁 THE PROCESS - Solving Private Content Availability

### Stage 1: Problem Analysis

**Core Problem**: We need CLAUDE.md and private files to be physically present in ALL branches for AI assistance, but they must NEVER be committed to public branches (dev, main, test, staging, live).

**Sub-problems**:
1. **Working Directory vs Repository**: Files need to exist locally but not in git
2. **Branch Switching**: Files must persist when switching branches
3. **Bidirectional Sync**: Private files created in public branches need to sync to private
4. **User Confusion**: Unclear which files are tracked vs untracked
5. **Git Clean Risk**: `git clean` could delete important private files

**Critical Insight**: Our current approach of removing files is wrong - we need them present but untracked!

### Stage 2: Conceptual Exploration

**Mental Models**:
1. **Ghost Files Model**: Files exist but git doesn't see them (via .gitignore)
2. **Parallel Universe Model**: Private branch is source of truth, other branches get read-only copies
3. **Symlink Model**: Private files live elsewhere, branches have symlinks
4. **Sparse Checkout Model**: Use git's sparse-checkout to control what's in working directory

**Key Realization**: Git has THREE states for files:
1. Tracked and committed
2. Tracked but modified/staged
3. Untracked (ignored or not)

We need private files to be:
- Tracked in private branch
- Untracked (ignored) in all other branches
- But still present in working directory

### Stage 3: Brainstorming Solutions

**Solution 1: Dynamic .gitignore**
- .gitignore changes based on current branch
- Post-checkout hook updates .gitignore
- Private branch: don't ignore private files
- Other branches: ignore private files

Pros:
- Simple concept
- Works with standard git
- No new commands needed

Cons:
- .gitignore changes could be accidentally committed
- Doesn't solve the "files must exist" problem

**Solution 2: Skip-worktree Flag**
- Use `git update-index --skip-worktree` on private files
- Files remain in working directory but git ignores changes
- Different flags per branch

Pros:
- Git native solution
- Files truly invisible to git
- Survives branch switches

Cons:
- Complex to manage
- Can be confusing
- Breaks with some git operations

**Solution 3: Private Overlay System**
- Maintain private/.git-private/ directory (always ignored)
- Post-checkout hook copies files from private/.git-private/ to working locations
- Pre-commit hook syncs changes back

Pros:
- Clear separation
- Easy to understand
- Works with any git operation

Cons:
- Duplicate files
- Sync complexity
- Storage overhead

**Solution 4: Assume-unchanged + Copy-on-checkout**
- In private branch: files are tracked normally
- On checkout to public branch: 
  1. Copy private files to temp location
  2. Checkout (files removed)
  3. Restore files from temp
  4. Mark with --assume-unchanged

Pros:
- No duplicate storage
- Git native features
- Reliable

Cons:
- Complex checkout process
- Need to manage assume-unchanged state

### Stage 4: Synthesis and Recommendation

**Optimal Solution**: Hybrid Approach - "Private File Persistence System"

Combine the best elements:
1. **Track normally in private branch** (source of truth)
2. **Use .gitignore in public branches** (prevent accidental commits)
3. **Post-checkout hook** copies private files from private branch
4. **Pre-commit hook** validates no private files staged
5. **Sync-back command** to update private branch with changes

### Stage 5: Implementation Plan

**Phase 1: Enhanced Hooks (Immediate)**
```python
# post-checkout hook:
1. Detect branch switch
2. If switching TO public branch:
   - Ensure .gitignore includes private patterns
   - Copy private files from private branch to working dir
3. If switching TO private branch:
   - Update .gitignore to NOT ignore private files
   - Copy new private files from working dir to private branch (stage & add them)
   - Files already present from git

# pre-commit hook:
1. If on public branch:
   - Verify no private files staged
   - Check .gitignore is correct
```

**Phase 2: Sync Commands**
```bash
# repokit sync-private
- Copies changes from current branch back to private branch
- Handles new files, modifications, deletions

# repokit check-private
- Shows status of private files across branches
- Identifies out-of-sync files
```

**Phase 3: Recovery System**
```bash
# repokit restore-private
- Restores private files from private branch
- Useful after git clean or accidental deletion
```

## Implementation Details

### Updated .gitignore Strategy

In public branches, .gitignore contains:
```
# RepoKit Private Content (DO NOT REMOVE THESE ENTRIES)
CLAUDE.md
private/claude/
private/docs/
private/notes/
private/temp/
```

In private branch, .gitignore does NOT contain these entries.

### File Persistence Workflow

1. **Developer works in any branch**
   - CLAUDE.md is present for AI assistance
   - private/claude/ logs are available
   - Changes are made

2. **Before commit in public branch**
   - Pre-commit hook blocks private files
   - Developer must sync changes to private branch first

3. **Sync to private branch**
   ```bash
   repokit sync-private
   git checkout private
   git add private/claude/new_log.md
   git commit -m "Add new conversation log"
   git checkout dev  # Files restored automatically
   ```

### Safety Mechanisms

1. **Never lose private content**: Always backed up in private branch
2. **Never commit private content**: Blocked by hooks and .gitignore
3. **Always have AI assistance**: Files present in all branches
4. **Clear status**: Commands show what's tracked where

## Advantages Over Current Approach

1. **No more file removal**: Files stay present for AI
2. **Natural workflow**: Edit anywhere, sync to private
3. **Fail-safe**: Multiple layers prevent accidents
4. **Recoverable**: Can always restore from private branch
5. **Bidirectional**: New private content flows to private branch

## Migration Path

1. First, update hooks to implement new strategy
2. Test in dev branch with copy of private files
3. Implement sync commands
4. Update documentation
5. Roll out via CASCADE protocol