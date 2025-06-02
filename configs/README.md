# RepoKit Configuration Examples

This directory contains example configuration files for different project types and scenarios.

## Available Examples

### minimal-python.json
A minimal Python project configuration using the "minimal" directory profile.
- Creates only essential directories: src, tests, docs
- Uses minimal branch strategy (just main branch)
- Perfect for small utilities or single-purpose scripts

### standard-web.json
Standard web application setup with JavaScript defaults.
- Uses "standard" directory profile
- Adds web-specific directories: public, static, dist
- Simple branch strategy for straightforward deployment
- Custom branch directory names (production/development)

### complete-enterprise.json
Enterprise-grade configuration with all features enabled.
- Complete directory structure with custom additions
- GitFlow branching strategy with multiple environments
- Custom directory profiles and enhanced private directory set
- Detailed branch flow configuration
- Suitable for large teams and complex projects

### custom-ml-project.json
Machine learning research project with specialized directories.
- Standard profile plus ML-specific directories
- Custom directory names using type mapping
- Private subdirectories for sensitive data
- Experiments branch with dedicated worktree

## Using Configuration Files

1. **With create command:**
   ```bash
   repokit create myproject --config configs/minimal-python.json
   ```

2. **Copy and customize:**
   ```bash
   cp configs/standard-web.json .repokit.json
   # Edit .repokit.json as needed
   repokit create myproject
   ```

3. **Override specific settings:**
   ```bash
   repokit create myproject --config configs/complete-enterprise.json --language javascript
   ```

## Configuration Hierarchy

RepoKit loads configuration from multiple sources (highest priority first):
1. Command-line arguments
2. Environment variables (REPOKIT_*)
3. Project config (./.repokit.json)
4. Global config (~/.repokit/config.json)
5. Default values

## Key Configuration Options

### Directory Profiles
- `minimal`: Basic structure (src, tests, docs)
- `standard`: Common directories for most projects
- `complete`: Full structure with all standard directories

### Directory Groups
- `development`: src, tests, scripts, tools
- `documentation`: docs, examples, resources
- `operations`: config, logs, data
- `privacy`: private, convos, credentials

### Branch Strategies
- `minimal`: Just main branch
- `simple`: main and dev branches
- `standard`: Full workflow (main, dev, staging, test, live)
- `gitflow`: GitFlow model
- `github-flow`: GitHub flow (main + feature branches)

## Creating Custom Configurations

1. **Start with an example:**
   Choose the closest example to your needs

2. **Customize directories:**
   - Use `directory_profile` for base structure
   - Add extra with `directories`
   - Specify private with `private_dirs`

3. **Configure branching:**
   - Choose a `branch_strategy`
   - Customize branch names and worktrees
   - Define branch flow rules

4. **Set project details:**
   - Update name and description
   - Set appropriate language
   - Configure user information

## Tips

- Use `_comment` fields to document your configuration choices
- Combine profiles with explicit directories for flexibility
- Private directories can include subdirectories (e.g., "data/raw")
- Branch directory mappings help organize worktrees
- Custom directory types let you rename standard directories