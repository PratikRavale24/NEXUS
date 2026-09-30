# Case prototype role boundary

The prototype uses a development-only `X-Prototype-Role` header at the FastAPI dependency boundary, with investigator/analyst read access, investigator processing access, and supervisor/admin status and audit access. This keeps identity integration isolated while ensuring authorization is enforced server-side and the frontend cannot grant privileges by itself.
