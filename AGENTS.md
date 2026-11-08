# Working on Boundary Conditions

Keep public code, documentation, commits, and pull requests in English.
Read the README, shared protocol, related work, and the relevant study plan first.
Plans are not results. Preserve negative results, uncertainty, and provenance.

## Parallel ownership

| Workstream | Branch | Owned paths |
| --- | --- | --- |
| Summary laundering | `study/summary-laundering` | `studies/summary-laundering/**` |
| Wrong-goal proof | `study/wrong-goal-proof` | `studies/wrong-goal-proof/**` |
| Integration coordinator | `main` | Root files, `docs/**`, and cross-study infrastructure |

Use the separate checkout assigned to your workstream. Do not switch branches
or modify files in another researcher's checkout. Initially keep each study
self-contained; propose shared infrastructure to the coordinator before editing it.

Each study maintains its own English `STATE.md` and append-only `HISTORY.md`
under its owned directory. These are the study's state and history for this
repository. The coordinator alone synchronizes shared competition trackers,
the repository README, and the root research log, avoiding concurrent writes.
Do not publish private coordination messages, identifiers, or local personal paths.

## Delivery and integration

1. Implement and validate the study within its owned paths.
2. Record exact commands, versions, seeds, test results, costs, and limitations.
3. Review the staged file list and content for ownership and private data.
4. Commit and push the study branch; open a pull request into `main`.
5. Request a read-only peer review and notify the integration coordinator.

The coordinator reviews and merges pull requests sequentially. Study workers
must not push to `main`, force-push, or merge their own pull requests without
coordination. Fetch before publishing; preserve any concurrent upstream work.
Report blockers and pending review honestly rather than calling an unmerged
change an integrated result.

## Experimental integrity

- Validate deterministic scorers and certificates before model evaluations.
- Separate synthetic test doubles from real model observations.
- Freeze a protocol before evaluating held-out cases; disclose later changes.
- Do not introduce additional paid compute or paid model services without authorization.
- Keep credentials and unreviewed raw logs out of Git and pull requests.
- Do not submit to the competition or change the license as an implementation step.