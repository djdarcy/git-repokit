#!/usr/bin/env python3
"""
Template engine for RepoKit.

Handles loading and rendering templates from the package's template directory.
"""

import os
import logging
import string
import pkg_resources
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

class TemplateEngine:
    """
    Template engine for loading and rendering templates.
    """
    
    def __init__(self, templates_dir: Optional[str] = None, verbose: int = 0):
        """
        Initialize the template engine.
        
        Args:
            templates_dir: Path to template directory (or use package's templates)
            verbose: Verbosity level (0=normal, 1=info, 2=debug)
        """
        self.verbose = verbose
        
        # Configure logging
        self.logger = logging.getLogger("repokit.templates")
        
        # Try multiple locations for templates
        self.templates_dirs = []
        
        # 1. Use provided template directory if specified
        if templates_dir:
            self.templates_dirs.append(templates_dir)
        
        # 2. Try to find templates in the package
        try:
            pkg_templates = pkg_resources.resource_filename("repokit", "templates")
            self.templates_dirs.append(pkg_templates)
        except (ImportError, pkg_resources.DistributionNotFound):
            pass
        
        # 3. Check current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.templates_dirs.append(os.path.join(script_dir, "templates"))
        
        # 4. Check current working directory
        cwd_templates = os.path.join(os.getcwd(), "repokit", "templates")
        self.templates_dirs.append(cwd_templates)
        
        # 5. Check parent directories (for development mode)
        current_dir = os.getcwd()
        for _ in range(3):  # Check up to 3 levels up
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                break
            current_dir = parent_dir
            self.templates_dirs.append(os.path.join(current_dir, "repokit", "templates"))
        
        # Find first valid template directory
        self.templates_dir = None
        for dir_path in self.templates_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                self.templates_dir = dir_path
                break
        
        if self.templates_dir:
            if self.verbose >= 1:
                self.logger.info(f"Using templates from: {self.templates_dir}")
        else:
            self.logger.warning(f"No template directory found. Tried: {self.templates_dirs}")
            # Use fallback templates
            self.templates_dir = None
        
        # Fallback templates for critical files
        self.fallback_templates = {
            "common/README.md.template": """# $project_name\n\n$description\n""",
            "common/gitignore.template": """# Ignore common files\n.DS_Store\n*.log\n""",
            "github/workflows/main.yml.template": """name: CI\n\non:\n  push:\n    branches: [ main ]\n  pull_request:\n    branches: [ main ]\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n    - uses: actions/checkout@v3\n""",
        }
    
    def get_template_path(self, template_name: str, category: str = "common") -> Optional[str]:
        """
        Get the path to a template file.
        
        Args:
            template_name: Name of the template file
            category: Category of the template (common, github, languages/python, etc.)
            
        Returns:
            Path to the template file or None if not found
        """
        if not self.templates_dir:
            return None
            
        # Try direct path first (if template_name includes a category)
        if "/" in template_name:
            direct_path = os.path.join(self.templates_dir, template_name)
            if os.path.exists(direct_path):
                return direct_path
        
        # Try with .template extension
        if not template_name.endswith(".template"):
            template_name = f"{template_name}.template"
        
        # Look in multiple possible locations
        possible_paths = []
        
        # 1. Look in the specified category
        possible_paths.append(os.path.join(self.templates_dir, category, template_name))
        
        # 2. Try common category if not found and not already looking there
        if category != "common":
            possible_paths.append(os.path.join(self.templates_dir, "common", template_name))
        
        # 3. Try languages subdirectory
        if "/" not in category and not category.startswith("languages/"):
            possible_paths.append(os.path.join(self.templates_dir, "languages", category, template_name))
        
        # 4. Try root templates directory
        possible_paths.append(os.path.join(self.templates_dir, template_name))
        
        # Check all possible paths
        for path in possible_paths:
            if os.path.exists(path):
                if self.verbose >= 2:
                    self.logger.debug(f"Found template at: {path}")
                return path
        
        # Log the paths we tried
        if self.verbose >= 2:
            self.logger.debug(f"Tried looking for template in: {possible_paths}")
        
        return None
    
    def load_template(self, template_name: str, category: str = "common") -> Optional[str]:
        """
        Load a template file.
        
        Args:
            template_name: Name of the template file
            category: Category of the template (common, github, languages/python, etc.)
            
        Returns:
            Template content as string or None if not found
        """
        # First try to find the template file
        template_path = self.get_template_path(template_name, category)
        if template_path:
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if self.verbose >= 2:
                    self.logger.debug(f"Loaded template: {template_path}")
                return content
            except Exception as e:
                self.logger.error(f"Error loading template {template_path}: {str(e)}")
        
        # If not found, try fallback templates
        fallback_key = f"{category}/{template_name}"
        if not fallback_key.endswith(".template"):
            fallback_key += ".template"
            
        if fallback_key in self.fallback_templates:
            if self.verbose >= 1:
                self.logger.info(f"Using fallback template for: {fallback_key}")
            return self.fallback_templates[fallback_key]
        
        # Final fallback for specific template types
        base_template_name = os.path.basename(template_name)
        if base_template_name == "README.md.template":
            return """# $project_name\n\n$description\n"""
        elif base_template_name == "gitignore.template":
            return """# Ignore patterns\n*.log\n.DS_Store\n"""
        
        self.logger.warning(f"Template not found: {template_name} in category {category}")
        return None
    
    def render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_content: Template content as string
            context: Dictionary of variables for template rendering
            
        Returns:
            Rendered template as string
        """
        try:
            template = string.Template(template_content)
            return template.safe_substitute(context)
        except Exception as e:
            self.logger.error(f"Error rendering template: {str(e)}")
            # Return original content in case of error
            return template_content
    
    def render_template_to_file(self, template_name: str, output_path: str, 
                               context: Dict[str, Any], category: str = "common") -> bool:
        """
        Load, render, and write a template to a file.
        
        Args:
            template_name: Name of the template file
            output_path: Path to write the rendered template
            context: Dictionary of variables for template rendering
            category: Category of the template (common, github, languages/python, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        template_content = self.load_template(template_name, category)
        if not template_content:
            return False
        
        rendered_content = self.render_template(template_content, context)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(rendered_content)
            
            if self.verbose >= 2:
                self.logger.debug(f"Rendered template {template_name} to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing template to {output_path}: {str(e)}")
            return False
    
    def list_templates(self, category: str = None) -> List[str]:
        """
        List available templates.
        
        Args:
            category: Category to list templates from (or all if None)
            
        Returns:
            List of template names
        """
        templates = []
        
        # Return fallback templates if no templates directory
        if not self.templates_dir:
            return list(self.fallback_templates.keys())
        
        if category:
            category_path = os.path.join(self.templates_dir, category)
            if os.path.exists(category_path) and os.path.isdir(category_path):
                for file in os.listdir(category_path):
                    if file.endswith(".template"):
                        templates.append(file)
        else:
            # List all templates
            for root, _, files in os.walk(self.templates_dir):
                for file in files:
                    if file.endswith(".template"):
                        rel_path = os.path.relpath(os.path.join(root, file), self.templates_dir)
                        templates.append(rel_path)
        
        return templates
