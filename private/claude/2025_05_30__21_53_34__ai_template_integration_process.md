# AI Template Integration for RepoKit - Using The Process
**Date**: 2025-05-30 21:53:34
**Task**: Design and implement AI-ready templates for RepoKit projects

## 🔁 Stage 1: Problem Analysis

### Core Problem Definition
We need to create a template system that automatically sets up AI-integration files (specifically for Claude Code) when users create new repositories with RepoKit. This should work seamlessly with the existing template system and branch strategies.

### Sub-problems and Dimensions

1. **Template Integration Problem**
   - How to add AI-specific templates to existing template categories
   - Whether to create a new category (e.g., "ai" or "claude") or integrate into existing ones
   - How to make AI templates optional vs default

2. **Branch Strategy Integration**
   - CLAUDE.md should only exist in the private branch
   - Private folder structure should be created appropriately
   - Need to respect existing branch strategies and worktree setups

3. **Content Standardization**
   - What default content should CLAUDE.md contain?
   - What instruction files to include by default?
   - How to make instructions generic enough but still useful?

4. **User Experience**
   - Should AI integration be opt-in or opt-out?
   - Do we need new CLI flags (--ai-integration, --claude, etc.)?
   - How to handle users who don't use AI tools?

5. **Extensibility**
   - Supporting other AI tools beyond Claude (GitHub Copilot, Cursor, etc.)
   - Making the system flexible for future AI integrations
   - Allowing customization of AI templates

### Constraints and Considerations

**Technical Constraints:**
- Must work with existing TemplateEngine class
- Must respect branch strategies (private branch only)
- Must integrate with current file generation flow
- Template substitution using $variable syntax

**User Constraints:**
- Not all users want AI integration
- Some may have security/privacy concerns
- Need to keep it simple for non-AI users

**Short-term vs Long-term:**
- Short-term: Get Claude integration working
- Long-term: Support multiple AI tools, customizable workflows

**Edge Cases:**
- Users without private branch in their strategy
- Custom branch strategies
- Existing projects being migrated
- Multiple AI tools in same project

**Dependencies:**
- Private branch must exist
- Template engine must handle new template locations
- CLI needs to parse any new flags

## 🔁 Stage 2: Conceptual Exploration

### Why This Problem Exists
- AI-assisted development is becoming standard practice
- Current RepoKit has no AI-aware setup
- Manual setup of AI integration is repetitive and error-prone
- Standardization helps teams collaborate with AI tools

### Mental Models and Analogies

1. **Plugin Architecture Model**
   - AI integration as a "plugin" to core RepoKit
   - Similar to how language-specific templates work
   - Modular and optional

2. **Layer Model**
   - AI integration as an additional layer on top of existing structure
   - Doesn't interfere with core functionality
   - Can be added or removed cleanly

3. **Configuration Profile Model**
   - AI setup as a configuration profile
   - Similar to how .gitignore works for different languages
   - Pre-defined but customizable

### Approach Types to Consider

1. **Integrated Approach**
   - AI templates are part of core template system
   - Automatically included based on flags or config
   - Tightly coupled with RepoKit

2. **Modular Approach**
   - AI templates as separate module/package
   - Can be installed/enabled separately
   - Loosely coupled

3. **Progressive Enhancement**
   - Basic setup always included (minimal)
   - Enhanced features added via flags
   - Gradual adoption path

### Relationships Between Elements
- CLAUDE.md → private branch (1:1 relationship)
- Instructions → CLAUDE.md references (dependency)
- Template generation → Branch creation (temporal dependency)
- AI templates → Language templates (parallel relationship)

## 🔁 Stage 3: Brainstorming Solutions

### Solution 1: Minimal Integration
Add AI templates to existing structure with no new flags.

**Implementation:**
- Add `repokit/templates/ai/` directory
- Include CLAUDE.md.template
- Include instruction templates
- Generate only if private branch exists

**Pros:**
- Simple implementation
- No CLI changes needed
- Works with existing flow

**Cons:**
- Always generates AI files (no opt-out)
- Not extensible to other AI tools
- May confuse non-AI users

**Edge Cases:**
- Handles missing private branch gracefully
- Works with all branch strategies

### Solution 2: Flag-Based Integration
Add `--ai` or `--claude` flag to enable AI templates.

**Implementation:**
- New CLI flag: `--ai claude` or `--ai none`
- Conditional template generation
- AI templates in `templates/ai/claude/`

**Pros:**
- Opt-in approach
- Extensible to other AI tools
- Clear user intent
- Can default to 'none' or 'claude'

**Cons:**
- Requires CLI changes
- More complex implementation
- Users might not discover feature

**Edge Cases:**
- Can validate AI choice
- Can warn if private branch missing

