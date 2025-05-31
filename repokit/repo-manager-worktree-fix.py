    """
    Update to repo_manager.py to fix worktree synchronization issues
    """

    def _update_branches_from_private(self) -> None:
        """
        Update all branches from the private branch.
        
        This is used after committing bootstrap files to ensure all branches
        have the same content.
        """
        private_branch = self.config.get("private_branch", "private")
        branches = self.config.get("branches", ["main", "dev", "staging", "test", "live"])
        
        # Get current branch
        current_branch = self.run_git(["branch", "--show-current"], cwd=self.repo_root)
        
        # Get the commit hash of the private branch for reset operations
        private_hash = self.run_git(["rev-parse", private_branch], cwd=self.repo_root)
        
        for branch in branches:
            if branch != private_branch:
                try:
                    # Check if the branch is checked out in a worktree
                    if self._is_branch_in_worktree(branch):
                        # For branches in worktrees, we need to update them directly in the worktree
                        worktree_path = self._get_worktree_path(branch)
                        if worktree_path:
                            # Use a more forceful update approach
                            self.logger.info(f"Updating branch '{branch}' in worktree {worktree_path}")
                            
                            # First fetch the changes from the main repository
                            self.run_git(["fetch", "..", private_branch], cwd=worktree_path, check=False)
                            
                            # Then hard reset to the private branch commit
                            self.run_git(["reset", "--hard", private_hash], cwd=worktree_path, check=False)
                            
                            # Verify the update worked
                            current_hash = self.run_git(["rev-parse", "HEAD"], cwd=worktree_path, check=False)
                            if current_hash == private_hash:
                                self.logger.info(f"Updated branch '{branch}' from {private_branch}")
                            else:
                                self.logger.warning(f"Failed to update branch '{branch}' to match {private_branch}")
                    else:
                        # For branches not in worktrees, we can update them directly
                        self.run_git(["checkout", branch], cwd=self.repo_root)
                        self.run_git(["reset", "--hard", private_branch], cwd=self.repo_root)
                        self.logger.info(f"Updated branch '{branch}' from {private_branch}")
                except Exception as e:
                    self.logger.warning(f"Failed to update branch '{branch}': {str(e)}")
        
        # Return to original branch
        if current_branch != self.run_git(["branch", "--show-current"], cwd=self.repo_root):
            self.run_git(["checkout", current_branch], cwd=self.repo_root)

    def _update_worktrees(self) -> None:
        """
        Update all worktrees to match their corresponding branches.
        
        This ensures that all worktree directories reflect the latest state
        of their branches.
        """
        # Check if we have worktrees
        worktree_output = self.run_git(["worktree", "list"], cwd=self.repo_root, check=False)
        if not worktree_output:
            return
        
        # Parse worktree list
        worktrees = {}
        for line in worktree_output.split('\n'):
            if not line.strip():
                continue
            
            # Parse worktree line (format: "/path/to/worktree  abcd1234 [branch]")
            parts = line.split()
            if len(parts) >= 3 and '[' in parts[2] and ']' in parts[2]:
                path = parts[0]
                branch = parts[2].strip('[]')
                worktrees[branch] = path
        
        # Update each worktree
        for branch, path in worktrees.items():
            if branch == self.config.get("private_branch", "private"):
                # Skip private branch
                continue
            
            try:
                # Force synchronization with the branch from the main repository
                branch_hash = self.run_git(["rev-parse", branch], cwd=self.repo_root)
                
                # Make sure worktree has latest changes from its branch
                self.run_git(["reset", "--hard", branch_hash], cwd=path, check=False)
                self.run_git(["clean", "-fd"], cwd=path, check=False)
                
                # Verify the update worked
                current_hash = self.run_git(["rev-parse", "HEAD"], cwd=path, check=False)
                if current_hash == branch_hash:
                    self.logger.info(f"Updated worktree for branch '{branch}' at {path}")
                else:
                    self.logger.warning(f"Failed to update worktree for branch '{branch}' at {path}")
            except Exception as e:
                self.logger.warning(f"Failed to update worktree for branch '{branch}': {str(e)}")
