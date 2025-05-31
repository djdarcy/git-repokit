#!/usr/bin/env python3
"""
Authentication handler for RepoKit.

Manages authentication with remote services like GitHub and GitLab.
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class AuthenticationHandler:
    """
    Handles authentication with remote services.
    """
    
    def __init__(self, verbose: int = 0):
        """
        Initialize the authentication handler.
        
        Args:
            verbose: Verbosity level (0=normal, 1=info, 2=debug)
        """
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.auth")
        
        # Default locations for credentials
        self.user_home = Path.home()
        self.default_creds_path = self.user_home / ".repokit" / "credentials.json"
        
        # Initialize with empty credentials
        self.credentials = {}
    
    def load_credentials(self, credentials_file: Optional[str] = None) -> bool:
        """
        Load credentials from a file.
        
        Args:
            credentials_file: Path to credentials file (or None to use default)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        if credentials_file:
            creds_path = Path(credentials_file)
        elif self.default_creds_path.exists():
            creds_path = self.default_creds_path
        else:
            if self.verbose >= 1:
                self.logger.info("No credentials file found")
            return False
        
        try:
            with open(creds_path, 'r') as f:
                self.credentials = json.load(f)
            
            if self.verbose >= 1:
                self.logger.info(f"Loaded credentials from {creds_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading credentials: {str(e)}")
            return False
    
    def get_token(self, service: str, token_command: Optional[str] = None) -> Optional[str]:
        """
        Get authentication token for a service.
        
        Tries multiple sources in this order:
        1. Command provided token command
        2. Environment variable
        3. Credentials file
        
        Args:
            service: Service name ('github' or 'gitlab')
            token_command: Optional command to retrieve token from password manager
            
        Returns:
            Authentication token or None if not found
        """
        # Standardize service name
        service = service.lower()
        
        # 1. Try token command if provided
        if token_command:
            try:
                if self.verbose >= 2:
                    self.logger.debug(f"Running token command: {token_command}")
                result = subprocess.run(
                    token_command, 
                    shell=True, 
                    check=True,
                    capture_output=True,
                    text=True
                )
                token = result.stdout.strip()
                if token:
                    if self.verbose >= 1:
                        self.logger.info(f"Retrieved {service} token using command")
                    return token
            except Exception as e:
                self.logger.error(f"Failed to get token from command: {str(e)}")
        
        # 2. Try environment variable
        env_var = f"{service.upper()}_TOKEN"
        token = os.environ.get(env_var)
        if token:
            if self.verbose >= 1:
                self.logger.info(f"Using {service} token from environment variable")
            return token
        
        # 3. Try credentials file
        if service in self.credentials and "token" in self.credentials[service]:
            if self.verbose >= 1:
                self.logger.info(f"Using {service} token from credentials file")
            return self.credentials[service]["token"]
        
        # Token not found
        self.logger.warning(f"No {service} token found")
        return None
    
    def get_organization(self, service: str) -> Optional[str]:
        """
        Get organization or group for a service.
        
        Args:
            service: Service name ('github' or 'gitlab')
            
        Returns:
            Organization/group name or None if not specified
        """
        # Standardize service name
        service = service.lower()
        
        # Try environment variable first
        env_var = f"{service.upper()}_ORGANIZATION"
        if service == "gitlab":
            env_var = "GITLAB_GROUP"  # GitLab uses "group" terminology
        
        org = os.environ.get(env_var)
        if org:
            return org
        
        # Try credentials file
        if service in self.credentials:
            if service == "github" and "organization" in self.credentials[service]:
                return self.credentials[service]["organization"]
            elif service == "gitlab" and "group" in self.credentials[service]:
                return self.credentials[service]["group"]
        
        return None
    
    def get_api_url(self, service: str) -> str:
        """
        Get API URL for a service.
        
        Args:
            service: Service name ('github' or 'gitlab')
            
        Returns:
            API URL for the service
        """
        if service.lower() == "github":
            return os.environ.get("GITHUB_API_URL", "https://api.github.com")
        elif service.lower() == "gitlab":
            return os.environ.get("GITLAB_API_URL", "https://gitlab.com/api/v4")
        else:
            return ""
    
    def store_credentials(self, service: str, token: str, 
                        organization: Optional[str] = None,
                        file_path: Optional[str] = None) -> bool:
        """
        Store credentials in the credentials file.
        
        Args:
            service: Service name ('github' or 'gitlab')
            token: Authentication token
            organization: Organization or group name (optional)
            file_path: Path to credentials file (or None to use default)
            
        Returns:
            True if stored successfully, False otherwise
        """
        # Standardize service name
        service = service.lower()
        
        # Load existing credentials if file exists
        if file_path:
            creds_path = Path(file_path)
        else:
            creds_path = self.default_creds_path
            # Ensure directory exists
            creds_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing credentials if file exists
        existing_creds = {}
        if creds_path.exists():
            try:
                with open(creds_path, 'r') as f:
                    existing_creds = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading existing credentials: {str(e)}")
                # Continue with empty credentials
        
        # Update credentials
        service_creds = existing_creds.get(service, {})
        service_creds["token"] = token
        
        if organization:
            if service == "github":
                service_creds["organization"] = organization
            elif service == "gitlab":
                service_creds["group"] = organization
        
        existing_creds[service] = service_creds
        
        # Save credentials
        try:
            with open(creds_path, 'w') as f:
                json.dump(existing_creds, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(creds_path, 0o600)
            
            if self.verbose >= 1:
                self.logger.info(f"Stored {service} credentials in {creds_path}")
            
            # Update in-memory credentials
            self.credentials = existing_creds
            
            return True
        except Exception as e:
            self.logger.error(f"Error storing credentials: {str(e)}")
            return False
