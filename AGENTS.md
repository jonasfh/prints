# AGENTS.md

Instructions for AI agents working on 3D designs in this repository using **SolidCraft** (via MCP and/or CLI).

## Common Agent Instructions

General workflow, documentation, testing, and architecture conventions are shared via the `.agents/common-agent-instructions` submodule:

- **[Workflow Guidelines](.agents/common-agent-instructions/WORKFLOW.md)**
- **[Documentation Standards](.agents/common-agent-instructions/DOCUMENTATION.md)**
- **[Testing & Quality Assurance](.agents/common-agent-instructions/TESTING.md)**
- **[Architecture Standards](.agents/common-agent-instructions/ARCHITECTURE.md)**

Where 3D CAD / SolidCraft-specific rules below conflict with general software-project rules in the submodule, the SolidCraft rules in this file take precedence.

## Repository Purpose & Conventions

- This repository stores parametric 3D designs intended for potential 3D printing.
- Organize projects cleanly under `designs/<project-name>/` (or follow existing folder conventions once established):
  - **Source designs:** `.sc` (SolidCraft container, default) or `.json` when plain JSON is explicitly desired.
  - **Print exports:** `.3mf` (preferred for slicers) or `.stl`.
  - **CAD interchange:** `.step` / `.stp`.
- Keep designs **parametric**: expose key dimensions, wall thicknesses, and print clearances/tolerances as named parameters so parts can be tuned easily after test prints.

## SolidCraft MCP Workflow

1. **Coordinate System & Units**
   - Units are **millimetres (`mm`)** and **degrees (`deg`)** in expressions.
   - **Z is up.** Orient parts for printing with the primary bed-contact face flat on `Z = 0` when practical.

2. **Start Properly**
   - For anything beyond a single primitive, read `skill_reference` (`{"skill": "solidcraft-modeling"}` / `file: "SKILL.md"`) first for command shapes, IDs, plane axes, worked examples, and known traps.
   - Run `inspect_design` (`{"measure": false, "sketches": false}`) to check the current design state before making changes.
   - **Live / GUI viewing:** The user generally wants to see designs in the SolidCraft app. If `inspect_design` reports a headless session (`Backend: headless`), either prompt the user to start SolidCraft before building (so the session bridges to the app live) or, after saving the `.sc` file, check if SolidCraft is already running (`pgrep -x solidcraft`). If not running, open it (`solidcraft <file.sc>`); if already running, do not launch a duplicate window (which triggers a file-lock / Read-Only dialog) — tell the user the file is saved so they can reload it in their existing window.

3. **Plan Before Building**
   - Calculate parameters, expected volume, bounding box, and world pick coordinates (`[x, y, z]`) before executing.
   - Use `list_commands` with a `filter` (never unfiltered) and `describe_command` to verify command schemas.
   - Build in `batch` calls (all-or-nothing, `verbose: false`) and **name every feature**.
   - Prefer primitives (`solid.box`, `solid.cylinder`, `solid.hole`, `solid.fillet`, `solid.shell`, patterns, mirror) with expression fields for simple geometry. Use sketches when the profile is not a box or circle.
   - Order features cleanly: fillet outside edges before shelling; add internal features after shelling; add holes and wall cuts last (specify explicit depth for blind holes or single-wall cuts).

4. **Keep It Parametric**
   - Use parameter expressions (e.g. `"L/2 - 10"`) in feature fields, sketch dimensions (referenced to `"origin"` or edges), and pattern spacings rather than hardcoded numbers.
   - Every sketch must end fully constrained (`dof 0`, checked via `sketch.solve`).

5. **Verify Every Stage**
   - Run `measure` after each major stage and compare volume and bounding box against your expected numbers (`ok: true` alone does not catch missed cuts or non-touching joins).
   - Use `body_topology` to verify hole/boss positions, cylinder origins, axes, and radii.
   - Use `check_parameters` to verify that changing parameters updates the model cleanly without errors.
   - Use `screenshot` / `compare_picture` for visual inspection when helpful.

6. **Fix In-Place, Don't Rebuild**
   - Correct mistakes using `timeline.edit`, `parameters.change`, or `edit.checkpoint` / `edit.restore_checkpoint` rather than starting over.

## 3D Printing Design Guidelines

- **Clearances & tolerances:** Parameterize fitment clearances (typically `0.2`–`0.4 mm` for FDM sliding/press fits depending on printer/material) instead of baking them into raw dimensions.
- **Printability:** Prefer chamfers over fillets on bottom edges touching the build plate to avoid steep overhangs; avoid unsupported overhangs > 45° where possible; keep wall thicknesses reasonable for standard nozzles (e.g. multiples of `0.4 mm` / >= `1.2`–`1.6 mm` for structural walls).
- **Clarify constraints:** If a part has tight mechanical tolerances, load-bearing requirements, or specific material/nozzle constraints, ask the user before assuming values.

## Saving & Exporting

- Save native files with `save` (`.sc` by default). Note that SolidCraft MCP restricts saving to allowed directories (the opened/saved design folder, recovery folder, or paths configured via `--allow-path`).
- Export print-ready meshes using `export` (prefer `.3mf` or binary `.stl`) only when requested or when wrapping up a completed part.
- For automated CI exports, each design folder may include a `deploy.yml` manifest (with `name`, `version`, `source`, `formats`, and `pieces` with optional `label` and `params`). Changes to `designs/` trigger `.github/workflows/deploy-designs.yml` on PRs (artifacts) and `main` (GitHub Releases).
- **Version bump reminder:** Whenever you modify an existing design or its `deploy.yml`, always bump `version` in `deploy.yml` (e.g. `0.0.1` → `0.0.2`); PR checks enforce this.
