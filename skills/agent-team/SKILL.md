---
name: agent-team
description: Use this skill when the user asks for Agent Team mode, team-based orchestration, subAgent delegation with named roles, or a reusable multi-agent workflow. This skill defines an Orchestrator-led team with Product/PM, Architect, Developer, QA, Code Reviewer, Docs, and Release/Ops responsibilities, plus rules for when to spawn subagents, how to assign ownership, and how to merge results safely across projects.
---

# Agent Team

## Overview

Use this skill when the user wants work handled in an Agent Team structure instead of by a single agent. The main agent stays the Orchestrator and may delegate bounded subtasks to subagents when delegation is explicitly allowed by the user and materially improves speed or quality.

This skill standardizes a reusable team shape across projects:

- `Orchestrator`
- `Product / PM Agent`
- `Architect Agent`
- `Developer Agent`
- `QA Agent`
- `Code Reviewer Agent`
- `Docs Agent`
- `Release / Ops Agent`

## Activation Rules

Use this skill when the user says or clearly implies any of the following:

- "Use Agent Team mode"
- "Enable subAgent"
- "Delegate this"
- "Split by roles"
- "Let multiple agents work in parallel"
- "Use the team structure"

Do not spawn subagents unless the user explicitly allows delegation, parallel agents, subagents, or Agent Team mode in the current request. This skill does not override platform rules about when subagents are allowed.

## Core Operating Model

The Orchestrator owns the task end to end. Subagents support the Orchestrator; they do not replace it.

The Orchestrator should:

1. Build a short execution plan.
2. Decide what stays on the critical path and must be done locally.
3. Delegate only sidecar or clearly bounded work that can proceed independently.
4. Give each subagent a named role, a clear deliverable, and explicit ownership.
5. Integrate outputs, resolve conflicts, run validation, and produce the final answer.

Keep the team lightweight. Do not spawn every role by default. Use only the roles that materially help the current task.

For ready-to-send user prompt patterns, see [references/prompts.md](references/prompts.md).

## Role Mapping

These are human-readable team roles layered on top of the currently available subagent types.

Default execution profile:

- `Architect Agent`, `Developer Agent`, and `Code Reviewer Agent` default to `model="gpt-5.3-codex"` with `reasoning_effort="high"`.
- Do not rely on inherited subagent defaults for those roles. In some runtimes, spawned agents may otherwise fall back to a mini or medium profile.

### Orchestrator

- Runs as the main agent.
- Owns planning, sequencing, integration, validation, and final communication.
- Keeps work local when the next step is blocked on the answer.

### Product / PM Agent

- Preferred runtime: `default`
- Use for: clarifying task scope, acceptance criteria, user stories, task decomposition, risk framing, rollout sequencing, and tradeoff summaries.
- Deliverables: task brief, acceptance checklist, scope notes, rollout recommendation.

### Architect Agent

- Preferred runtime: `explorer`
- Fallback runtime: `default`
- Default model profile: explicitly spawn with `gpt-5.3-codex` and `high` reasoning.
- Use for: codebase reconnaissance, architecture mapping, dependency analysis, interface design, migration paths, and implementation options.
- Deliverables: recommended approach, touched systems, constraints, file map, risk list.

### Developer Agent

- Preferred runtime: `worker`
- Default model profile: explicitly spawn with `gpt-5.3-codex` and `high` reasoning.
- Use for: implementing a bounded code change in an explicitly assigned write scope.
- Deliverables: code changes, changed file list, notable assumptions, local verification notes.

### QA Agent

- Preferred runtime: `worker`
- Use for: writing or adjusting tests, reproducing bugs, validating edge cases, checking regressions, and running higher-confidence validation for user-facing flows.
- Deliverables: test additions, repro notes, validation steps, failing or passing results.
- Tooling note: When browser-based end-to-end validation is necessary, QA may explicitly use an available `$playwright` skill for real-browser automation, snapshots, screenshots, and UI-flow debugging.

### Code Reviewer Agent

- Preferred runtime: `worker`
- Default model profile: explicitly spawn with `gpt-5.3-codex` and `high` reasoning.
- Use for: independent review of changed code, risk detection, missing tests, maintainability concerns, and regression scanning.
- Deliverables: findings ordered by severity, open questions, residual risks.

### Docs Agent

- Preferred runtime: `worker`
- Use for: updating docs, READMEs, runbooks, migration notes, examples, and user-facing instructions.
- Deliverables: doc updates, usage notes, upgrade steps, change summary.

### Release / Ops Agent

- Preferred runtime: `worker`
- Use for: packaging, release notes, deployment steps, env/config checks, operational validation, and rollback guidance.
- Deliverables: release checklist, commands, config diffs, rollout notes, rollback notes.

## Delegation Rules

Only delegate when all of the following are true:

1. The user has explicitly allowed subagents, delegation, or Agent Team mode.
2. The delegated task is concrete, self-contained, and materially useful.
3. The delegated task is not the immediate blocking step on the critical path.
4. The write scope can be kept isolated, or the task is read-only.

Keep work local when:

- the answer is needed immediately for the next step
- the task is too coupled to ongoing edits
- the write scope is unclear
- the problem is small enough that delegation would add overhead

