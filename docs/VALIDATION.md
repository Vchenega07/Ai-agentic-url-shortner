# Validation evidence

Validated on 2026-10-12 with Temurin Java 21 and Maven 3.9.9.

## Build and quality gates

Command: `./mvnw --batch-mode verify`

- 49 tests, zero failures, zero errors, zero skipped.
- JaCoCo line coverage: 75.43% (required: 70%).
- JaCoCo branch coverage: 55.35% (required: 50%).
- SpotBugs: zero high-priority errors/warnings; verify succeeded.

The tests use Mockito's subclass mock maker because they do not require inline/final
mocking. This avoids runtime agent self-attachment, which is unavailable in some
restricted Java environments. No tests or quality gates are disabled.

## Live HTTP scenarios

Command against a locally running packaged JAR: `python3 scripts/smoke.py --engineering`.
All scenarios passed:

- URL lifecycle: creation, idempotency, redirect, analytics authorization, click recording, disable.
- GREENFIELD: RELEASE_READY with a passing real build and hashed reports.
- BROWNFIELD: RELEASE_READY after one actual compilation failure and one successful repair build.
- AMBIGUOUS: paused for clarification without a patch, then cancelled successfully.

The script fails immediately on unexpected
HTTP status, workflow state, missing test evidence or invalid audit-chain verification.

## Scope of verification

Local workflow scenarios use the deterministic model adapter, real isolated file changes,
and actual Maven processes. Approvals in this automated demo are simulated using distinct
submitter/approver accounts. A real human must review plans and outcomes outside the demo.
External OpenAI calls, PostgreSQL/Compose deployment, distributed execution, and production
hardening are not verified by this local run. See PROVENANCE.md for inherited limitations.
