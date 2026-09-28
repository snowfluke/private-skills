---
name: pmt-tatanan-code-review
description: Review a pull request in the Tatanan repository (PT-Perkasa-Pilar-Utama/tatanan) as its tech lead. Extends the code-review skill with Tatanan's docs, file-viewed marking, Drizzle migration checks, AC wording checks, and the reviewer sign-off. Use for Tatanan PRs only; for any other repository use code-review.
---

# Tatanan Code Review

This skill adds Tatanan steps to `code-review`. It does not replace any of it.

1. Find the installed `code-review` skill. It sits in the same skills directory as this skill, for example `~/.claude/skills/code-review/`. Read its `SKILL.md` and follow it in full.
2. Do the steps below at the `code-review` step each one names.
3. The finding format, severity, verdict, rounds, and `review_body.py check` come from `code-review` only. This file changes none of them.

The scripts are `scripts/review_body.py` and `scripts/check_ac_refs.py` inside that `code-review` directory.

## Project

| Item | Value |
| --- | --- |
| Repository | `PT-Perkasa-Pilar-Utama/tatanan` |
| Local checkout | `/Users/vexeee/Documents/project/tatanan`. Confirm you are in it before you read its files or scripts. |
| Stack | Bun, Hono (BE), React 18 (FE), Drizzle ORM, PostgreSQL |
| Layout | Monorepo: `apps/api`, `apps/web`, `packages/shared` |
| Gate | `bun fmt && bun lint && bun type-check && bun test` |
| Frontend tests | Optional. A missing frontend test is not a finding. |

## At code-review step 1: the standards

| Document | Use |
| --- | --- |
| `docs/CODING_STANDARDS.md` | Full rules with examples |
| `docs/CODE_REVIEW_CHECKLIST.md` | The checklist to walk |
| `docs/technical-specs/` | Architecture, data model, business rules, task state machine (`5.module-definitions.md` §5.3) |
| `docs/USER_STORY.md` | User stories US-01 to US-28 |
| `docs/ACCEPTANCE_CRITERIA.md` | AC rows per user story |
| `docs/TASK_BREAKDOWN.md` | Task cards, sprints, AC references |
| `docs/api-specs/` | REST specs per module. `_index.md` maps them. |

A task can depend on another task. A mock or a TODO is not a finding when the task card defers that work.

## At code-review step 3: mark the files viewed

Before you read any code, run this from the repo root, not the worktree:

```bash
bash /Users/vexeee/Documents/project/tatanan/sandbox/mark-viewed.sh <number>
```

It marks every changed file as viewed on GitHub's "Files changed" tab.

## At code-review step 5: extra review steps

### Migrations

Run these checks if the diff touches `apps/api/src/db/migrations/`. Run them before any other review step. Run them on `main`, not on the PR branch. They cover checklist lines 122 and 123.

1. **Journal index.** Checklist line 123: "`_journal.json` changed according to newly named descriptive migration file." Read the `idx` the PR adds to the journal. Confirm `main` does not already use that `idx`:

   ```bash
   python3 -c "
   import json
   j = json.load(open('apps/api/src/db/migrations/meta/_journal.json'))
   for e in j['entries']: print(e['idx'], e['tag'])
   "
   ```

   A taken `idx` means the branch was not rebased after other migrations merged. That is a BLOCKER. Fix: rebase on `main`, then regenerate the migration.

2. **Snapshot chain.** The PR snapshot's `prevId` must equal the `id` of the last snapshot on `main`:

   ```bash
   python3 -c "
   import json, glob
   snaps = sorted(s for s in glob.glob('apps/api/src/db/migrations/meta/*.json') if '_journal' not in s)
   print(snaps[-1], json.load(open(snaps[-1]))['id'])
   "
   ```

   A different `prevId` is a BLOCKER. Fix: rebase, then regenerate.

3. **Table names.** List each table the PR's migration SQL creates. Grep `main`'s migrations for each name:

   ```bash
   grep -l 'CREATE TABLE.*"<table>"' apps/api/src/db/migrations/*.sql
   ```

   A match means `db:migrate` fails with "relation already exists". That is a BLOCKER.

