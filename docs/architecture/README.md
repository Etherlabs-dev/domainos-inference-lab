# Handwritten architecture diagrams

I use Virgil handwriting, rough orange connectors, warm text and charcoal previews, with 28% of the canvas reserved for the presenter. The `.excalidraw` files contain editable objects on a light-source palette; the dark and light SVGs provide recording previews.

The diagrams cover component roles, local serving, cloud serving, authentication, readiness, economics and the recap. `architecture.svg` and `architecture.excalidraw` are the cloud-overview aliases used by the README.

`spec.json` contains the final diagram states. `source-manifest.json` records their hashes and source sections. The complete 26-state presentation lives in my tutorial library.

## Rebuild

```sh
npm ci --prefix docs/architecture/renderer
python3 docs/architecture/build.py --output /tmp/domainos-architecture-rebuild
```

Use a fresh output directory for each revision. The renderer produces editable scenes, SVG previews and PNGs. It uses Rough.js and outlined Virgil glyphs; the font license is included in `renderer/fonts/`.

Open a scene in Excalidraw to edit its objects. For recording, check text fit at the intended zoom and leave the presenter area clear.
