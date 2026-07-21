# Agent Required Reading: Mathematical Modeling Team Repository

> Read this file before every task. Current confirmed operator for this agent: **[A]**. Every action, handoff, generated-file attribution, and local commit made by this agent uses `[A]` until the user explicitly changes it.

## 1. Purpose and non-negotiable facts

This repository supports training, mock contests, official contests, coursework, code, validation, paper writing, and archiving for a three-person mathematical-modeling team. Repository files are the source of truth; chat, screenshots, and unverified AI output are not evidence.

`[A]`, `[B]`, and `[C]` identify operators, not fixed roles. Confirm the active operator at a new conversation unless recorded above. Modeling Lead, Validation Lead, and Paper Lead are assigned per task; do not infer them from an operator code.

## 2. Required first-minute checklist

1. Read this file, root `README.md`, and the relevant task files.
2. Run `git status --short`, `git status --ignored --short`, and `git branch --show-current`.
3. Confirm the branch, operator, role, exact files to change, and any overlap with another person's uncommitted work.
4. Stop for conflicts, unfinished merge/rebase/cherry-pick, unsafe branch identity, or unclear ownership.
5. For project work also read `01_architecture/full-problem-architecture.md`, `01_architecture/model-decision-log.md`, and `08_results/final-results.md`.

Never discard others' work. Do not use `git reset --hard`, `git clean -fd`, `git checkout -- .`, `git restore .`, or automatic stash.

## 3. Project structure and ownership

| Area | Main responsibility | Purpose |
| --- | --- | --- |
| `00_problem/` | all, read-only | official problem and attachments |
| `01_architecture/`, `02_references/`, `04_code/`, `06_figures/` | Modeling Lead | route, model V0, code, formal figures |
| `03_data/`, `05_validation/`, `08_results/` | Validation Lead | data audit, reproduction, validation, numeric registry |
| `07_paper/`, `09_submission/` | Paper Lead | manuscript and delivery artifacts |

`07_paper/main.tex` belongs to the designated Paper Lead. Modeling and validation notes go to their `paper-notes/` directories. `08_results/final-results.md` is the single formal numerical source: do not state a key number in paper, table, or caption unless it matches that file.

## 4. SOP: one-question rolling loop

```text
joint problem analysis
  → parallel foundation (architecture / data+validation / paper framework)
  → V0: Modeling Lead supplies runnable technical package
  → V1: Validation Lead independently reproduces, tests, and may veto
  → draft: Paper Lead writes only evidence-backed material
  → review: technical meaning and claim boundary are checked
  → Frozen: approved interface for the next question
```

V0 must define inputs, outputs, variables, units, constraints, assumptions, code entry point, preliminary evidence, alternatives, and risks. V1 must check data, units, formulas, constraints, reproducibility, baseline, error/convergence/sensitivity where relevant, and evidence boundaries. Do not write a formal conclusion from unreviewed V0. Freeze only after technical review; then preserve the handoff files and status.

## 5. Status, evidence, and file rules

Use only `planned`, `in progress`, `validated`, and `frozen`. Every material handoff records operator code, changed paths, status, evidence paths, risks, and next owner. Never fabricate data, literature, experiments, citations, or results.

- Raw data in `03_data/raw/` are immutable; derivations go in `03_data/processed/`.
- Important process CSV goes in `08_results/intermediate/`; validation CSV in `05_validation/q*/`; only Validation-Lead-approved data enters `08_results/final/` and the numerical registry.
- TEX is the editable authoritative result source; same-basename PDF is human preview. Edit TEX, never PDF; recompile after TEX changes. TEX/PDF conflicts resolve in favor of TEX.
- Names use lowercase English, digits, hyphens/underscores, no status words in filenames. Use Git commits/tags for versions.

## 6. Automatic local commit; remote permission

Terms: local write = edit files; local staging = `git add`; local commit = `git commit`; remote push = `git push`.

After each explicit task with valid changes, automatically run task-appropriate validation and `git diff --check`; stage exact relevant non-ignored paths; inspect staged names/stat and text diff; then create one focused local commit with the current operator prefix, e.g. `[A][MODEL] implement Q1 physical model`. Do not create an empty commit. Do not stage caches, editor files, LaTeX auxiliaries, unrelated files, suspected secrets, or files over 50 MB without direction. Check suspected secret patterns without printing values.

Remote push is forbidden unless the current request explicitly says `git push`, remote push/upload, or equivalent and names an unambiguous target. Previous permission never carries forward. Before an authorized push, inspect status, branch, remote, recent log, and fetch; stop for conflicts or non-fast-forward risk. Force push, remote deletion, tag push, release, PR, and settings changes each need separate explicit authorization.

Without push permission, report the local commit and only show (never run):

```bash
git switch practice/apmcm-2026-b
git pull --rebase origin practice/apmcm-2026-b
git push origin practice/apmcm-2026-b
```

## 7. Before handoff

Report changed files, validation run/result, commit hash, `git status`, excluded files and reason, and whether a remote push occurred. State: `Remote push not executed: explicit remote permission was not granted.` unless it was explicitly authorized.