4. **File name.** Checklist line 122: "Migration file named descriptively." The file name must be descriptive (for example `0003_create_tasks_tables.sql`). The file stem must match the journal `tag` exactly. A mismatch is a BLOCKER, because a manual rename breaks the Drizzle chain.

### Acceptance criteria

`check_ac_refs.py` does not read Tatanan's layout. Instead, grep each AC ID the PR cites in `docs/ACCEPTANCE_CRITERIA.md`. An ID with no row is a finding. Also read the task card in `docs/TASK_BREAKDOWN.md` for the ACs the task must cover.

Each AC row has these columns:

| Column | Check |
| --- | --- |
| Scenario | The behavior under test |
| GIVEN | Role, page, prior state |
| WHEN | The user's trigger action |
| THEN | The outcome the code must produce |

Trace each THEN clause to the code:

- **Displayed text.** Messages, labels, titles and empty states must match the AC wording exactly, including Indonesian text. A paraphrase or a translation is a finding.
- **Layout.** If THEN describes a layout ("halaman terbagi menjadi 2"), the view must match it.
- **Conditions.** If THEN shows something only under a condition, the condition and the empty state must be in the code.
- **Real data.** If THEN names dynamic data, it must come from the data source, not a hard-coded string.
- **Role.** If GIVEN names a role, RBAC must keep other roles out.

An unmet THEN clause is a BLOCKER. Write it in the `code-review` format: `Rule` links the AC row and quotes the THEN clause, and `Problem` quotes what the code shows.

## At code-review step 10: the PR description and sign-off

1. **Description content.** The description must have the Task ID, the US reference (see `TASK_BREAKDOWN.md`), what changed, why, and how to test. A missing item is a BLOCKER. Its Rule quotes the PR template section that asks for it.
2. **Self-review box.** The template has one box: "I have read and verified every applicable item in `CODE_REVIEW_CHECKLIST.md`." If the diff breaks a checklist item, that item is already a finding. Uncheck the box with `gh pr edit <number> --body-file <file>`.
3. **Sign-off table.** Set the Tech Lead row's Decision to the verdict: `Approve` or `Request Changes`. Do not touch the Developer row. Do not add `claude`, `opencode` or any agent as a reviewer.

   ```markdown
   | Reviewer         | Role      | Decision                  | Notes |
   | ---------------- | --------- | ------------------------- | ----- |
   |                  | Developer | Approve / Request Changes |       |
   | Awal Ariansyah   | Tech Lead | Approve / Request Changes |       |
   ```

## Edit a posted review

Do this only when the user asks to edit a specific review. Normal rounds post a new review.

1. Get the review ID. It is the number after `#pullrequestreview-` in the URL. Or take the latest:

   ```bash
   REVIEW_ID=$(gh api "repos/PT-Perkasa-Pilar-Utama/tatanan/pulls/<number>/reviews" --jq '.[-1].id')
   ```

2. Write the new body to `/tmp/pr<number>-review.md`. Run `code-review` step 9 on it (verify, then check with `--repo PT-Perkasa-Pilar-Utama/tatanan`) until the check prints `OK`.
3. Replace the body:

   ```bash
   gh api --method PUT "/repos/PT-Perkasa-Pilar-Utama/tatanan/pulls/<number>/reviews/$REVIEW_ID" \
     --field body=@/tmp/pr<number>-review.md
   ```

Use `body=@file`. An inline `body='...'` string breaks backticks. A PUT cannot change the review state. Post a new review to change it.

## Task state machine

Valid transitions only (`docs/technical-specs/5.module-definitions.md` §5.3):

```
[*] -> to_do : Created from template
to_do -> blocked : Dependency exists, prerequisite incomplete
blocked -> to_do : Prerequisite completed
to_do -> in_progress : start_date set and reached (cron 08:00)
in_progress -> escalated : Assignee escalates
escalated -> in_progress : PM resolves
in_progress -> completed : Assignee completes
completed -> [*]
```

- `overdue` is derived, not stored (`end_date < CURRENT_DATE`).
- An invalid transition returns `422 INVALID_TRANSITION`.
- Every transition is recorded in `TASK_STATE_HISTORY`.
