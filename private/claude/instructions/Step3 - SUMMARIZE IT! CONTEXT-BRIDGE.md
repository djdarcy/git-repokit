## Summarize It! (aka ContextBridge or ContextBridgeGPT): A Universal Conversation Handoff Instruction (Copy-Paste Version)

We are nearing the token limit *OR* we need to transfer this conversation to a different LLM *OR* we need to make this conversation easily available to other humans (keep all these use cases in mind but the focus is usually with LLMs). Please generate a detailed, structured summary (in an artifact or a Canvas) of our full conversation so we can resume later with full context. This summary should preserve:

### 1. **Topic Overview**

- A detailed nuanced (but concise where possible) summary of what this conversation is about.
- Include the problem, context, and project or domain area.

### 2. **Current Situation**

- What are we working on *right now*?
- What step are we in?
- Mention recent designs, code, configurations, or active problems.

### 3. **Key Artifacts**

- Any files, functions, APIs, schemas, prompts, tools, or systems discussed.
- Summarize important snippets or logic with context.

### 4. **Unresolved Issues / Questions**

- List all open questions, bugs, unknowns, or assumptions yet to be validated.
- Flag possible bugs or risky areas.

### 5. **Next Steps / TODOs**

- What needs to be done next?
- Include a clear list of pending actions.

### 6. **Assumptions / Constraints**

- Any assumptions we are making in logic, design, or scope.
- Include constraints like performance, time, resource limits, or LLM behavior.

### 7. **Decisions Made**

- What has already been decided or ruled out?
- Brief justification for those decisions.

### 8. **External References**

- Links, files, paths, tools, repos, or anything external that matters.

### 9. **Optional: Time Sensitivity / Urgency**

- Deadlines, deployment windows, or time-sensitive info (if applicable).

> The goal is to make it easy for another LLM (or future version of this one) to pick up the conversation immediately without missing key ideas or logic. The summary should be structured, complete, and copy-pasteable into a new chat session.