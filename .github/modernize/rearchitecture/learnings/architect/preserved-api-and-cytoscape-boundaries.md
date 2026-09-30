# Preserved API and Cytoscape boundaries

- Keep existing FastAPI route meanings and Pydantic response shapes stable; use additive optional metadata for analytics/provenance.
- Treat `NetworkGraph` as the sole Cytoscape owner: initialize once per container, synchronize elements/classes through refs, and destroy only on unmount.
- Keep request state and investigator controls in the page; keep graph rendering and event translation in the Cytoscape component.
