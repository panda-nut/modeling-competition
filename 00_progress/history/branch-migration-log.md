# Branch migration log

## Scope

The three legacy feature branches were inspected before consolidation. Each pointed to the same commit as `practice/apmcm-2026-b` (`4ac4fea`), so none contained branch-specific files or commits to relocate. Their shared repository-framework files remain at the repository root; the project directory structure below was created for subsequent work.

| Original path | New path | Source branch | Reason |
| --- | --- | --- | --- |
| No branch-specific paths | No file migration required | `feature/paper-framework` | Branch tip matched project branch exactly. |
| No branch-specific paths | No file migration required | `feature/q1-mechanism` | Branch tip matched project branch exactly. |
| No branch-specific paths | No file migration required | `feature/q2-surrogate-review` | Branch tip matched project branch exactly. |

The archive tags `archive-paper-framework-before-merge`, `archive-q1-mechanism-before-merge`, and `archive-q2-surrogate-review-before-merge` preserve the legacy branch tip.
