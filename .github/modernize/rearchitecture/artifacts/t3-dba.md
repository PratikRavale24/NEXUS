# t3 — Bounded Neo4j Projection and Identifier Review

## Scope

Review of the existing Neo4j network projection, depth and limit handling, filter boundaries, and identifier lookup indexes for the approved NEXUS network redesign. No application source changes are required in this plan task; backend implementation belongs to t5.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/artifacts/t1-architect.md` — preserved network route, depth 1 default, explicit depth 2, bounded projection, and stable identifier rules.
- `.github/modernize/rearchitecture/artifacts/t2-ux.md` — client-side filter/search behavior and the requirement that filters do not refetch or mutate loaded elements.
- `/memories/session/plan.md` — query-cost, server-side limit, filter validation, and identifier-index requirements.

## Evidence Mapping

- `t1-architect.md#HTTP Contracts` → retain `GET /entities/{entity_id}/network`, `depth=1..2`, and existing node/edge limit ranges.
- `t1-architect.md#Network Response` → preserve source IDs, deterministic edge IDs, and actual Neo4j properties.
- `t1-architect.md#Risks and Mitigations` → prevent unbounded path expansion and duplicate node/edge projections.
- `t2-ux.md#Filters` → keep entity/relationship filtering client-side for loaded data; any server-side filter must be optional and validated.

## Findings

### 1. Current network query is only partially bounded

`backend/app/services/network_service.py` clamps the Python arguments, but the Cypher query expands `[*1..{depth}]` before applying `LIMIT $path_limit` to rows produced by `UNWIND nodes(path)`. A path limit is not a node limit or an edge limit, and the loop stops only when both collections reach their limits. The query can therefore expand more paths than the response limits suggest and can return a partial mix that is sensitive to Neo4j traversal order.

### 2. Depth is safe at the HTTP boundary but should remain explicit in the service

`backend/app/api/entities.py` already validates `depth` as `1..2`. `get_person_network` additionally clamps values, which is useful for direct service callers. Keep both protections, but use fixed query branches for depth 1 and depth 2 rather than interpolating a variable-length upper bound. No depth 3 path should be accepted or silently coerced.

### 3. Client filters should not be pushed into the initial projection by default

The approved UX derives entity and relationship options from the loaded response and applies them locally without refetching. The network route therefore needs no filter parameters for the redesign. If a future server-side reduction is added, accept only validated repeated values or a validated comma-separated list, constrain values against known labels/types, and preserve the same response contract. Never interpolate user-provided labels, relationship types, or property names into Cypher.

### 4. Identifier lookups need idempotent uniqueness constraints

The ingestion service uses `MERGE` on these identifiers and all profile/network/search lookups use them in label-scoped predicates. Add one Neo4j 5 constraint per identifier property:

```cypher
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (n:Person) REQUIRE n.person_id IS UNIQUE;
CREATE CONSTRAINT phone_id_unique IF NOT EXISTS
FOR (n:Phone) REQUIRE n.phone_id IS UNIQUE;
CREATE CONSTRAINT vehicle_id_unique IF NOT EXISTS
FOR (n:Vehicle) REQUIRE n.vehicle_id IS UNIQUE;
CREATE CONSTRAINT location_id_unique IF NOT EXISTS
FOR (n:Location) REQUIRE n.location_id IS UNIQUE;
CREATE CONSTRAINT organization_id_unique IF NOT EXISTS
FOR (n:Organization) REQUIRE n.organization_id IS UNIQUE;
CREATE CONSTRAINT account_id_unique IF NOT EXISTS
FOR (n:Account) REQUIRE n.account_id IS UNIQUE;
CREATE CONSTRAINT evidence_id_unique IF NOT EXISTS
FOR (n:Evidence) REQUIRE n.evidence_id IS UNIQUE;
CREATE CONSTRAINT finding_id_unique IF NOT EXISTS
FOR (n:Finding) REQUIRE n.finding_id IS UNIQUE;
CREATE CONSTRAINT event_id_unique IF NOT EXISTS
FOR (n:Event) REQUIRE n.event_id IS UNIQUE;
```

