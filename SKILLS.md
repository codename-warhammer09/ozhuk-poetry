# Agent Skills & Operating Disciplines for Claude Code

This file defines the active behavioral modes and slash-command skills available in this workspace. When a command is called or an intent is triggered, adopt the corresponding protocol strictly.

---

## 1. Skill: `/grill-me` (Relentless Pre-Implementation Interrogation)
**Trigger:** User says `/grill-me`, "grill me", "stress-test this plan", or presents a new design/feature spec.
**Objective:** Interrogate the user relentlessly about every branch of the design tree until reaching shared understanding. Never allow a half-baked plan to touch code.

### Grilling Rules & Execution Discipline:
1. **One question per turn:** Never bundle multiple architectural questions into a single message.
2. **Always provide a recommendation:** Never ask lazy open questions like *"What do you think?"*. Always provide your recommended default choice with a 1-sentence rationale so the user can just answer *"Yes"* or choose an alternative.
3. **Explore the codebase first:** Before asking a question, use grep/read to see if the codebase already answers it. If you found evidence in code, state it: *"I checked `auth.py` and noticed JWT is used; I assume we follow this pattern. Confirm?"*
4. **Depth-first tree traversal:** Walk down one dependency branch completely before opening another.
5. **No execution during grilling:** Do not write or edit production files while a grilling session is active.
6. **Session Conclusion:** Once all decision branches are resolved, output:
   - **Status:** `[Shared Understanding Reached]`
   - **Locked Decisions Table:** (Decision | Rationale | Impacted Files)
   - Ask for explicit user sign-off to proceed to execution.

---

## 2. Skill: `/sanity-check` (The "Don't Be An Idiot" Output Filter)
**Trigger:** Pre-commit reviews, before applying large diffs, or when invoked with `/sanity-check`.
**Objective:** Run an adversarial post-generation verification pass to eliminate hallucinations, lazy placeholders, and regressions.

### Checklist Before Presenting/Writing Code:
- **No Pseudo-code/Stubs:** Zero `// TODO: implement later` or `pass` in critical paths.
- **Dependency Audit:** Did we introduce unpinned or unnecessary libraries? Can standard library or existing dependencies do this?
- **Breaking Changes:** Did we change any public signature, schema, or route without updating callers?
- **Secret Leaks:** Ensure `.env`, API tokens, or hardcoded credentials are never embedded in code, git commits, or tests.
- **Fail Loudly:** Ensure network calls, JSON deserialization, and subprocesses have explicit error handling rather than silent `except: pass`.

---

## 3. Skill: `/archaeologist` (Git & Repo Context Archaeology)
**Trigger:** Refactoring unfamiliar files, addressing legacy bugs, or when invoked with `/archaeologist <path>`.
**Objective:** Understand *why* code exists in its current form before altering it (Chesterton’s Fence).

### Protocol:
42	1. Run `git log -p -S <symbol>` or inspect recent commits touching the file.
43	2. Identify the "Chesterton's Fence": Why was this specific implementation chosen?
44	3. Trace dependencies back to the original intent.
45	
46	---
47	
48	## 4. Environment-Provided Tool Skills
49	
50	The following skills are available via the Claude Code harness and the `Skill` tool.
51	
52	### DevRelay
53	- `devrelay-challenges`: Active DEV Challenges, MLH hackathons, and community events.
54	- `devrelay-community-wisdom`: Search dev.to developer reports for library/architecture recommendations.
55	- `devrelay-knowledge`: Reference guides for MLH, Global Hack Week, and DEV community.
56	- `devrelay-mlh-submissions`: Handle MLH submissions.
57	- `devrelay-navigator`: Navigation for DevRelay services.
58	- `devrelay-offers`: DevRelay offers and sponsorship info.
59	- `devrelay-publishing`: Publishing to DEV.
60	- `devrelay-sessions`: Save, curate, and embed session transcripts on DEV.
61	- `devrelay-sponsor-skills`: Access sponsor-specific agent skills.
62	
63	### Development & Utility
64	- `dataviz`: Guidelines and tools for creating charts, graphs, and dashboards.
65	- `update-config`: Configure Claude Code harness via `settings.json`.
66	- `keybindings-help`: Customize keyboard shortcuts and `keybindings.json`.
67	- `code-review`: Review diffs/PRs for bugs and efficiency.
68	- `simplify`: Review code for reuse and simplification.
69	- `fewer-permission-prompts`: Optimize `settings.json` allowlists to reduce prompts.
70	- `loop`: Run tasks on a recurring interval.
71	- `claude-api`: Reference for Claude API / Anthropic SDK.
72	- `workflow-authoring`: Reference for writing Workflow tool scripts.
73	- `run`: Launch and drive the project app.
74	- `plugin-authoring`: Create mods for Claude's interface/behavior.
75	- `init`: Project initialization.
76	- `security-review`: Perform security audits on code.
