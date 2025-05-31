# Authentication Guide for Remote Integration

RepoKit can publish repositories directly to GitHub or GitLab. This guide explains how to set up and securely store authentication credentials.

## GitHub Authentication

### 1. Creating a Personal Access Token (PAT)

1. Go to your GitHub account settings
2. Select at the bottom on the left "Developer settings" → "Personal access tokens" → "Tokens (classic)"
3. Click "Generate new token"
4. Give your token a descriptive name (e.g., "RepoKit Integration")
5. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (if you plan to use GitHub Actions)
6. Click "Generate token"
7. **IMPORTANT**: Copy your token immediately! GitHub will only show it once.

### 2. Using Your Token with RepoKit

Once you have your GitHub token, you have three secure ways to use it:

#### Option A: Environment Variable (Recommended)

Set the `GITHUB_TOKEN` environment variable:

```bash
# On Linux/macOS
export GITHUB_TOKEN=your_token_here

# On Windows (Command Prompt)
set GITHUB_TOKEN=your_token_here

# On Windows (PowerShell)
$env:GITHUB_TOKEN="your_token_here"
```

For permanent storage, add this to your shell profile (~/.bashrc, ~/.zshrc, etc.).

#### Option B: Credentials File

Create a JSON file with your credentials (e.g., `~/.repokit/credentials.json`):

```json
{
  "github": {
    "token": "your_token_here",
    "organization": "optional_organization_name"
  },
  "gitlab": {
    "token": "your_gitlab_token_here",
    "group": "optional_group_name"
  }
}
```

Then use it with RepoKit:

```bash
repokit create my-project --credentials-file ~/.repokit/credentials.json --publish-to github
```

**IMPORTANT**: Never commit this file to a repository!

#### Option C: Password Manager Integration

For advanced users, integrate with a password manager:

```bash
# Example with pass (Unix password manager)
repokit create my-project --github-token-command "pass show github/repokit-token" --publish-to github
```

## GitLab Authentication

### 1. Creating a Personal Access Token

1. Go to your GitLab account → "Preferences"
2. Select "Access Tokens"
3. Create a token with the following scopes:
   - `api` (API access)
   - `write_repository` (Repository write access)
4. Click "Create personal access token"
5. Copy your token immediately!

### 2. Using Your Token with RepoKit

Use your GitLab token in the same ways as GitHub:

#### Environment Variables

```bash
export GITLAB_TOKEN=your_token_here
# Optional: Specify a custom GitLab instance
export GITLAB_API_URL=https://gitlab.example.com/api/v4
```

#### Credentials File

Same as GitHub (see above).

## Security Best Practices

1. **Use environment variables** when possible to avoid storing tokens in files
2. **Set restrictive permissions** on any file containing tokens:
   ```bash
   chmod 600 ~/.repokit/credentials.json
   ```
3. **Never commit credential files** to repositories
4. **Use .gitignore** to prevent accidental commits:
   ```
   # Add to .gitignore
   *credentials*.json
   *.repokit-credentials
   ```
5. **Rotate tokens periodically** for enhanced security
6. **Use scoped tokens** with only the permissions needed
7. **Consider using a secrets manager** for team environments

## Using Authentication

Once you've set up authentication, you can use it to:

### Create and Publish Repositories

```bash
# Create a new repository and publish it to GitHub
repokit create my-project --language python --publish-to github

# Create a private repository in an organization
repokit create my-project --language python --publish-to github --private-repo --organization your_org_name
```

### Publish Existing Repositories

```bash
# Publish an existing repository to GitHub
repokit publish ./my-existing-project --publish-to github
```

### Generate a Bootstrap Script

```bash
# Generate a script that demonstrates using RepoKit to set up itself
repokit bootstrap --publish-to github --output bootstrap_repokit.py
```
## Troubleshooting

If you encounter authentication issues:

1. Verify your token has the correct permissions
   - For GitHub: repo, workflow (if using GitHub Actions)
   - For GitLab: api, write_repository
2. Check that the token hasn't expired
3. Ensure environment variables are properly set
4. Try using the `--verbose` flag for detailed error messages
   ```bash
   repokit create my-project --publish-to github -vvv
   ```
5. Verify network connectivity to the Git hosting service
6. Check that your organization/group name is correct

## Command Reference

```
repokit store-credentials --publish-to SERVICE [--token TOKEN] [--token-command COMMAND] [--organization ORG] [--credentials-file FILE]
```

Arguments:
- `--publish-to`: Service to use (github or gitlab)
- `--token`: Authentication token
- `--token-command`: Command to retrieve token
- `--organization`: Organization or group name
- `--credentials-file`: Custom path for credentials file
- `--verbose`, `-v`: Increase verbosity level

For more help, see the [GitHub token documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) or [GitLab token documentation](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).
