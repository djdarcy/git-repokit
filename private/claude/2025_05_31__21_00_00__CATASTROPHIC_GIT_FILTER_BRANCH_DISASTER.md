# CATASTROPHIC GIT FILTER-BRANCH DISASTER - CRITICAL LESSONS LEARNED

## Date: 2025-05-31 21:00:00
## Severity: CATASTROPHIC DATA LOSS

## What Happened

We attempted to remove private files (CLAUDE.md and private/claude/) from the dev branch to prevent exposure when pushing to GitHub. However, the cleanup operation resulted in catastrophic data loss.

### The Fatal Command
```bash
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch CLAUDE.md private/claude/* || true' --prune-empty -- --all
```

### Why This Was Catastrophic

1. **Used `--all` flag**: This rewrote history on ALL branches, not just dev
2. **Lost uncommitted work**: When we reset branches after filter-branch, all untracked files were lost
3. **No backup**: We didn't create a backup before this dangerous operation

## Data Lost

### 1. configs/ Directory
- Complete loss of JSON configuration files
- These were meant to be example configurations for directory profiles
- Were created but never committed (our first mistake)

### 2. private/claude/ Conversation Logs  
- Multiple conversation log files that were untracked
- Some logs were empty/corrupted during the operation
- Lost detailed implementation notes and context

### 3. Other Untracked Files
- Any work-in-progress files
- Test artifacts that might have been useful
- Temporary notes or scripts

## Root Causes

1. **Uncommitted Work**: Critical files (configs/) were created but never committed
2. **Overly Broad Command**: Used `--all` instead of targeting specific branches
3. **No Safety Check**: Didn't verify untracked files before dangerous operation
4. **Misunderstanding Tool**: filter-branch is extremely dangerous and should be last resort

## The Irony

RepoKit exists to prevent exactly this type of disaster. The fact that we experienced this while developing RepoKit is a profound lesson that our safeguards are insufficient.

## Recovery Attempts

1. Used git reflog to restore branch states
2. Recreated CLAUDE.md from template and memory
3. Found some information about configs/ in conversation logs
4. But much work is permanently lost

## Using "The Process" to Analyze and Prevent

### 1. Problem Analysis

**Core Problem**: Developers need to remove sensitive files from certain branches without losing data

**Sub-problems**:
- Branch-specific file exclusion is complex
- Git operations can have unintended consequences  
- Uncommitted work is vulnerable
- No clear workflow for branch hygiene

**Risks**:
- Data loss (as we experienced)
- Accidental exposure of sensitive data
- Corruption of git history
- Loss of development context

### 2. Conceptual Exploration

**Why this problem exists**:
- Git's power comes with danger
- Branch management is conceptually difficult
- File tracking vs. working directory is confusing
- No built-in safeguards for dangerous operations

**Mental Models**:
- Branches as parallel universes that can affect each other
- Working directory as shared state across branches
- Git history as immutable until forcefully rewritten

### 3. Brainstorming Solutions

**Solution 1: Pre-operation Checklist**
- Automated check for uncommitted files
- Backup creation before dangerous operations
- Dry-run mode for all rewrite operations
- Pros: Comprehensive safety
- Cons: Could be ignored/skipped

**Solution 2: Branch-Conditional Excludes Enhancement**
- Better tooling for .git/info/exclude setup
- Automated exclude file management per branch
- Visual indicators of excluded files
- Pros: Prevents problem at source
- Cons: Doesn't help with existing tracked files

**Solution 3: RepoKit Safe-Merge Command**
- Custom merge command that respects excludes
- Automatic filtering during merge
- Preview of what will be merged
- Pros: User-friendly, safe
- Cons: Additional complexity

**Solution 4: Worktree-Based Isolation**
- Enforce worktree usage for different branches
- Separate working directories prevent confusion
- Automatic exclude setup per worktree
- Pros: Strong isolation
- Cons: More disk space, complexity

### 4. Synthesis and Recommendation

**Optimal Approach**: Combination of all solutions

1. **Immediate**: Implement pre-operation safety checks
2. **Short-term**: Enhance branch-conditional exclude tooling  
3. **Long-term**: Create safe-merge command
4. **Best Practice**: Promote worktree-based workflow

### 5. Implementation Plan

**Phase 1 - Safety Checks (1 day)**
- Add `repokit safety-check` command
- Check for uncommitted files
- Create automatic backups
- Warn about dangerous operations

**Phase 2 - Exclude Enhancement (2-3 days)**
- Add `repokit setup-excludes` command
- Per-branch exclude management
- Visual status indicators
- Integration with existing workflow

**Phase 3 - Safe Merge (1 week)**
- Implement `repokit safe-merge` command
- Preview merge results
- Automatic exclude filtering
- Rollback capability

**Phase 4 - Documentation (ongoing)**
- Document all dangerous scenarios
- Create workflow guides
- Add warnings throughout codebase

## Immediate Recovery Actions

1. **Recreate configs/ directory from conversation logs**
2. **Document all lost work that can be remembered**
3. **Commit everything immediately**
4. **Create backup of current state**
5. **Implement basic safety checks**

## Lessons for RepoKit Users

1. **ALWAYS commit or stash before branch operations**
2. **NEVER use git filter-branch without a full backup**
3. **Use worktrees to isolate branch work**
4. **Set up excludes BEFORE creating private content**
5. **Regular commits are your safety net**

## New RepoKit Principles

1. **Safety First**: Every dangerous operation must have safeguards
2. **Fail Loud**: Better to stop than lose data
3. **Guide Users**: Provide clear workflows for complex tasks
4. **Protect the Naive**: Assume users will make mistakes
5. **Learn from Pain**: This disaster must improve RepoKit

## Never Forget

On May 31, 2025, we lost hours of work because we didn't follow our own principles. This document serves as a permanent reminder that the tools we build must protect users from the mistakes we made.

The command that caused this disaster should have never been run without:
- A full backup
- Checking for uncommitted work  
- Understanding the full implications
- Testing on a copy first

RepoKit must make it impossible for users to experience this pain.