### Solution 3: Configuration-Based
Add AI settings to repokit config file.

**Implementation:**
- Add `ai_integration` section to config
- Support multiple AI tools in config
- Template selection based on config

**Pros:**
- Highly flexible
- Supports complex setups
- Can save preferences globally
- Works with existing config system

**Cons:**
- More complex for users
- Requires config documentation
- May over-engineer simple use case

**Edge Cases:**
- Config inheritance works naturally
- Can have project-specific AI setup

### Solution 4: Hybrid Approach
Combine flag and config with smart defaults.

**Implementation:**
- CLI flag for quick setup: `--ai claude`
- Config for detailed control
- Smart defaults (detect .claude directory)
- Templates in `templates/ai/*/`

**Pros:**
- Best of both worlds
- Progressive disclosure
- Future-proof
- Good UX for all users

**Cons:**
- Most complex implementation
- More testing needed
- Documentation complexity

**Edge Cases:**
- Handles all scenarios well
- Graceful degradation

### Solution 5: Post-Creation Hook
Generate AI files after main repo creation.

**Implementation:**
- Add post-creation step
- Separate AI setup phase
- Could be separate command: `repokit add-ai`

**Pros:**
- Completely decoupled
- Can add to existing repos
- Clean separation of concerns

**Cons:**
- Two-step process
- Might be forgotten
- Doesn't feel integrated

**Edge Cases:**
- Works with any repo state
- Can be run multiple times

## 🔁 Stage 4: Synthesis and Recommendation

### Recommended Approach: Enhanced Hybrid Solution

After analyzing all options, I recommend a hybrid approach with smart defaults, combining the best elements:

1. **From Solution 2**: CLI flag for simple activation
2. **From Solution 3**: Config support for advanced users  
3. **From Solution 4**: Smart defaults and progressive disclosure
4. **From Solution 1**: Simple template structure

### Specific Design:

**CLI Interface:**
```bash
# Default behavior (no AI files)
repokit create my-project

# With AI integration
repokit create my-project --ai claude

# Future support
repokit create my-project --ai copilot
```

**Template Structure:**
```
repokit/templates/
├── ai/
│   └── claude/
│       ├── CLAUDE.md.template
│       └── instructions/
│           ├── step1_context_rebuilder.md
│           ├── step2_dev_workflow_process.md
│           └── step3_context_bridge.md
```

**Configuration Enhancement:**
```json
{
  "ai_integration": {
    "provider": "claude",
    "auto_enable": false,
    "templates": {
      "claude": {
        "instruction_files": ["step1", "step2", "step3"]
      }
    }
  }
}
```

**Key Features:**
1. Only generates in private branch
2. Creates `private/claude/` structure
3. Includes our proven instruction files
4. Respects existing patterns
5. Future-proof for other AI tools

### Justification:
- **Solves core problem**: Easy AI integration
- **Handles edge cases**: Works with custom branch strategies
- **Aligns with long-term**: Extensible to other AI tools
- **Balances complexity**: Simple for users, flexible for power users
- **Follows existing patterns**: Similar to language templates

## 🔁 Stage 5: Implementation Plan

### Step 1: Create AI Template Structure
1. Create `repokit/templates/ai/` directory
2. Add `claude/` subdirectory
3. Create CLAUDE.md.template with our content
4. Add instruction file templates

### Step 2: Update CLI
1. Add `--ai` argument to create command
2. Add choices=['none', 'claude'] with default='none'
3. Pass ai_integration to RepoManager config

### Step 3: Modify RepoManager
1. Update `_generate_template_files()` to handle AI templates
2. Add `_generate_ai_templates()` method
3. Ensure only runs when on private branch
4. Create private/claude/ directory structure

### Step 4: Update TemplateEngine
1. Add support for 'ai' category templates
2. Ensure proper path resolution
3. Handle missing AI templates gracefully

### Step 5: Create Template Files
1. Convert our CLAUDE.md to template format
2. Create simplified instruction templates
3. Add placeholder variables for customization

### Step 6: Testing & Documentation
1. Test with various branch strategies
2. Test with/without --ai flag
3. Update README with AI integration section
4. Add example usage

### Success Criteria:
- `repokit create test --ai claude` produces working setup
- CLAUDE.md only exists in private branch
- Instructions are accessible and useful
- No impact on non-AI users
- Clean, maintainable code

### Contingency Plans:
- If template complexity too high: Start with simpler CLAUDE.md
- If CLI changes blocked: Use config-only approach initially
- If private branch issues: Document manual steps as fallback

### Next Actions:
1. Create feature branch for this work
2. Start with template file creation
3. Test manually before code changes
4. Implement incrementally