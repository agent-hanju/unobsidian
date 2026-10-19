# Changelog

## 0.1.1 — 2026-10-19

- Preserve all directed links and relationship types between nodes in a BFS
  neighborhood, including links between nodes at the maximum depth.
- Keep neighbor JSON output order consistent with the full graph.
- Reject traversal depths outside the documented 1–3 range instead of clamping.
- Return absolute resolved paths and support relative visualization output paths.
- Accept tag queries with or without the leading `#`.
- Escape HTML titles and embedded graph data in the visualization.
- Correct output-format and Canvas/Base ID documentation; explain local runtime
  requirements, offline limitations, and content-reading workflows.
- Pin the tested parser dependency and include the MIT license in the skill bundle.
- Add regression coverage for the five command scripts.
