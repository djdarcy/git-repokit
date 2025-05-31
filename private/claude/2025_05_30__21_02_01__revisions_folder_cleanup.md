# Revisions Folder Cleanup
**Date**: 2025-05-30 21:02:01
**Task**: Remove revisions folder from all branches except private and update .gitignore

## Background
The revisions folder was accidentally committed to the repository and pushed to GitHub. We need to:
1. Remove it from all branches (dev, main, test, staging, live)
2. Add it to .gitignore to prevent future commits (but make sure it doesn't affect the private branch)
3. Keep it only in the private branch for local version control

## Process Overview
1. Switch to each branch
2. Remove the revisions folder
3. Add revisions/ to .gitignore
4. Commit the changes
5. Push to GitHub to remove from remote

## Commands to Execute

### Step 1: Switch to dev branch and clean up
```bash
git checkout dev
git rm -r revisions/
# Check if .gitignore exists, if so update it
# Add revisions/ to .gitignore
git add .gitignore
git commit -m "Remove revisions folder and add to .gitignore"
git push origin dev
```

### Step 2: Switch to main branch and clean up
```bash
git checkout main
git rm -r revisions/
# Merge the .gitignore change from dev
git merge dev --no-ff --no-commit
# Review and commit
git commit -m "Remove revisions folder and update .gitignore from dev"
git push origin main
```

### Step 3: Return to private branch
```bash
git checkout private
```

## Note on Future Merges
Going forward, we will use:
- `--no-ff` (no fast-forward) to preserve merge history
- `--no-commit` to review changes before committing
This ensures we can track where changes originate and verify correctness before finalizing.