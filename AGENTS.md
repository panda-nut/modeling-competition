# Repository AI Context and Collaboration Rules

## Repository purpose

This repository supports a three-member mathematical-modeling team across training problems, mock contests, official contests, coursework, model code, technical review, paper writing, and final-result archiving.

The required workflow is:

`joint problem analysis → model V0 → reproduction and validation → paper drafting → technical review → cross-check → human remote upload`.

Files under version control are the source of truth. AI chat history, screenshots, and unverified generated text are not evidence.

## Branch policy

| Branch pattern | Purpose |
| --- | --- |
| `main` | SOP, paper templates, shared code utilities, checklists, and archived results |
| `practice/<project-name>` | Training problem or mock contest |
| `contest/<competition-year-problem>` | Official contest |
| `coursework/<project-name>` | Coursework |

The current project branch is `practice/apmcm-2026-b`. One contest or project uses exactly one project branch. Do not create long-lived member-, question-, or task-specific branches; do not use long-lived `develop`, `release`, or `final` branches. Mark a completed project with a Git tag, for example `apmcm-2026-b-v1.0`.

## Required project layout

All AI reads and writes on `practice/apmcm-2026-b` must follow this layout. Use `.gitkeep` for required empty directories.

```text
00_problem/          # problem statement, attachments, original instructions
01_architecture/     # full architecture, model V0, decision log
02_references/       # literature and background
03_data/
  raw/                # immutable source data
  processed/          # derived data
04_code/
  q1/ q2/ q3/ q4/ q5/ common/
05_validation/
  q1/ q2/ q3/ q4/ q5/
06_figures/
  q1/ q2/ q3/ q4/ q5/
07_paper/
  sections/ tables/ bibliography/ main.tex
08_results/
  intermediate/ final-results.md
09_submission/       # final delivery files
```

## Operator identity, role assignment, and logical write ownership

`[A]`, `[B]`, and `[C]` are **operator codes**, not permanent role labels. At the beginning of every new AI conversation, read this file and confirm the active operator with the user unless it is already recorded below. The confirmed operator for this agent and repository context is **`[A]`**; every commit, handoff, generated-file attribution, and local action performed by this agent uses `[A]`.

Do not infer a person's modeling, validation, or paper role from an operator code. Roles are assigned explicitly per task or project. The following are responsibility areas, not a mapping to `[A]/[B]/[C]`:

| Role | Primary directories | Responsibilities |
| --- | --- | --- | --- |
| Modeling Lead | `01_architecture/`, `02_references/`, `04_code/`, `06_figures/` | architecture, literature, model V0, core code, formal figures, model choice, technical-boundary review |
| Validation Lead | `03_data/`, `05_validation/`, `08_results/` | data audit, reproduction, baselines, cross-validation, convergence/sensitivity checks, formal result tables, numerical consistency |
| Paper Lead | `07_paper/`, `09_submission/` | restatement, paper structure, sections, LaTeX, abstract, conclusion, references, submission files |

Cross-role rules:

1. Do not modify another member's primary files without stating the reason first.
2. State the reason before making a cross-directory change.
3. `07_paper/main.tex` is maintained by the designated Paper Lead; other operators must not overwrite it.
4. The Modeling Lead writes paper material in `01_architecture/paper-notes/`; the Validation Lead writes paper material in `05_validation/paper-notes/`; the Paper Lead integrates it into `07_paper/sections/`.
5. `08_results/final-results.md` is the sole source of formal numerical values. Key values in abstracts, text, tables, and captions must match it.
6. Do not have more than one person modify the same file simultaneously.

## AI local-work rules

Before every task, an AI/Codex must:

1. Read this `AGENTS.md`.
2. Confirm the current branch and run `git status`.
3. Confirm its operator code; use the recorded current code `[A]` unless the user explicitly changes it. Identify intended directories/files and possible overlap with others' work.
4. Check that it will not overwrite another member's uncommitted work.

Default local flow:

```bash
git switch practice/apmcm-2026-b
git status
git pull --rebase origin practice/apmcm-2026-b
```

If networking is unavailable, skip the pull only after explicitly reporting it. AI may create/move/edit local files, run code and tests, generate local figures, format files, and create local commits. AI must not automatically push, delete a remote branch, create a remote release, alter GitHub settings, or force-push.

After a local change: run relevant validation, `git diff --check`, `git status`, inspect staged paths, make a focused local commit, summarize the change, and provide manual upload commands. Prefer `git add <specific-paths>`; use `git add .` only when all changed files are confirmed relevant.

## Human remote-upload process

Humans alone confirm and execute remote writes:

```bash
git switch practice/apmcm-2026-b
git status
git pull --rebase origin practice/apmcm-2026-b
git push origin practice/apmcm-2026-b
```

For `main`, use `git pull --rebase origin main` then `git push origin main`. Push a tag with `git push origin apmcm-2026-b-v1.0`. Delete an old remote branch only with `git push origin --delete <branch-name>`. On rejection, never force-push: pull with rebase, resolve conflicts, re-run checks, then perform a normal push.

## Commit messages

Use English, imperative verb phrases, and one clear task per commit. Allowed types are:

```text
[ARCH] repository architecture and modeling framework
[MODEL] model implementation or improvement
[DATA] data import, cleaning, or transformation
[REVIEW] model validation and technical review
[PAPER] paper writing or LaTeX update
[FIGURE] figure generation or standardization
[RESULT] numerical result update
[FIX] correction of code, formula, figure, or value
[FINAL] freeze final result or submission
[CHORE] repository maintenance without model changes
```

