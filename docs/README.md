# RepoKit Documentation Guide

This directory contains comprehensive documentation for RepoKit. Here's the recommended reading order based on your needs:

## 🆕 New to RepoKit? Start Here

1. **[Why RepoKit Exists](Why-RepoKit-Exists.md)** ⭐ *Start here*
   - Simple explanation of the problem RepoKit solves
   - Before/after comparisons showing the transformation
   - Perfect for understanding the value proposition

2. **[Main README](../README.md)** 
   - Quick overview, installation, and basic usage
   - Links to all other documentation

## 🛠️ Ready to Use RepoKit?

3. **[Adoption Guide](Adoption-Guide.md)** ⭐ *Primary tutorial*
   - Step-by-step tutorials for adopting existing projects
   - Real examples from simple folders to GitHub deployment
   - Troubleshooting and best practices

4. **[Recipes and How-Tos](Recipes-And-Howtos.md)** ⭐ *Recipe book*
   - Copy-paste commands for common scenarios
   - Language-specific examples (Python, JavaScript, etc.)
   - GitHub deployment recipes

## 🌳 Understanding Workflows

5. **[Branch Strategies](Branch-Strategies.md)**
   - Explanation of different branching approaches
   - When to use simple vs. GitFlow vs. GitHub Flow
   - Custom branch configuration

## 📂 Documentation Structure

```
docs/
├── README.md                 # This guide (start here)
├── Why-RepoKit-Exists.md    # The "why" - problem and solution
├── Adoption-Guide.md         # The "how" - step-by-step tutorials  
├── Recipes-And-Howtos.md    # The "cookbook" - copy-paste examples
├── Branch-Strategies.md      # The "workflow" - branching explained
├── Auth-Guide.md            # Authentication setup
├── Migration-Guide.md       # Legacy migration scenarios
├── Workflow-Guide.md        # Development workflows
└── Deployment-Demo.md       # Deployment examples
```

## 🎯 Quick Navigation by Goal

### "I want to understand what RepoKit does"
→ [Why RepoKit Exists](Why-RepoKit-Exists.md)

### "I have a messy project folder and want to organize it"
→ [Adoption Guide](Adoption-Guide.md) → Section: Basic Adoption Tutorial

### "I want to put my project on GitHub professionally"
→ [Adoption Guide](Adoption-Guide.md) → Section: GitHub Deployment Tutorial

### "I need a specific command for my use case"
→ [Recipes and How-Tos](Recipes-And-Howtos.md)

### "I want to understand the branching workflow"
→ [Branch Strategies](Branch-Strategies.md)

### "I'm working with a complex/legacy codebase"
→ [Migration Guide](Migration-Guide.md)

## 💡 Pro Tips

- **Always start with `--dry-run`** to preview changes
- **Use `--backup`** for safety when adopting existing projects
- **Read the recipes** - they contain real-world tested commands
- **Check the troubleshooting sections** if you encounter issues

## 🆘 Getting Help

- **CLI Help**: `repokit --help` or `repokit adopt --help`
- **Examples**: Every command has examples in the help text
- **Issues**: [GitHub Issues](https://github.com/djdarcy/git-repokit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/djdarcy/git-repokit/discussions)

---

*This documentation is organized to get you productive quickly while providing depth when you need it.*