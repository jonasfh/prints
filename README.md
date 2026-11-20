# Prints

Samling av parametriske 3D-modeller og deler laget med **SolidCraft** for 3D-printing, inkludert automatisert eksport og release-bygging via GitHub Actions.

## Design i repoet

| Design | Beskrivelse | Kildefil | Deploy-konfigurasjon |
| --- | --- | --- | --- |
| `motor-sleeve` | Todelt hylse med sammenlåsende fingre og kulelåser for rund aksling | [`motor-sleeve.sc`](designs/motor-sleeve/motor-sleeve.sc) | [`deploy.yml`](designs/motor-sleeve/deploy.yml) |

---

## Mappestruktur

```text
.
├── .github/
│   ├── schemas/deploy.schema.json       # JSON Schema for validering av deploy.yml
│   ├── scripts/build_designs.py         # Byggeskript som kjører solidcraft-cli
│   └── workflows/deploy-designs.yml     # GitHub Action for PR-artefakter og Releases
├── designs/
│   └── <prosjektnavn>/
│       ├── <del>.sc                     # Parametrisk kildefil i SolidCraft
│       └── deploy.yml                   # Deklarativ eksport- og versjonskonfigurasjon
├── AGENTS.md                            # Instruksjoner for AI-agenter (SolidCraft MCP)
├── LICENSE                              # CC0 1.0 Universal
└── README.md
```

---

## Automatisk eksport og release (`deploy.yml`)

Hver designmappe under `designs/` kan inneholde en `deploy.yml`-fil som beskriver hvilke kropper, parameter-overstyringer og filformater som skal eksporteres.

### Eksempel (`designs/motor-sleeve/deploy.yml`)

```yaml
# yaml-language-server: $schema=../../.github/schemas/deploy.schema.json
name: motor-sleeve
version: 0.0.1
source: motor-sleeve.sc
formats:
  - stl
  - 3mf
pieces:
  - body: Half_A
    label: ID14mm
    copies: 2
    params:
      ID: 14 mm
  - body: Half_A
    label: ID15mm
    copies: 2
    params:
      ID: 15 mm
```

- **Validering:** Strukturen valideres mot [`.github/schemas/deploy.schema.json`](.github/schemas/deploy.schema.json) både i editor (via `yaml-language-server`-kommentaren) og automatisk når `build_designs.py` kjøres.
- **Pull Request:** Endrede design bygges automatisk i GitHub Actions og lastes opp som **Workflow Artifacts** (`design-exports`).
- **Merge til `main`:** Endrede design publiseres som en **GitHub Release** med tag `<name>-v<version>` (f.eks. `motor-sleeve-v0.0.1`) og ferdige `.stl`/`.3mf`-filer vedlagt.

### Teste bygging lokalt

```bash
python3 .github/scripts/build_designs.py designs/motor-sleeve/deploy.yml
```

De genererte filene havner i `dist/<name>-<version>/` (som er ignorert av Git).

---

## Oppsett av SolidCraft (GUI, CLI og MCP)

SolidCraft er et parametrisk 3D CAD-verktøy med støtte for skripting via `solidcraft-cli` og AI-assistert modellering via **MCP (Model Context Protocol)**.

### Ressurser
- **Nettside og nedlasting:** [solidcraft.io](https://solidcraft.io) / [solidcraft.io/download](https://solidcraft.io/download)
- **Dokumentasjon:** [docs.solidcraft.io](https://docs.solidcraft.io/)
- **Kildekode og releases:** [github.com/tangency-labs/solidcraft](https://github.com/tangency-labs/solidcraft)

### Sette opp `solidcraft-cli` og MCP
Etter at SolidCraft er installert (f.eks. via `.deb`, `.AppImage` eller annen pakke fra GitHub Releases), følger `solidcraft` og `solidcraft-cli` med i `PATH`.

1. **Automatisk oppsett for støttede AI-klienter:**
   ```bash
   # Legger til solidcraft MCP-server (legg til --dry-run for å forhåndsvise)
   solidcraft-cli mcp setup

   # Eller med --live for å koble direkte til et kjørende SolidCraft-vindu:
   solidcraft-cli mcp setup --live
   ```
   Støttede klienter i `mcp setup`: `opencode`, `claude-desktop`, `claude-code`, `cursor`.

2. **Manuell MCP-konfigurasjon (f.eks. Antigravity eller andre MCP-klienter):**
   ```json
   {
     "command": "solidcraft-cli",
     "args": ["mcp", "--allow-path", "/sti/til/prints"]
   }
   ```
   - `--allow-path`: Lar MCP-serveren lagre `.sc`-filer og eksporter direkte i repoet.
   - **Live-visning i SolidCraft:** Start SolidCraft-appen *før* du starter en ny AI/MCP-økt — da kobler MCP-serveren seg automatisk til det åpne vinduet (`127.0.0.1:27878`) slik at du ser modellen bygges opp live.

---

## AI-assistert modellering og lisens

- Se [AGENTS.md](AGENTS.md) for arbeidsflyt, navnekonvensjoner og retningslinjer for 3D-printing med SolidCraft MCP.
- Dette repoet er lisensiert under **CC0 1.0 Universal** — se [LICENSE](LICENSE).