When spawning `Architect Agent`, `Developer Agent`, or `Code Reviewer Agent`, explicitly pass these tool arguments on `spawn_agent`:

- `model: "gpt-5.3-codex"`
- `reasoning_effort: "high"`

Use Playwright under QA only when at least one of these is true:

- the task changes browser UI flows, forms, or navigation
- the user wants end-to-end coverage or a real-browser check
- screenshots or visual proof would materially help
- the bug reproduces only in an interactive browser flow
- integration confidence is more important than unit-level speed

Prefer non-browser validation when:

- the change is backend-only
- unit or integration tests already cover the risk well
- the UI is not part of the acceptance criteria
- browser setup cost would exceed the value of the check

## Ownership Rules

When assigning a `worker`, always state:

- exact responsibility
- owned files or directories
- files it must not modify unless necessary
- expected output format

Tell each worker that it is not alone in the codebase, must not revert others' work, and should adapt to concurrent edits when they appear.

Prefer these ownership patterns:

- `Developer Agent`: feature files or one subsystem
- `QA Agent`: test files only, unless a tiny production hook is required
- `Docs Agent`: docs and examples only
- `Release / Ops Agent`: deployment, CI, scripts, and config paths only

When QA uses Playwright:

- QA owns browser validation steps, captured artifacts, and test notes
- Prefer storing artifacts under `output/playwright/` when working in a repo
- QA should not introduce Playwright spec files unless the user explicitly asks for test files
- Default to CLI-style browser automation and evidence capture, not framework migration

If two roles would edit the same file, keep one of them local with the Orchestrator or sequence the work instead of parallelizing it.

## Default Team Playbooks

### Product + Architect

Use at the start of ambiguous or large tasks.

- `Product / PM Agent` refines scope and acceptance criteria.
- `Architect Agent` maps the system and recommends an approach.
- The Orchestrator uses both outputs to decide whether to proceed, ask a clarifying question, or implement directly.

### Architect + Developer + QA

Use for medium or large code changes.

- `Architect Agent` identifies the safest implementation path.
- `Developer Agent` implements within a bounded write scope.
- `QA Agent` prepares or runs validation in a non-overlapping scope.
- If the change affects real browser flows, interactive UI behavior, or user-visible regressions that are hard to validate otherwise, QA may use Playwright for end-to-end checks.

### Developer + Code Reviewer + Docs

Use when implementation is clear and speed matters.

- `Developer Agent` ships the code.
- `Code Reviewer Agent` performs an independent pass on risk and missing tests.
- `Docs Agent` updates usage or migration docs.

### Developer + QA + Release / Ops

Use for changes near deployment or config.

- `Developer Agent` edits the product code.
- `QA Agent` validates behavior and regressions.
- `Release / Ops Agent` checks rollout and rollback readiness.

## Default Role Selection Strategy

When the user enables Agent Team mode but does not specify which roles to use, choose the smallest team that covers the task well.

### Tiny tasks

Use for:

- one-file fixes
- small refactors
- quick answers with minimal repo impact

Default roles:

- `Orchestrator` only

Optional add-on:

- `Architect Agent` if a quick read-only codebase lookup would save time

### Small implementation tasks

Use for:

- isolated bug fixes
- focused feature edits
- bounded config or script updates

Default roles:

- `Architect Agent`
- `Developer Agent`

Add `QA Agent` when behavior is testable or regression-prone.
If the task is UI-heavy or flow-heavy, QA may use Playwright.
Add `Docs Agent` when usage, config, or workflows change.

### Medium engineering tasks

Use for:

- multi-file changes
- API or schema-touching work
- feature work with moderate regression risk

Default roles:

- `Architect Agent`
- `Developer Agent`
- `QA Agent`

Add `Code Reviewer Agent` when the risk of subtle regressions is meaningful.
Add `Docs Agent` when the user-facing workflow or setup changes.
Add `Release / Ops Agent` when env, config, CI, or rollout needs attention.

### Large or ambiguous tasks

Use for:

- architecture changes
- migrations
- cross-cutting refactors
- broad product or platform work

Default roles:

- `Product / PM Agent`
- `Architect Agent`

Then add:

- `Developer Agent` for implementation
- `QA Agent` for validation
- `Code Reviewer Agent` for independent review
- `Docs Agent` and `Release / Ops Agent` as needed

## Orchestrator Prompting Checklist

When you delegate, include:

- the team role name
- the exact task
- the owned scope
- the expected deliverable
- any constraints on files, tests, or tools
- whether the task is read-only or may edit files

Keep delegated tasks concrete. Bad: "Explore the codebase and help." Good: "As Architect Agent, map the auth flow in `src/auth` and list the files touched by token refresh."

## Integration Checklist

Before finalizing:

- collect all delegated outputs
- check for conflicting edits or assumptions
- run the required validation locally or via the appropriate role
- summarize residual risks and any omitted checks
- ensure the final answer reflects integrated results, not raw subagent transcripts

## Anti-Patterns

Avoid these mistakes:

- delegating the immediate blocking step and then waiting idly
- spawning too many roles for a small task
- giving overlapping write scopes to multiple workers
- turning `Product / PM Agent` into a generic explainer when a brief local note would do
- using QA for browser automation when cheaper validation covers the risk
- using this skill to bypass platform rules on subagent use
