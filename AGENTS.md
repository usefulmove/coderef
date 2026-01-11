# Context Engineering Protocol

A single-file seed for managing context across LLM agents, sessions, and tools.

## 1. Purpose

This protocol defines how to manage context when working with LLM agents on software projects. The workflow:

1. Drop this file into a project directory
2. Point an agent to it
3. Agent bootstraps the directory structure
4. Agent creates a PRD from conversation with human
5. Documents evolve as work unfolds, staying compact and focused

The goal: maintain the smallest set of high-signal tokens needed for the next step.

## 2. Principles

**Context is finite.** The context window is the agent's working memory. Every token competes for attention. Treat context as a scarce resource.

**Four operations manage context:**

| Operation | Action |
|-----------|--------|
| **Write** | Persist information outside the context window |
| **Select** | Pull relevant information into working context |
| **Compress** | Summarize to retain only essential tokens |
| **Isolate** | Split context across agents or scopes |

**Keep current, not historical.** Documents reflect the present state. Git preserves history. Don't accumulate cruft in docs.

**Progressive disclosure.** Load context only when needed. Frontmatter before full docs. Summaries before details.

## 3. Terminology

| Term | Definition |
|------|------------|
| **Working Context** | Active tokens in the current LLM call. Ephemeral, limited by context budget. |
| **Persistent Context** | Markdown documents that survive across sessions. Includes Core, Stories, Reference, Skills, and Logs. |
| **Reference Context** | Queryable external sources: codebase (LSP, grep), RAG indexes, web. Not stored in the doc system. |
| **Compaction** | Summarizing working context into persistent context before it's lost. |
| **Context Budget** | The token limit of the model's context window. |
| **Context Scope** | Per-story declaration of file boundaries: what the agent can write, read, or must exclude. |

**Hierarchy:**

```
WORKING CONTEXT (ephemeral, token-limited)
    |
    | <- Select (load)     -> Write (persist)
    v                         v
PERSISTENT CONTEXT (markdown, durable)
  |-- Core Docs (PRD, Architecture, Standards)
  |-- Stories (active tasks)
  |-- Reference (conventions, completed work)
  |-- Skills (on-demand capabilities)
  |-- Logs (session summaries)

REFERENCE CONTEXT (external, queryable)
  |-- Codebase (LSP, grep, git)
  |-- RAG indexes
  |-- External sources (web, APIs)
```

## 4. Directory Structure

```
docs/
  core/           # Foundational docs (rarely change)
    PRD.md        # Problem, goals, scope, requirements
    ARCHITECTURE.md  # System design (when needed)
    STANDARDS.md  # Coding conventions, patterns
  stories/        # Active units of work
  reference/      # Read-only knowledge
    completed/    # Archived stories
  skills/         # On-demand capabilities (Agent Skills format)
  logs/           # Session summaries
```

## 5. Bootstrapping

When an agent encounters this file in a new project:

**Step 1: Create structure**
```bash
mkdir -p docs/{core,stories,reference/completed,skills,logs}
```

**Step 2: Gather context**
Prompt the human for:
- What problem are we solving?
- What does success look like?
- What's in scope? What's out?
- Any known constraints?

**Step 3: Generate PRD**
Create `docs/core/PRD.md` from the conversation.

**Step 4: Architecture (if needed)**
For non-trivial systems, create `docs/core/ARCHITECTURE.md`.

**Step 5: First story**
If the scope is clear, create the first story in `docs/stories/`.

**Step 6: Begin work**

## 6. Document Lifecycle

**Core Docs** (PRD, Architecture, Standards)
- Update in place when scope or direction changes
- Keep current—don't preserve history in the doc
- These are the source of truth

**Stories**
- Create when planning work
- Update during execution (notes, learnings)
- Move to `docs/reference/completed/` when done

**Reference**
- Conventions, patterns, and completed stories
- Read-only during execution
- Prune when no longer relevant

**Skills**
- Add as capabilities are needed
- Update when procedures change
- Remove when obsolete

