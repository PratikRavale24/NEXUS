## [t1] Preserved architecture and graph lifecycle contract

- Codebase/domain discoveries: FastAPI already has a module-scoped Neo4j driver and shutdown close; the network route is person-centric with depth 1..2 and node/edge bounds. The current Cytoscape component already has cleanup but combines mount, element replacement, layout, and view-state updates across effects.
- Wrong assumptions and corrections: coordinator context/decisions/log files were absent; the approved design source was session memory and the live source tree.
- Debugging dead-ends and what actually worked: the documented PowerShell `Get-Date -AsUTC` form is unsupported on this host; `(Get-Date).ToUniversalTime().ToString('o')` captured UTC successfully.
- Techniques/patterns worth reusing for future tasks: preserve existing route/response shapes, make optional metadata additive, and specify Cytoscape ownership as mount/data/view/command boundaries.
- Learnings consumed: none — architect learnings directory was empty.