Prefix every commit with the actual operator code. Current-agent examples: `[A][MODEL] implement Q1 physical model`, `[A][REVIEW] validate Q2 cross-validation pipeline`, `[A][PAPER] draft Q2 methodology section`. Do not use a different code unless the user explicitly reassigns the operator.

## Progress management

Before editing, read `01_architecture/full-problem-architecture.md`, `01_architecture/model-decision-log.md`, and `08_results/final-results.md` in addition to this file. Record each material route decision in the decision log and never mark a task `validated` or `frozen` without the designated Validation Lead's record. Statuses are `planned`, `in progress`, `validated`, and `frozen`; every AI handoff must state its actual operator code, changed paths, current status, evidence paths, and next owner.

# LaTeX Result Document Workflow

## File roles and pairing

- `.tex` is the editable source of a formal result document. AI reads, analyzes, edits, and resolves conflicts at the TEX layer; models, formulas, prose, tables, figure references, and conclusions are governed by TEX.
- A same-basename `.pdf` is the human-reading preview. Do not directly edit PDF, use it as default AI input, or reverse-engineer TEX from a PDF. If TEX and PDF differ, TEX wins and must be recompiled.
- Keep formal pairs in the same directory, e.g. `q2-surrogate-model.tex` and `q2-surrogate-model.pdf`. Never use state filenames such as `final.pdf` or `latest.pdf`; versions use commits and tags.
- After modifying TEX, rebuild its PDF. If compilation fails, preserve the previous working PDF, report the first error, and do not create an empty replacement.

## Reading, directories, and compilation

Before a result task, read AGENTS, the project README, relevant TEX, code/data/results registry/validation records; inspect PDF only for requested visual or layout QA. Results use `08_results/q1/` through `q5/` (the current combined Q4/Q5 source is in `08_results/q4-q5/`); reviews use `05_validation/q*/`; the paper pair is `07_paper/main.tex` and `07_paper/main.pdf`; submission copies belong in `09_submission/`.

Compile with XeLaTeX/latexmk into `.latex-build/<document-id>/`, then copy only the resulting same-name PDF beside TEX. Build intermediates are ignored; formal TEX and PDF are tracked. AI may edit and compile locally but may not push or alter remote state.

# CSV Data Workflow

CSV is the traceable interface between programs, figures, and papers. Store raw immutable inputs in `03_data/raw/`, reproducible transformations in `03_data/processed/`, important process data in `08_results/intermediate/`, review evidence in `05_validation/q*/`, and only Validation-Lead-validated outputs in `08_results/final/`. Do not hand-edit raw data or promote an intermediate CSV to formal results without Validation Lead review and an update to `08_results/final-results.md`.

Use UTF-8 comma-separated CSV with a header, `snake_case` names where new files are created, explicit missing-value conventions, no implicit DataFrame index, and no units embedded in numeric values. Important CSV must be traceable to source data and a generating script; the Modeling Lead owns model-process data, the Validation Lead owns audits/validation/formal result registration, and the Paper Lead reads rather than changes formal numeric CSV. AI must inspect context, generating code, fields, and status before interpreting a CSV; filenames alone are insufficient.

After importing or generating important process, validation, or final CSV data, AI/Codex must run the applicable checks and create a focused **local** Git commit automatically. It must never automatically push that commit, delete remote content, or force-push; remote upload remains a human action.

## Naming rules

- Use lowercase English letters, digits, hyphens, and underscores only; no spaces, Chinese names, parentheses, repeated separators, or state words such as `final`, `latest`, `new`, `new2`, `final-v2`.
- Extensions are lowercase; use commits and tags, not filenames, for versioning. Dates use `YYYY-MM-DD`.
- Ordinary directories and Markdown files use kebab-case: `surrogate-model/`, `paper-notes/`, `full-problem-architecture.md`, `q2-validation-report.md`. Keep `README.md`, `AGENTS.md`, `LICENSE`, and `CHANGELOG.md` uppercase.
- Python files use snake_case, e.g. `load_data.py`, `fit_surrogate_model.py`; notebooks use `q1_exploratory_analysis.ipynb` style.
- Data files use snake_case. Source files belong in `03_data/raw/` and must not be modified; corrected/derived files go to `03_data/processed/`.
- Figures use `fig_q<question-number>_<sequence>_<topic>.<ext>` (for example `fig_q2_02_oof_predictions.pdf`). Keep PNG for previews and PDF/SVG for vectors; do not retain meaningless screenshots.
- Tables use `table_q<question-number>_<sequence>_<topic>.<ext>`; result files use `q<question-number>_<topic>_results.<ext>`. The only formal all-project value table is `08_results/final-results.md`.
- LaTeX root is `07_paper/main.tex`; section files are `01_problem_statement.tex`, `02_model_assumptions.tex`, `03_q1_physical_model.tex`, `04_q2_surrogate_model.tex`, `05_q3_optimization.tex`, `06_q4_preference_robustness.tex`, `07_q5_sensitivity_analysis.tex`, `08_model_evaluation.tex`, and `09_conclusion.tex`.
- Logs use `YYYY-MM-DD-task-name.md`, for example `2026-07-21-branch-migration.md`.