**Logs**
- Append session summaries after compaction
- Prune older logs when they no longer inform future work

## 7. Context Scope

Every story declares its context boundaries:

```markdown
## Context Scope

**Write** (files this task will modify):
- src/auth/login.ts
- src/auth/session.ts

**Read** (files for reference only):
- docs/core/ARCHITECTURE.md
- src/auth/types.ts

**Exclude** (ignore these):
- src/legacy/
- *.test.ts
```

**Enforcement:**
- Agent must not modify files outside Write scope
- Agent should consult Read files before making changes
- Agent should avoid loading Excluded paths into context
- Scope changes require explicit human approval

## 8. Skills

Skills are discoverable, on-demand capabilities. They follow the [Agent Skills specification](https://agentskills.io/specification).

**Location:** `docs/skills/`

**Structure:**
```
docs/skills/
  skill-name/
    SKILL.md           # Required: frontmatter + instructions
    scripts/           # Optional: executable code
    references/        # Optional: additional docs
    assets/            # Optional: templates, data files
```

**Required frontmatter:**
```yaml
---
name: skill-name
description: What this does and when to use it.
---
```

**Progressive disclosure:**
1. Agent scans `docs/skills/` directories at session start
2. Agent reads frontmatter (~100 tokens per skill) for discovery
3. Agent loads full `SKILL.md` only when activating a skill
4. Agent loads `scripts/`, `references/`, `assets/` only when needed

**Skills may reference other skills.** Agent follows references as needed.

## 9. Compaction

Compaction moves insights from working context to persistent context.

**Triggers:**
- Approaching context budget (~80% utilization)
- Completing a story or major task
- Conversation becoming circular or confused
- Ending a session

**Process:**
1. Summarize key decisions and insights
2. List artifacts created or modified
3. Note open items and next steps
4. Write summary to `docs/logs/YYYY-MM-DD-topic.md`
5. Update core docs if new patterns or decisions emerged
6. Continue with fresh working context

## 10. Templates

Templates are guidelines, not rigid forms. Start minimal, expand as needed.

### PRD

**Start with (required):**

```markdown
# [Project Name] PRD

## Problem
What problem are we solving? Why does it matter?

## Goals
What does success look like? How will we measure it?

## Scope
**In scope:**
- ...

**Out of scope:**
- ...
```

**Expand when ready:**

```markdown
## Requirements
**Functional:**
- ...

**Non-functional:**
- ...

## Constraints
- ...
```

### Architecture

Create when the system has multiple components or non-obvious structure.

```markdown
# [Project Name] Architecture

## Overview
High-level description of the system.

## Components
| Component | Responsibility |
|-----------|----------------|
| ... | ... |

## Key Decisions
| Decision | Rationale |
|----------|-----------|
| ... | ... |

## Tech Stack
- ...

## Integration Points
- ...
```

### Story

```markdown
# [STORY-ID] [Title]

## Goal
What are we trying to accomplish? Why now?

## Acceptance Criteria
- [ ] ...
- [ ] ...

## Context Scope
**Write:**
- ...

**Read:**
- ...

**Exclude:**
- ...

## Approach
High-level implementation strategy.

## Notes
(Fill during/after implementation)
```

### Session Summary

```markdown
# Session: [Topic]
**Date:** YYYY-MM-DD

## Overview
What was accomplished this session.

## Key Decisions
- ...

## Artifacts Modified
- ...

## Open Items
- ...

## Next Steps
- ...
```

## 11. Agent Guidelines

**Search first.** Exhaust search tools (grep, glob, LSP) before asking for file paths or context.

**Read before writing.** Always consult the Context Scope. Read the Read files before modifying Write files.

**Update, don't accumulate.** Modify existing docs to reflect current state. Don't append history—git tracks that.

**Compact proactively.** Don't wait for context overflow. Summarize and persist insights regularly.

**Stay in scope.** Don't modify files outside the story's Write scope without explicit approval.

**Be concise.** Terse, technical communication. No filler.
