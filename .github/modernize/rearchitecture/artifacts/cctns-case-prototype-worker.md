# CCTNS Prototype Case Workspace

## Summary

Implemented the smallest end-to-end operational case/FIR prototype slice on the existing SQLAlchemy and Next.js foundations.

## Deliverables

- `backend/app/api/cases.py` — typed case, document, timeline, audit, processing, and status routes with isolated prototype role headers.
- `backend/app/services/case_service.py` — SQLAlchemy case/document/audit/job operations.
- `backend/app/schemas/case.py` — typed response and request contracts.
- `frontend/src/app/cases/page.tsx` — responsive queue/detail workspace with loading, error, empty, provenance, processing, timeline, and status views.
- `frontend/src/lib/api.ts`, `frontend/src/lib/types.ts` — typed case client contracts.
- `tests/test_case_contracts.py` — schema and role matrix coverage.

## Upstream Artifacts Consumed

- `/memories/session/plan.md` — approved CCTNS Prototype Addendum, route list, role boundaries, and verification requirements.
- `.github/modernize/rearchitecture/board.md` — not available as a task dependency; repository status was preserved.

## Evidence Mapping

- Addendum prototype routes `/cases`, detail, documents, timeline, processing, status, audit -> `backend/app/api/cases.py` and frontend Cases workspace.
- Addendum role boundary and no fabricated legal roles -> `prototype_identity`, `require`, metadata-only document responses, and explicit UI prototype-role notice.
- Addendum verification requirement -> test and smoke results below.

## Test Results

- Command: `backend/.venv/Scripts/python.exe -m pytest tests -q`
- Passed: 18
- Failed: 0
- Skipped: 0
- Frontend: `npm.cmd run lint` passed; `npm.cmd run build` passed.
- Runtime: `/health` 200, `/cases` 200 with empty current database, frontend `/cases` 200.
- Authorization smoke: default investigator `/cases/1/audit` 403 and `/cases/1/status` 403.

## Limitations

- Prototype identity uses `X-Prototype-Role` and `X-Prototype-User-Id` headers only while `APP_ENV=development`; production identity integration remains intentionally deferred.
- The current operational database has no registered cases, so populated FIR/detail and processing transitions were not exercised against live records.
- Processing creates a pending `ProcessingJob` and audit record; it does not execute the existing NLP/entity/relation pipeline asynchronously yet.
- Existing unrelated working-tree changes were preserved.
