# t2 — Responsive Network Workspace Interactions and Investigator States

## Scope

This artifact specifies the investigator-facing interaction contract for the existing Next.js App Router network route and Cytoscape renderer. It preserves the current route, API semantics, entity identifiers, actual Neo4j properties, and three-zone workspace while making the state transitions and responsive behavior explicit.

## Upstream Artifacts Consumed

- `/memories/session/plan.md` — approved redesign requirements, must-have interactions, preserved architecture, and verification sequence.
- `.github/modernize/rearchitecture/artifacts/t1-architect.md` — page state machine, Cytoscape lifecycle boundary, network contract, and responsive workspace boundary.
- `.github/modernize/rearchitecture/artifacts/project-profile.yaml` — stack, project scope, and non-grouped topology.
- `frontend/src/app/entities/[entityId]/network/page.tsx` — current controls, selection, loading/error/empty rendering, inspector, and responsive grid.
- `frontend/src/app/entities/[entityId]/network/NetworkGraph.tsx` — current Cytoscape styles, radial/concentric layout, classes, selection callbacks, resize observer, and cleanup.
- `frontend/src/lib/types.ts` — current `NetworkNode`, `NetworkEdge`, and `NetworkResponse` public shapes.

## Evidence Mapping

- `/memories/session/plan.md#24-32` → interaction model, progressive labels, filters, focus, expansion, inspector, and acceptance sequence below.
- `t1-architect.md#Cytoscape Lifecycle Boundary` → graph instance ownership and command/state separation.
- `t1-architect.md#Page State Machine` → loading, ready, empty, error, and expanding state behavior.
- `network/page.tsx` current controls and inspector → preserve existing selection, profile/timeline/findings navigation, and actual-property rendering while extracting responsibilities.
- `NetworkGraph.tsx` current classes and concentric layout → retain class-driven filtering/focus and selected-root centered radial layout without recreating Cytoscape.

## Workspace Contract

### Desktop

Use three explicit zones in a stable grid:

- **Controls, left:** loaded-network search, entity-type filters, relationship filters, focus, fit, reset, and the explicit `Expand to depth 2` command. Keep advanced actions visually secondary.
- **Graph, center:** the dominant workspace with stable height and a visible status/count strip. The selected root remains the radial center. Graph controls must not cause the canvas to resize unpredictably.
- **Inspector, right:** summary, node, or relationship detail. It is the authoritative detail surface; graph labels remain intentionally sparse.

The graph column should remain usable at intermediate widths. At widths where three columns become cramped, move controls and inspector to drawers or stacked sections while preserving the same callbacks and state ownership.

### Narrow screens

Use a predictable reading order: graph/status first, selected-item inspector second, controls third. Controls and inspector may be collapsible drawers, but opening a drawer must not remount the Cytoscape component. Keep a minimum graph height and call `resize()` after drawer/section transitions. The selected item remains visible in the inspector when the drawer opens.

Do not hide required actions behind hover-only affordances. Icon buttons need accessible names and tooltips; text labels remain for investigator-critical commands such as `Expand to depth 2`, `Reset view`, and `Retry`.

## Interaction Model

### Initial ready state

- Request only depth 1 on initial mount.
- Center the root entity and show its full label.
- Show short labels for first-hop nodes; keep secondary/depth-2 labels hidden or minimal.
- Hide all edge labels by default.
- Select the root node initially and show its actual metadata in the inspector.
- Derive entity-type and relationship filter options from the loaded response. Do not offer values not present in the response.
- Show counts from loaded nodes/edges only. Do not imply total database counts unless returned by the API.

### Selection

- Clicking a node selects it, clears edge selection, applies the selected class, and updates the node inspector.
- Clicking an edge selects it, clears node selection as defined by the existing page behavior, applies the selected class, shows that edge label only, and updates the relationship inspector.
- Clicking empty graph space clears the selection to the summary inspector only if that behavior is implemented consistently; otherwise retain the current selection.
- Inspector navigation actions appear only when the selected entity type and actual identifier support them. Preserve current Person links to profile, timeline, and findings.

### Search within loaded network

- Search is local to the currently loaded nodes. It must never call the catalog entity-search endpoint.
- Trim input, support a blank state, and match node label and identifier case-insensitively.
- Highlight matches without removing non-matches. Show a compact `N matches` status and an explicit no-match message when a non-empty query has no loaded matches.
- Search does not change selection automatically. Selecting a highlighted node remains an explicit investigator action.

### Filters

- Entity filters are multi-select and apply Cytoscape classes to nodes and incident edges; they do not delete elements or refetch.
- Relationship filters are multi-select and apply classes to edges; incident nodes remain available so the investigator can understand context.
- If filters hide the selected node or edge, retain the selection in state but show a clear `Selected item is hidden by filters` notice and provide `Show all` or reset access.
- The visible count reflects the filtered view; the loaded count remains available in the status strip.
- Reset restores all loaded entity and relationship types, clears search/focus, selects the root, and returns to depth 1 only after a depth-2 expansion has occurred.

### Focus, fit, reset

- `Focus selection` shows the selected node and its immediate loaded neighborhood. If the current selection is an edge, focus around both endpoints or disable the command with an accessible explanation.
- Focus is a view-class operation only. It must not mutate the response or trigger a request.
- `Fit network` calls Cytoscape `fit()` on the existing instance and respects the current visible/filter state.
- `Reset view` restores root-centered depth-1 presentation, selections, filters, search, and focus. It should not create a new Cytoscape instance.

### Explicit depth-2 expansion

