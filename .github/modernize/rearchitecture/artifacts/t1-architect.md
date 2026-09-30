# t1 — Preserved Architecture, API Contracts, and Cytoscape Boundaries

## Scope

This design preserves the existing FastAPI + Neo4j backend, Next.js App Router frontend, and Cytoscape network renderer. It changes reliability, query bounding, and investigator interaction behavior without changing entity identifiers, route meanings, intelligence data, or ingestion/analytics semantics.

## Upstream Artifacts Consumed

- `/memories/session/plan.md` — approved redesign requirements, preserved decisions, and verification sequence.
- `.github/modernize/rearchitecture/artifacts/project-profile.yaml` — project structure, stack, and non-grouped topology.
- `backend/app/graph.py`, `backend/app/main.py` — current Neo4j driver ownership and FastAPI lifecycle.
- `backend/app/api/entities.py`, `backend/app/services/network_service.py`, `backend/app/schemas/entity.py` — current network route, bounds, query shape, and response models.
- `frontend/src/app/entities/[entityId]/network/page.tsx`, `NetworkGraph.tsx`, `frontend/src/lib/api.ts`, `frontend/src/lib/types.ts` — current page state, API client, graph data, and Cytoscape lifecycle.

## Evidence Mapping

- `/memories/session/plan.md#12-19` → frontend/backend separation, cancellable requests, and route preservation described below.
- `/memories/session/plan.md#20-30` → network workspace states, depth behavior, filtering, labels, focus, fit/reset, and expansion boundaries.
- `backend/app/api/entities.py` network route → preserved `GET /entities/{entity_id}/network` contract and depth/limit rules.
- `backend/app/services/network_service.py` → node/edge identity, actual-property preservation, and bounded projection requirements.
- `frontend/src/app/entities/[entityId]/network/NetworkGraph.tsx` → lifecycle split into mount, data, view-state, and resize responsibilities.

## Preserved System Boundaries

### Backend

- `backend/app/graph.py` owns the single application-scoped Neo4j `Driver`, session context helper, connectivity check, and shutdown close. Route modules never create or close drivers and never call `verify_connectivity()` during ordinary requests.
- `backend/app/api/entities.py` owns HTTP validation and status mapping. Services receive the shared driver and return domain-shaped dictionaries. Pydantic schemas remain the public serialization boundary.
- `backend/app/services/network_service.py` owns bounded graph projection and deterministic node/edge normalization. It must not mutate Neo4j data or alter ingestion, anomaly, relation, or finding semantics.
- `backend/app/main.py` owns FastAPI startup/shutdown and the structured Neo4j exception response. Health connectivity is the only route allowed to perform an explicit connectivity check.

### Frontend

- `frontend/src/lib/api.ts` remains the only network-request boundary for the App Router client components. It owns timeout/cancellation, request IDs, and translation of `{error, message, request_id}` failures.
- `frontend/src/lib/types.ts` is the shared contract for network nodes, edges, metadata, and API errors. Optional fields represent absence; no UI layer invents confidence, relevance, evidence, timestamps, or analytics.
- `frontend/src/app/entities/[entityId]/network/page.tsx` owns request state, selected IDs, depth expansion intent, filters, search text, focus mode, and inspector mode.
- `NetworkGraph.tsx` owns exactly one Cytoscape instance per mounted container. It owns graph elements, classes, layout, event subscription, resize handling, and destruction, but not API requests or inspector rendering.
- Inspector and toolbar components consume normalized loaded data and callbacks. They do not query Neo4j directly and do not infer missing metadata.

## HTTP Contracts

### Existing routes remain stable

- `GET /health` → `{status, service, version}`.
- `GET /health/database` → `{status, database}` or existing `503` failure.
- `GET /health/neo4j` → `{status, database}` or existing `503` failure.
- `GET /entities/search?q=<1..100>&limit=<1..50>` → `EntitySearchResult[]`.
- `GET /entities/{entity_id}` → `EntityProfile` or `404`.
- `GET /entities/{entity_id}/network` → `NetworkResponse` or `400/404`.
- `GET /entities/{entity_id}/timeline?limit=<1..500>` → `TimelineResponse` or `400/404`.
- Existing findings routes and review payloads remain unchanged.

### Network request

`GET /entities/{person_id}/network` accepts:

- `depth`: integer `1..2`; default `1`. Depth 1 is the initial and reset state.
- `node_limit`: integer `1..500`; default `250`.
- `edge_limit`: integer `1..1000`; default `500`.
- Optional server-side `entity_type` and `relationship` filters may be added only as repeated or comma-separated validated values if the backend implementation needs query reduction. Client-side filters remain authoritative for already-loaded data and must not trigger a refetch.

The route remains person-centric and rejects non-person IDs with `400`. Missing persons remain `404`. Expansion to depth 2 is an explicit user action and uses the same route with `depth=2`; it is never an automatic second request on initial mount.

### Network response

```text
NetworkResponse {
  root_entity_id: string
  depth: 1 | 2
  nodes: NetworkNode[]
  edges: NetworkEdge[]
}

NetworkNode {
  id: string
  entity_type: string
  label: string
  properties: Record<string, JSON value>
  // Optional future additions: analytics/community fields when returned by Neo4j.
}

NetworkEdge {
  id: string
  source: string
  target: string
  relationship: string
  properties: Record<string, JSON value>
}
```

