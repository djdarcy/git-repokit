# Branch Strategies: Choosing the Right Workflow for Your Project

This guide explains RepoKit's branch strategies and helps you choose the right one for your project type and team size.

## 📋 Table of Contents

1. [Understanding Branch Strategies](#understanding-branch-strategies)
2. [Simple Strategy (Recommended)](#simple-strategy-recommended)
3. [GitFlow Strategy](#gitflow-strategy)
4. [GitHub Flow Strategy](#github-flow-strategy)
5. [Minimal Strategy](#minimal-strategy)
6. [Custom Strategies](#custom-strategies)
7. [When to Use Each Strategy](#when-to-use-each-strategy)
8. [Working with Your Chosen Strategy](#working-with-your-chosen-strategy)

## 🤔 Understanding Branch Strategies

A branch strategy defines how you organize your code development using Git branches. Think of branches as parallel universes for your code:

- **Private Branch**: Your personal lab where you experiment freely
- **Development Branches**: Where you build and test features
- **Main Branch**: The polished version ready for the world

Different strategies organize these branches differently based on project needs.

## 🎯 Simple Strategy (Recommended)

**Best for**: Most projects, solo developers, small teams, beginners

### Branch Structure:
```
private     # Your personal workspace (never shared)
    ↓
dev         # Development and testing
    ↓
main        # Clean, deployable version
```

### How It Works:

1. **Work in `private`**: Experiment, take notes, make messy commits
2. **Test in `dev`**: Clean up features, run tests, collaborate
3. **Deploy from `main`**: Only polished, working code

### Directory Layout:
```
my-project/
├── local/      # private branch - your personal workspace
├── dev/        # dev branch - development and testing
└── github/     # main branch - clean version for GitHub
```

### Typical Workflow:
```bash
# Start in your private workspace
cd my-project/local
# Make changes, experiment freely
git add . && git commit -m "working on new feature"

# When ready, merge to dev for testing
cd ../dev
git merge private --no-ff --no-commit
# Test, fix issues, commit clean version

# When stable, merge to main for deployment
cd ../github
git merge dev --no-ff --no-commit
# Final polish, then commit and push to GitHub
```

### Advantages:
- ✅ Simple to understand and use
- ✅ Safe experimentation in private
- ✅ Always have a clean public version
- ✅ Good for learning Git fundamentals

### Use Command:
```bash
repokit adopt ./my-project --branch-strategy simple
```

## 🌊 GitFlow Strategy

**Best for**: Large projects, multiple developers, scheduled releases

### Branch Structure:
```
private         # Your personal workspace
    ↓
feature/*       # Individual features
    ↓
develop         # Integration branch
    ↓
release/*       # Release preparation
    ↓
main           # Stable releases
    ↓
hotfix/*       # Emergency fixes
```

### How It Works:

1. **Features developed in `feature/` branches**: Each new feature gets its own branch
2. **Integration in `develop`**: All features merge here for testing
3. **Releases via `release/` branches**: Prepare and polish releases
4. **Stable code in `main`**: Only tested, released versions
5. **Emergency fixes via `hotfix/`**: Critical fixes go directly to main

### Typical Workflow:
```bash
# Create feature branch
git checkout develop
git checkout -b feature/user-auth

# Develop feature
# ... work on authentication ...

# Merge to develop
git checkout develop
git merge feature/user-auth

# Create release
git checkout -b release/1.2.0
# ... finalize release ...

# Merge to main and develop
git checkout main
git merge release/1.2.0
git checkout develop  
git merge release/1.2.0
```

### Advantages:
- ✅ Excellent for team coordination
- ✅ Clear separation of features and releases
- ✅ Supports parallel development
- ✅ Good for scheduled release cycles

### Disadvantages:
- ❌ More complex than Simple strategy
- ❌ Can slow down development
- ❌ Requires discipline from team

### Use Command:
```bash
repokit adopt ./my-project --branch-strategy gitflow
```

## 🐙 GitHub Flow Strategy

**Best for**: Continuous deployment, web applications, small teams

### Branch Structure:
```
private         # Your personal workspace
    ↓
feature/*       # Short-lived feature branches
    ↓
main           # Always deployable
```

### How It Works:

1. **`main` is always deployable**: Every commit should work in production
2. **Features in short-lived branches**: Create, develop, merge quickly
3. **Continuous deployment**: Deploy from main frequently

### Typical Workflow:
```bash
# Create feature branch from main
git checkout main
git checkout -b feature/quick-fix

# Develop quickly
# ... make changes ...

# Merge directly to main
git checkout main
git merge feature/quick-fix

# Deploy immediately
git push origin main
```

### Advantages:
- ✅ Simple and fast
- ✅ Great for continuous deployment
- ✅ Encourages small, frequent changes
- ✅ Minimal overhead

### Disadvantages:
- ❌ Requires excellent testing
- ❌ Less suitable for scheduled releases
- ❌ Can be risky without good CI/CD

### Use Command:
```bash
repokit adopt ./my-project --branch-strategy github-flow
```

## 🔧 Minimal Strategy

**Best for**: Personal projects, experiments, learning

### Branch Structure:
```
private         # Your personal workspace
    ↓
main           # Public version
```

### How It Works:

1. **Work in `private`**: All development happens here
2. **Clean up for `main`**: Manually clean and organize for public

### Typical Workflow:
```bash
# Work in private
cd my-project/local
# ... develop everything ...

# Clean up for public
cd ../github
# Manually copy/clean files for public consumption
```

### Advantages:
- ✅ Extremely simple
- ✅ Low overhead
- ✅ Good for learning

### Disadvantages:
- ❌ No development branch for testing
- ❌ More manual work
- ❌ Less suitable for collaboration

### Use Command:
```bash
repokit adopt ./my-project --branch-strategy minimal
```

## ⚙️ Custom Strategies

You can define your own branch strategy by specifying branches manually:

```bash
# Custom branches
repokit adopt ./my-project \
  --branches "main,staging,production" \
  --default-branch main \
  --private-branch development

# With custom worktrees
repokit adopt ./my-project \
  --branches "main,testing,staging,production" \
  --worktrees "main,staging,production"
```

## 🎯 When to Use Each Strategy

### Choose **Simple** when:
- ✅ You're new to Git or RepoKit
- ✅ Working solo or with a small team (2-3 people)
- ✅ Building most types of projects
- ✅ Want to learn good Git habits
- ✅ Need something that "just works"

### Choose **GitFlow** when:
- ✅ Large team (5+ developers)
- ✅ Scheduled releases (v1.0, v2.0, etc.)
- ✅ Complex project with multiple features
- ✅ Need strict quality control
- ✅ Traditional software development

### Choose **GitHub Flow** when:
- ✅ Web applications with continuous deployment
- ✅ Small, agile team
- ✅ Excellent automated testing
- ✅ Deploy multiple times per day
- ✅ SaaS or web services

### Choose **Minimal** when:
- ✅ Personal learning projects
- ✅ Experiments and prototypes
- ✅ Very simple tools or scripts
- ✅ Want absolute simplicity

## 🛠️ Working with Your Chosen Strategy

### Daily Workflow Examples

#### Simple Strategy Daily Workflow:
```bash
# Morning: Start in private
cd my-project/local
git status
# Work on features

# Afternoon: Test in dev
cd ../dev
git merge private --no-ff --no-commit
# Test everything works
git commit -m "feat: add user authentication"

# Evening: Deploy to main
cd ../github
git merge dev --no-ff --no-commit
# Final check, then commit and push
```

#### GitFlow Daily Workflow:
```bash
# Start feature
git checkout develop
git checkout -b feature/payment-system

# Work on feature
# ... develop payment system ...

# Finish feature
git checkout develop
git merge feature/payment-system
git branch -d feature/payment-system
```

### Best Practices for All Strategies:

1. **Commit often in private**: Don't worry about perfect commits
2. **Clean up before merging**: Make public commits meaningful
3. **Test before promoting**: Each branch should be more stable than the last
4. **Use meaningful commit messages**: Especially in public branches

### Migration Between Strategies:

You can change strategies later:
```bash
# Start with simple
repokit adopt ./my-project --branch-strategy simple

# Later upgrade to gitflow
cd my-project/local
git checkout -b develop main
git checkout -b feature/new-feature develop
# Continue with gitflow workflow
```

## 📚 Strategy Comparison

| Feature | Simple | GitFlow | GitHub Flow | Minimal |
|---------|---------|---------|-------------|---------|
| **Complexity** | Low | High | Medium | Very Low |
| **Team Size** | 1-5 | 5+ | 2-8 | 1 |
| **Release Style** | Flexible | Scheduled | Continuous | Ad-hoc |
| **Learning Curve** | Easy | Steep | Medium | Minimal |
| **Flexibility** | High | Medium | High | Very High |
| **Safety** | High | Very High | Medium | Low |

## 🚀 Getting Started

1. **Choose your strategy** based on the guidelines above
2. **Adopt with strategy**:
   ```bash
   repokit adopt ./my-project --branch-strategy simple
   ```
3. **Learn the workflow** for your chosen strategy
4. **Practice** with small changes first
5. **Evolve** as your project grows

## 📞 Need Help?

- **Start simple**: When in doubt, use the Simple strategy
- **Experiment**: Try different strategies with test projects
- **Ask for guidance**: Check the adoption guide or project documentation
- **Practice**: The best way to learn is by doing

---

**Remember**: The best branch strategy is the one your team actually uses consistently. Start simple and evolve as needed.