- The command is visible only after a successful depth-1 response and is labeled `Expand to depth 2`.
- While expanding, keep the depth-1 graph visible and disable duplicate expansion requests. Show progress in the graph status area and preserve the current selection until the response succeeds.
- On success, replace the bounded response, keep the root centered, preserve the selected ID if still present, and recompute filter options from actual loaded data. Do not automatically expand beyond depth 2.
- On failure, retain the depth-1 graph and selection, show a retryable expansion error, and do not claim that depth 2 is loaded.

## Inspector States

### Summary state

Show when no node/edge is selected: loaded node/edge counts, current depth, active filter/search/focus summary, and a short prompt to select a node or relationship. Do not show invented risk, confidence, relevance, or connectivity metrics.

### Node state

Show actual entity type, label, identifier, and `properties`. Include optional analytics/community fields only when returned by the backend. Render absent/null/empty values as `Unavailable`; never synthesize values. Show connected-entity count only when it is computed from the loaded graph or returned by the API, and label its scope clearly as `Loaded network`.

### Relationship state

Show actual relationship type, source, target, and returned `properties`. Surface timestamp, source, evidence, case, confidence, and method only when present. Keep the edge label visible only while selected. Do not convert absent provenance into a placeholder source or confidence score.

## State Matrix

| State                      | Graph area                                                           | Controls                                                         | Inspector                                               | Recovery/action                         |
| -------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------- |
| Initial loading            | Stable skeleton/spinner with bounded-network message; no stale graph | Disable commands that require data; avoid duplicate loads        | Loading placeholder                                     | Automatic request; no fabricated counts |
| Ready depth 1              | Radial root-centered graph, progressive labels, hidden edge labels   | Search/filter/focus/fit/reset enabled; depth-2 expansion enabled | Root node or summary                                    | Normal interaction                      |
| Expanding depth 2          | Keep depth-1 graph visible; show non-blocking expansion progress     | Disable expansion; local view actions remain usable              | Preserve current selection                              | Retry expansion on failure              |
| Ready depth 2              | Same radial semantics with explicit depth indicator                  | Filters/search/focus/fit/reset enabled; no depth 3 action        | Preserve selected item when present                     | Reset returns to depth 1 presentation   |
| Empty                      | Empty graph state, no misleading canvas                              | Retry and return-to-profile available                            | Explain no connected entities                           | Retry request or navigate back          |
| Error before first success | No graph data; structured investigator message                       | Retry enabled; other graph commands disabled                     | Error summary with request ID only where appropriate    | Retry without duplicate request         |
| Error during expansion     | Keep last successful depth-1 graph                                   | Retry expansion; local actions remain enabled                    | Preserve existing selection and explain depth-2 failure | Retry or continue investigating depth 1 |
| Search no match            | Graph remains intact; no-match status                                | Clear search action                                              | Keep current inspector selection                        | Clear query                             |
| Filter hides selection     | Graph classes hide selected item                                     | Show all/reset action                                            | Notice that selected item is hidden                     | Clear filters or select visible item    |

## Accessibility and Feedback

- Use `aria-live="polite"` for load/expand status and match/count changes; use `role="alert"` for request failures.
- Every icon-only control has an accessible label. Every toggle exposes `aria-pressed`; filter controls expose checked state and group labels.
- Preserve keyboard focus after search/filter changes and return focus to the triggering control after drawer close.
- Do not use color as the sole entity-type or selection signal. Pair accents with labels, shape/border treatment, or inspector context.
- Keep error copy investigator-facing and stable. Technical request IDs may be shown as secondary diagnostic text, never raw driver/query errors.

## Acceptance Checks

1. Opening P001 requests one depth-1 network and renders a centered root with first-hop labels and no edge labels.
2. Selecting a node or edge updates the inspector with only returned data and does not create another Cytoscape instance.
3. Entity and relationship filters alter visibility/classes without refetching or losing normalized elements.
4. Loaded-network search highlights local matches, reports no matches, and never calls catalog search.
5. Focus, fit, and reset work without remounting the graph; reset restores root/depth-1 state.
6. Explicit depth-2 expansion retains the depth-1 graph while loading, prevents duplicates, preserves selection on success, and retains depth 1 on failure.
7. Loading, error, empty, search-no-match, and filter-hides-selection states are visible and recoverable.
8. Desktop and narrow layouts keep graph, controls, and inspector usable; drawers/stacking do not remount Cytoscape.
9. Browser validation records no React hydration, Cytoscape, or console errors for the P001 acceptance sequence.

## Risks and Limitations

- The current page has no explicit relationship filter or depth-2 action; the frontend implementation must add those without changing the API route meaning.
- The current graph labels edge data even though the default label value is blank; selection-only labeling must be enforced in the final style contract.
- The current mobile layout stacks controls before the graph via CSS order; the implementation should preserve graph-first investigator flow on narrow screens.
- Live Neo4j data availability is an environment prerequisite for browser validation; this artifact does not claim runtime coverage.
- No optional pathfinding, comparison, playback, export, or community visualization is specified.

## Test Results

- Command: Not run; planning artifact only.
- Passed: 0
- Failed: 0
- Skipped: 1 (implementation and browser validation belong to downstream frontend/tester tasks)

## Task Notes

- Charter source: expected UX charter reference was not present in the checked-out extension/workspace paths; constraints were derived from the assigned task, approved session plan, and t1 architecture artifact.
- Scope: one planning artifact, one frontend subsystem, medium complexity.
- Timing: local timestamp captured as `2026-09-30T12:54:51.1772100+05:30`; UTC conversion unavailable through the provided PowerShell parameter set.
