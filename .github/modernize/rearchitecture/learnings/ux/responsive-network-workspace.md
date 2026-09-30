# Responsive Network Workspace

- Preserve Cytoscape mount identity while drawers/stacked responsive sections open and close; responsive UI state must synchronize through refs/classes, not remount the graph.
- Treat the graph as graph-first on narrow screens: status and canvas precede inspector and controls, while critical actions remain keyboard-accessible and explicitly labeled.
- Relationship filters are client-side classes over loaded edges; filter options and inspector fields come only from actual loaded response data.
