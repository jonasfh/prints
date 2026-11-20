# Prints

Et lokalt repository for ulike 3D-design og parametriske modeller laget for mulig 3D-printing senere.

## Verktøy

Designene i dette repoet lages primært med **SolidCraft** (parametrisk 3D CAD med GUI, CLI og MCP-støtte).

- **Kildefiler:** `.sc` (SolidCraft design-container) eller `.json`
- **Eksport for slicing / 3D-print:** `.3mf` (anbefalt) eller `.stl`
- **CAD-utveksling:** `.step` / `.stp`

## Foreslått mappestruktur

Etter hvert som det blir flere prosjekter kan det være ryddig å organisere hver del eller hvert prosjekt i sin egen mappe:

```text
.
├── AGENTS.md           # Instruksjoner for AI-agenter ved 3D-modellering
├── README.md
└── designs/
    └── <prosjektnavn>/
        ├── <del>.sc    # Parametrisk kildefil i SolidCraft
        ├── <del>.3mf   # Eksport klar for slicer
        └── README.md   # Valgfrie notater (materiale, laghøyde, toleranser, osv.)
```

## AI-assistert modellering

Se [AGENTS.md](AGENTS.md) for retningslinjer rundt parametrisk design, verifisering og bruk av SolidCraft MCP når du bruker en AI-agent til å lage eller endre modeller.