These are additive and rerunnable. Before applying them to a populated database, run duplicate checks per label; a constraint creation failure is a data-quality blocker and must not be bypassed by dropping or rewriting records. The existing loaders do not create `Finding` or `Event` master nodes, so those two constraints should be applied only when those labels are present in the deployed graph.

## Recommended Projection Contract for t5

1. Validate `person_id` and bounds in the route and service. Keep `node_limit <= 500`, `edge_limit <= 1000`, and `depth <= 2`.
2. Match the root by the indexed `:Person.person_id`. Always include the root, even when it has no relationships.
3. Use a fixed depth-1 query for direct undirected relationships. Use a separate fixed depth-2 query only after explicit expansion. Do not use a user-derived Cypher fragment for the upper bound.
4. Project only `properties(root)`, `properties(neighbor)`, and `properties(relationship)` plus the stable identifiers, labels, relationship type, and Neo4j element ID needed to normalize the response.
5. Deduplicate nodes by `(entity_type, identifier)` and edges by `(source_id, relationship_type, target_id, relationship_element_id)`. Preserve the current deterministic edge ID shape.
6. Apply deterministic ordering before truncation, for example by hop distance, relationship type, relationship element ID, and endpoint identifier. This makes repeated requests stable and makes node/edge limit tests reliable.
7. Enforce response bounds independently: `len(nodes) <= node_limit` and `len(edges) <= edge_limit`, with the root retained. Do not rely on a path-row limit to enforce either bound.
8. Keep filter behavior client-side for the redesign. Entity and relationship filters must affect visibility only after the response is loaded and must not alter this server projection.

For depth 1, the preferred shape is a direct relationship projection with a bounded, deterministically ordered relationship collection, followed by distinct node normalization. For depth 2, cap the first-hop and second-hop relationship collections before combining them, or use a bounded subquery that returns already-normalized node/edge rows. A single unrestricted `MATCH path ... UNWIND` is not sufficient evidence of bounded work even if the final Python lists are sliced.

## Required Backend Tests

- Service clamps direct-call values and never emits depth outside `1..2`.
- Route rejects `depth=0`, `depth=3`, `node_limit=0`, `node_limit=501`, `edge_limit=0`, and `edge_limit=1001` with validation errors.
- Root-only person returns one root node, no edges, and the requested depth.
- Depth 1 does not issue a depth-2 query or perform a second request internally.
- Explicit depth 2 returns no path longer than two hops.
- Responses never exceed node or edge limits independently; the root is retained when `node_limit >= 1`.
- Duplicate paths produce one node per stable identifier and one edge per stable edge key.
- Unknown/non-person entity IDs preserve the existing `400`/`404` meanings.
- Optional server-side filters, if implemented, reject unknown entity/relationship values and cannot change the Cypher structure.
- Constraint/bootstrap statements are idempotent; duplicate identifier data is reported as a migration failure rather than silently changed.

## Migration and Compatibility Risks

- Uniqueness constraints can fail on pre-existing duplicate IDs. Treat this as a blocking data-quality issue and report the offending label/property before retrying.
- Replacing traversal-order truncation with deterministic ordering can change which records appear at a saturated limit, but it does not change entity or relationship semantics.
- A depth-2 bounded projection may return fewer nodes than the old query because it correctly honors independent limits. The response schema and identifiers remain compatible.
- Do not add indexes on display fields such as `name`, `registration`, or `account_number` solely for this redesign; current search uses case-insensitive `CONTAINS`, which does not benefit from ordinary exact-match indexes. Revisit search-specific indexing separately if catalog scale requires it.

## Test Results

- Command: Not run; this is a plan-phase DBA review and contains no source-code implementation.
- Passed: 0
- Failed: 0
- Skipped: 1 (backend implementation and executable validation belong to t5/t8)

## Recommended Handoff

Implement the projection and constraint bootstrap in `backend/app/services/network_service.py` and the backend's Neo4j initialization boundary, then add the route/service tests above before frontend integration. Notify the backend role that query shape and deterministic truncation are contract-sensitive.
