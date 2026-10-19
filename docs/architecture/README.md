# Handwritten architecture snapshots

The diagrams use the same Virgil handwriting, rough orange connectors, neutral charcoal previews and 28% presenter-safe layout as the tutorial. Each `.excalidraw` scene has editable light-source objects; `*-light.svg` and dark SVGs are separate exports.

`architecture.svg` and `architecture.excalidraw` are the cloud overview aliases used by the README. The other named files cover roles, local serving, authentication, readiness, economics and the recap. `spec.json` contains the reviewed final states; `source-manifest.json` identifies the canonical production section and output hashes. The full 26-reveal tutorial master lives in the user's canonical content library.

## Rebuild locally

```sh
npm ci --prefix docs/architecture/renderer
python3 docs/architecture/build.py --output /tmp/domainos-architecture-rebuild
```

Choose a new output directory on later runs. The build uses local Node packages and makes no cloud inference requests. It produces full-size preview scenes and exports under that directory. Virgil's original license is retained under `renderer/fonts/`. No project-wide open-source license has been selected.

All 26 production reveal exports were rendered and visually reviewed, with measured Virgil text bounds and reciprocal arrow bindings. Native Excalidraw import/edit and Light/Dark/System behavior are not yet certified: the available browser interface did not expose a working file-import control. Inspect those in the native editor before recording. These SVGs are Rough.js exports with outlined glyphs, rather than native Excalidraw pixel-identical exports.