The existing ID rules remain: node IDs are source entity identifiers, edge IDs are deterministic source/type/target/Neo4j-element combinations. `properties` is the only source for detail metadata. Missing values render as unavailable, not as placeholders or synthetic scores.

### Error contract

Neo4j request failures return HTTP `503`, `X-Request-ID`, and JSON `{error, message, request_id, details: null}`. Investigator-facing messages remain stable and do not expose driver/query text. The frontend preserves the request ID on its typed error for diagnostics, maps timeout/cancellation separately, and offers retry without duplicating requests.

## Cytoscape Lifecycle Boundary

`NetworkGraph` must use four independent effects or equivalent responsibilities:

1. **Mount-only initialization**: create Cytoscape once when the container exists, with styles and a stable preset/concentric configuration. Register node/edge handlers through callback refs. Register one `ResizeObserver`. Cleanup removes handlers, disconnects the observer, destroys the instance, and clears the ref.
2. **Element synchronization**: when the normalized `network` changes, replace or patch the element collection, preserve selected IDs where still present, then run the centered concentric/radial layout. This effect must not recreate the instance.
3. **View-state synchronization**: apply selected, filtered, focus-hidden, and search-match classes; apply relationship filters to edges; never remove elements for a client-side filter. Edge labels remain hidden by default and are shown only for the selected edge.
4. **Commands**: fit/reset and explicit depth-2 expansion are callback-driven commands. Fit calls `fit()` on the existing instance. Reset restores root selection, depth 1, filters, search, and focus state at page level, then lets element/view effects converge.

The selected root is the radial center. Initial depth 1 uses full root labeling, short labels for first-hop nodes, and no labels for secondary nodes. Depth 2 uses the same rule with secondary labels still progressive/minimal. Edge labels are blank by default; the inspector is the primary relationship detail surface.

## Page State Machine

The network page exposes these mutually understandable states:

- `loading`: initial request or explicit depth-2 expansion; graph area shows a stable loading state and controls do not issue duplicate loads.
- `ready`: response has loaded; graph, counts, filters, and summary inspector are available.
- `empty`: valid response has no connected nodes/edges; show an explicit no-connections state with retry/return navigation as appropriate.
- `error`: request failed; preserve the last successful graph when available, show a retry action, and do not fabricate graph data.
- `expanding`: depth 2 request in flight; retain depth-1 graph context until the response succeeds, then replace the bounded projection.

Selection is one of `summary`, `node`, or `edge`. Node selection clears edge selection; edge selection clears node selection only if that matches existing page behavior. Focus is a view class operation around the selected node and must not mutate the response. Search matches loaded node IDs/labels only and must not call the catalog search endpoint.

## Responsive Workspace Contract

The page remains a three-zone workspace: controls, graph, inspector. Desktop uses columns; narrow layouts stack or drawer controls/inspector without changing callbacks or data ownership. Graph height and container dimensions must be stable enough for Cytoscape to resize deterministically. Controls expose entity and relationship filters, in-network search, focus, fit, reset, and an explicit expand-depth-2 action. Optional playback, pathfinding, comparison, export, and community visualization stay out of this implementation.

## Risks and Mitigations

| Risk                                                                     | Severity | Mitigation                                                                                                                   |
| ------------------------------------------------------------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Recreating Cytoscape on state changes leaks handlers and loses positions | HIGH     | Mount-only instance effect, callback refs, one cleanup path, and a no-duplicate-instance interaction test.                   |
| Unbounded path/unwind query duplicates nodes/edges or exhausts Neo4j     | HIGH     | Keep depth capped at 2, parameterize node/edge limits, deduplicate by stable IDs, and validate limits at the route boundary. |
| Client filters remove elements and invalidate selected IDs               | MEDIUM   | Use Cytoscape classes/visibility semantics; retain normalized data and reconcile selections.                                 |
| Synthetic labels or metrics mislead investigators                        | HIGH     | Render only `label`, `properties`, and explicitly returned analytics/provenance fields; absent values are unavailable.       |
| Stale requests overwrite a newer entity/depth selection                  | HIGH     | Abort obsolete requests, associate responses with entity/depth intent, and update state only for the active request.         |
| Neo4j startup/plugin delay appears as a graph defect                     | MEDIUM   | Keep health failure messaging structured and retryable; treat container readiness separately from graph UI logic.            |
| Existing duplicate `/health/neo4j` declarations drift                    | MEDIUM   | Consolidate to one route during backend implementation and cover it with route smoke tests.                                  |

## Implementation Sequence

1. Backend worker preserves schemas, consolidates driver/health lifecycle, adds bounded query validation, and covers route/service contracts.
2. Frontend worker adds typed cancellable API flow and page request states.
3. Frontend worker splits Cytoscape lifecycle from page state, then adds filters/search/focus/fit/reset/explicit depth 2.
4. Testers run backend tests/API probes and frontend lint/type/build, then browser-validate P001 at desktop and mobile widths.
5. Architect review checks this contract against the resulting diff before final sign-off.

## Verification Status

- Design verification: complete from current source inspection and approved plan.
- Source changes in this task: none.
- Build/test execution: not run in the plan phase; implementation and smoke-test roles own executable validation.
- Known environment constraint: Neo4j readiness must be established before live network/API probes.
