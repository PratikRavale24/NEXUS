# Bounded Neo4j Projections

Variable-length path expansion followed by a path-row `LIMIT` does not independently bound projected nodes and relationships.

## What Happened

During NEXUS t3, the network service was found to expand `[*1..depth]` and unwind path nodes before Python-side truncation. The redesign contract requires depth 1 by default, explicit depth 2 only, and independent node/edge limits.

## Takeaway

Use fixed depth branches or bounded subqueries, deterministic ordering, stable identifier deduplication, and separate node/edge limit enforcement. Keep loaded-network filters client-side unless a future server filter has a validated allowlist.

## History

- 2026-09-30 (NEXUS/t3): initial
