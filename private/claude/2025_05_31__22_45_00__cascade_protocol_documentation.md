# CASCADE Protocol - Cascading Branch Update Strategy

## Date: 2025-05-31 22:45:00

## Overview

The CASCADE Protocol (Cascading Automated Sync for Continuous And Dependable Evolution) is RepoKit's systematic approach to propagating changes through the branch hierarchy while maintaining branch integrity and preventing private content leakage.

## The CASCADE Flow

```
private → dev → main → test → staging → live
         ↑_______________________________|
                  (fix cascade back)
```

## Protocol Steps

### 1. Initial Development (private branch)
- Develop features with full access to private content
- Test thoroughly in isolation
- Commit all changes including private files

### 2. Cascade Forward
For each branch transition:
1. Merge with `--no-ff --no-commit`
2. Review changes and exclude private content
3. Run full test suite
4. If tests fail: implement fixes
5. Commit the merge

### 3. Fix Cascade Back
When fixes are needed:
1. Fix in the current branch
2. Cascade fix back to previous branch
3. Test in previous branch
4. Re-merge forward with fix included
5. Continue cascade

### 4. Push Strategy
- Push to origin: `dev`, `main`, `test`, `staging`
- NEVER push: `private` (contains sensitive content)
- Hold on pushing: `live` (until thoroughly tested)

## Detailed CASCADE Implementation

### Phase 1: Initial State
```bash
# Current branch: private
# All features implemented and tested
git status  # Clean working directory
```

### Phase 2: private → dev
```bash
git checkout dev
git merge private --no-ff --no-commit

# Review staged changes
git status
# Remove any private files that shouldn't be in dev using guardrail repokit code
# git rm -rf private/claude/ CLAUDE.md

# Run tests
python tests/run_tests.py --all

# If tests pass:
git commit -m "merge: bring features from private to dev"

# If tests fail:
# 1. Fix issues in dev
# 2. Commit fixes
# 3. Checkout private and merge dev to get fixes
# 4. Test in private
# 5. Re-merge private to dev
```

### Phase 3: dev → main
```bash
git checkout main
git merge dev --no-ff --no-commit

# Review and test
python tests/run_tests.py --all

# If tests fail:
# Apply CASCADE back protocol:
# 1. Fix in main
# 2. Merge main → dev (test)
# 3. Merge dev → private (test)
# 4. Re-cascade forward
```

### Phase 4: Continue CASCADE
Repeat for main → test → staging → live

## CASCADE Rules

### Rule 1: Always Test
Every branch must pass all tests before cascading forward

### Rule 2: Fix Cascade Back
Fixes flow backward through the hierarchy to maintain consistency

### Rule 3: Private Content Protection
- Use RepoKit guardrails at every step
- Validate no private content leaks to public branches
- Use `repokit check-guardrails` before commits

### Rule 4: Atomic Cascades
Complete entire cascade or rollback - no partial states

### Rule 5: Document Issues
Log any issues encountered during cascade for future reference

## Quick Reference Commands

```bash
# Check current state
repokit check-guardrails
git status

# Safe merge with preview
repokit safe-merge <source-branch> --preview

# Cascade merge
git merge <source> --no-ff --no-commit
# Review changes
git status
# Test
python tests/run_tests.py --all
# Commit if clean
git commit -m "cascade: merge <source> to <target>"

# Fix cascade back
git checkout <previous-branch>
git merge <current-branch> --no-ff
# Test and validate
```

## CASCADE Checklist

- [ ] All tests passing in source branch
- [ ] Working directory clean
- [ ] Guardrails installed and active
- [ ] Private content validated
- [ ] Merge performed with --no-ff --no-commit
- [ ] Changes reviewed for private content
- [ ] Tests run and passing
- [ ] Commit message follows convention
- [ ] Ready for next cascade step

## Common Issues and Solutions

### Issue: Private files in public branch
**Solution**: Use `git rm` before committing merge

### Issue: Tests fail after merge
**Solution**: Fix, commit, cascade back, re-merge

### Issue: Merge conflicts
**Solution**: Resolve carefully, ensuring no private content leaks

### Issue: Forgotten exclude patterns
**Solution**: Update branch_utils.py patterns, reinstall guardrails

## Benefits of CASCADE

1. **Consistency**: All branches stay in sync
2. **Safety**: Private content never leaks
3. **Quality**: Tests at every step
4. **Traceability**: Clear merge history
5. **Rollback**: Can stop cascade at any point