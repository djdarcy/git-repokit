# RepoKit Recipes and How-To Guides

Quick solutions for common RepoKit use cases. Copy, paste, and adapt these recipes for your projects.

## 📋 Table of Contents

1. [Quick Start Recipes](#quick-start-recipes)
2. [Language-Specific Recipes](#language-specific-recipes)
3. [GitHub Deployment Recipes](#github-deployment-recipes)
4. [Security and Privacy Recipes](#security-and-privacy-recipes)
5. [Team Collaboration Recipes](#team-collaboration-recipes)
6. [Maintenance and Cleanup Recipes](#maintenance-and-cleanup-recipes)
7. [Troubleshooting Recipes](#troubleshooting-recipes)

## 🚀 Quick Start Recipes

### Recipe: "Help me create a simple new project locally"

```bash
repokit create ./my-project \
  --language python \
  --branch-strategy simple \
  --dir-profile standard \
  --private-repo \
  --user-name name \
  --user-email id+user@users.noreply.github.com \
  --ai claude
```

### Recipe: "I just want to organize my code"

```bash
# Test first
repokit adopt ./my-project --dry-run

# Basic organization
repokit adopt ./my-project --backup
```

### Recipe: "Put my project on GitHub (Private)"
```bash
repokit adopt ./my-project \
  --publish-to github \
  --repo-name my-project \
  --private-repo \
  --backup
```

### Recipe: "Put my project on GitHub (Public)"
```bash
repokit adopt ./my-project \
  --publish-to github \
  --repo-name my-awesome-project \
  --description "An awesome open source project" \
  --clean-history \
  --cleaning-recipe pre-open-source
```

### Recipe: "I want the full professional setup"
```bash
repokit adopt ./my-project \
  --dir-profile complete \
  --branch-strategy simple \
  --language python \
  --ai claude \
  --publish-to github \
  --repo-name my-professional-project \
  --private-repo \
  --backup
```

## 💻 Language-Specific Recipes

### Python Project Recipes

#### Recipe: Python Package Development
```bash
repokit adopt ./my-python-package \
  --language python \
  --dir-profile standard \
  --directories "src,tests,docs,examples" \
  --sensitive-patterns "*.pyc,__pycache__/*,*.egg-info/*,dist/*,build/*" \
  --publish-to github \
  --repo-name my-python-package
```

#### Recipe: Data Science Project
```bash
repokit adopt ./data-science-project \
  --language python \
  --directories "data,notebooks,models,experiments,reports" \
  --private-dirs "experiments,drafts,raw_data" \
  --sensitive-patterns "*.csv,*.pkl,*.h5,data/raw/*,*.ipynb_checkpoints/*" \
  --ai claude \
  --private-repo
```

#### Recipe: Django Web App
```bash
repokit adopt ./django-app \
  --language python \
  --directories "static,templates,media,requirements" \
  --sensitive-files "settings/local.py,.env,db.sqlite3" \
  --sensitive-patterns "media/*,staticfiles/*,*.log,*.sqlite3" \
  --branch-strategy simple \
  --publish-to github \
  --private-repo
```

#### Recipe: Flask API
```bash
repokit adopt ./flask-api \
  --language python \
  --directories "app,tests,migrations,config" \
  --sensitive-files ".env,.flaskenv,instance/config.py" \
  --sensitive-patterns "*.db,*.sqlite,instance/*,logs/*" \
  --ai claude \
  --publish-to github
```

### JavaScript Project Recipes

#### Recipe: Node.js Application
```bash
repokit adopt ./node-app \
  --language javascript \
  --directories "src,tests,public,config" \
  --sensitive-files ".env,.env.local,config/keys.js" \
  --sensitive-patterns "node_modules/*,*.log,dist/*,build/*" \
  --publish-to github \
  --repo-name node-application
```

#### Recipe: React Application
```bash
repokit adopt ./react-app \
  --language javascript \
  --directories "src,public,tests,docs" \
  --sensitive-patterns "node_modules/*,build/*,.env.local,*.log" \
  --branch-strategy github-flow \
  --publish-to github \
  --repo-name react-application
```

#### Recipe: Express.js API
```bash
repokit adopt ./express-api \
  --language javascript \
  --directories "routes,middleware,models,tests" \
  --sensitive-files ".env,config/database.js" \
  --sensitive-patterns "node_modules/*,logs/*,uploads/*" \
  --ai claude \
  --publish-to github \
  --private-repo
```

### Generic Project Recipes

#### Recipe: Documentation Project
```bash
repokit adopt ./documentation \
  --language generic \
  --directories "content,assets,templates,scripts" \
  --dir-profile minimal \
  --publish-to github \
  --repo-name project-docs
```

#### Recipe: Configuration Repository
```bash
repokit adopt ./configs \
  --language generic \
  --directories "configs,scripts,templates,docs" \
  --sensitive-patterns "*.key,*.pem,secrets/*,private/*" \
  --private-repo \
  --ai claude
```

## 🌐 GitHub Deployment Recipes

### Recipe: Personal Open Source Project
```bash
repokit adopt ./open-source-project \
  --publish-to github \
  --repo-name awesome-open-source \
  --description "An awesome open source project that solves X problem" \
  --language python \
  --dir-profile complete \
  --clean-history \
  --cleaning-recipe pre-open-source \
  --ai claude
```

### Recipe: Company Private Repository
```bash
repokit adopt ./company-project \
  --publish-to github \
  --repo-name internal-tools \
  --organization mycompany \
  --private-repo \
  --description "Internal tools for company operations" \
  --sensitive-patterns "*.env,secrets/*,credentials/*,*.key" \
  --backup \
  --backup-location ../company-project-backup
```

### Recipe: Portfolio Project
```bash
repokit adopt ./portfolio-project \
  --publish-to github \
  --repo-name portfolio-awesome-project \
  --description "A project demonstrating my skills in X technology" \
  --language python \
  --dir-profile complete \
  --clean-history \
  --ai claude
```

### Recipe: Team Collaboration Project
```bash
repokit adopt ./team-project \
  --publish-to github \
  --repo-name team-collaboration \
  --organization our-team \
  --private-repo \
  --branch-strategy gitflow \
  --dir-profile complete \
  --ai claude
```

## 🔒 Security and Privacy Recipes

### Recipe: Maximum Privacy Protection
```bash
repokit adopt ./sensitive-project \
  --private-set enhanced \
  --private-dirs "secrets,credentials,internal,drafts" \
  --sensitive-files ".env,.env.*,api_keys.txt,passwords.txt" \
  --sensitive-patterns "*.key,*.pem,*.p12,*.pfx,secrets/*,credentials/*,*.log,*~" \
  --private-repo \
  --backup \
  --no-push  # Don't push automatically
```

### Recipe: Clean History for Open Source
```bash
repokit adopt ./legacy-project \
  --clean-history \
  --cleaning-recipe pre-open-source \
  --sensitive-patterns "*.env,*.key,passwords/*,secrets/*,internal/*" \
  --backup \
  --backup-location ../legacy-project-backup \
  --publish-to github \
  --repo-name cleaned-open-source
```

### Recipe: Research Project with Data Protection
```bash
repokit adopt ./research-project \
  --directories "papers,code,analysis,figures" \
  --private-dirs "raw_data,personal_notes,drafts" \
  --sensitive-patterns "*.csv,*.xlsx,data/raw/*,personal/*,*.pdf,drafts/*" \
  --private-repo \
  --ai claude \
  --description "Research project on X topic"
```

### Recipe: Web App with Environment Variables
```bash
repokit adopt ./web-app \
  --sensitive-files ".env,.env.local,.env.production,config/secrets.yml" \
  --sensitive-patterns "*.env.*,secrets/*,uploads/*,*.log,node_modules/*" \
  --directories "src,tests,config,public" \
  --publish-to github \
  --private-repo
```

## 👥 Team Collaboration Recipes

### Recipe: Multi-Developer Team Setup
```bash
repokit adopt ./team-project \
  --branch-strategy gitflow \
  --dir-profile complete \
  --publish-to github \
  --organization our-company \
  --repo-name team-project \
  --private-repo \
  --user-name "Team Lead" \
  --user-email "lead@company.com"
```

### Recipe: Open Source Contribution Ready
```bash
repokit adopt ./oss-project \
  --dir-profile complete \
  --branch-strategy github-flow \
  --clean-history \
  --cleaning-recipe pre-open-source \
  --publish-to github \
  --repo-name community-project \
  --description "Open source project welcoming contributions" \
  --ai claude
```

### Recipe: Continuous Integration Setup
```bash
repokit adopt ./ci-project \
  --language python \
  --directories "src,tests,scripts,docs" \
  --branch-strategy github-flow \
  --sensitive-patterns "*.log,coverage/*,htmlcov/*,.tox/*" \
  --publish-to github \
  --repo-name ci-enabled-project
```

### Recipe: Mentorship Project
```bash
repokit adopt ./mentorship-project \
  --dir-profile complete \
  --branch-strategy simple \
  --ai claude \
  --publish-to github \
  --repo-name learning-project \
  --description "Project for learning and mentorship" \
  --directories "lessons,exercises,solutions,resources"
```

## 🧹 Maintenance and Cleanup Recipes

### Recipe: Clean Up Existing Repository
```bash
# First, backup
cp -r ./messy-project ./messy-project-backup

# Then clean
repokit adopt ./messy-project \
  --clean-history \
  --cleaning-recipe windows-safe \
  --sensitive-patterns "*.tmp,*.bak,*~,*.log,Thumbs.db,.DS_Store" \
  --backup
```

### Recipe: Migrate from Another System
```bash
repokit adopt ./legacy-system-export \
  --migration-strategy safe \
  --clean-history \
  --sensitive-patterns "*.old,*.backup,migration/*,temp/*" \
  --directories "src,docs,tests,scripts" \
  --backup \
  --backup-location ../legacy-backup
```

### Recipe: Archive Old Project
```bash
repokit adopt ./old-project \
  --dir-profile minimal \
  --branch-strategy minimal \
  --description "Archived project - no longer maintained" \
  --sensitive-patterns "*.log,temp/*,cache/*" \
  --publish-to github \
  --repo-name archived-old-project
```

### Recipe: Modernize Project Structure
```bash
repokit adopt ./outdated-project \
  --dir-profile complete \
  --language python \
  --clean-history \
  --cleaning-recipe pre-open-source \
  --ai claude \
  --publish-to github \
  --repo-name modernized-project \
  --backup
```

## 🚨 Troubleshooting Recipes

### Recipe: Fix Permission Issues
```bash
# Fix permissions first
chmod -R u+w ./problematic-project

# Then adopt
repokit adopt ./problematic-project \
  --backup \
  --verbose
```

### Recipe: Handle Large Files
```bash
# Set up Git LFS first
cd my-project
git lfs track "*.csv"
git lfs track "*.pkl"
git lfs track "*.h5"
git add .gitattributes

# Then adopt
repokit adopt . \
  --sensitive-patterns "*.csv,*.pkl,*.h5,data/large/*" \
  --backup
```

### Recipe: Recover from Failed Adoption
```bash
# Restore from backup
rm -rf ./failed-project
cp -r ./failed-project-backup ./failed-project

# Try again with safer options
repokit adopt ./failed-project \
  --migration-strategy safe \
  --dry-run \
  --verbose
```

### Recipe: Fix Git Issues
```bash
# Check git status
cd problematic-project
git status
git fsck

# Clean up if needed
git gc --prune=now

# Then adopt
cd ..
repokit adopt ./problematic-project \
  --migration-strategy safe \
  --backup
```

## 🎯 Use Case Specific Recipes

### Recipe: Academic Research Project
```bash
repokit adopt ./research \
  --directories "papers,data,analysis,figures,presentations" \
  --private-dirs "drafts,reviews,personal_notes" \
  --sensitive-patterns "*.pdf,data/raw/*,reviews/*,personal/*" \
  --language python \
  --ai claude \
  --private-repo \
  --description "Research project on computational analysis"
```

### Recipe: Freelance Client Project
```bash
repokit adopt ./client-project \
  --private-repo \
  --organization client-name \
  --sensitive-files "credentials.json,api_keys.txt,.env" \
  --sensitive-patterns "client_data/*,confidential/*,*.key" \
  --backup \
  --backup-location ../client-project-backup-$(date +%Y%m%d) \
  --description "Project for Client Name"
```

### Recipe: Learning/Tutorial Project
```bash
repokit adopt ./learning-project \
  --directories "lessons,exercises,solutions,notes" \
  --private-dirs "personal_notes,drafts" \
  --language python \
  --ai claude \
  --publish-to github \
  --repo-name learning-python-tutorial \
  --description "Learning Python through practical exercises"
```

### Recipe: Hackathon Project
```bash
repokit adopt ./hackathon-project \
  --branch-strategy github-flow \
  --directories "src,demos,presentations" \
  --language javascript \
  --publish-to github \
  --repo-name hackathon-awesome-project \
  --description "Project built during XYZ Hackathon"
```

## 📱 Platform-Specific Tips

### Windows Users:
```bash
# Handle Windows-specific files
repokit adopt ./windows-project \
  --sensitive-patterns "Thumbs.db,desktop.ini,*.lnk,*.tmp" \
  --clean-history \
  --cleaning-recipe windows-safe
```

### Mac Users:
```bash
# Handle Mac-specific files
repokit adopt ./mac-project \
  --sensitive-patterns ".DS_Store,.AppleDouble,.LSOverride,Icon*" \
  --backup
```

### Linux Users:
```bash
# Handle Linux-specific patterns
repokit adopt ./linux-project \
  --sensitive-patterns "*~,*.swp,*.swo,.directory" \
  --language python
```

## 🎉 Success Tips

1. **Always test first**: Use `--dry-run` to preview changes
2. **Always backup**: Use `--backup` for important projects
3. **Start simple**: Begin with basic options, add complexity later
4. **Use verbose output**: Add `-v` or `-vv` for debugging
5. **Read the output**: RepoKit tells you what it's doing

## 📞 Getting More Help

- **Check the docs**: See other files in the `docs/` directory
- **Use verbose mode**: Add `-vv` to see detailed operations
- **Test first**: Always use `--dry-run` when unsure
- **Start simple**: Begin with basic recipes and evolve

---

**Pro Tip**: Save successful commands in a notes file for future reference. Each project type tends to use similar patterns.