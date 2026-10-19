# Lab 7 validation record

Date: 19 October 2026. Environment: existing local virtual environment, Python 3.14.2 and Modal 1.6.2. The remote image definition uses Python 3.12.

| Check | Actual result |
| --- | --- |
| Offline HTTP, readiness, auth, audit and guard tests | 32 passed in the installed project |
| Deployment definitions | Imported and registered with the installed Modal 1.6.2 SDK; no remote execution |
| Python syntax | All public Python sources parsed |
| Public text/file secret audit | Zero findings |
| Original/private/history secret audit | Zero findings; exact invalid test fixture allowed |
| Git boundary | Initial audit found no lab commits. The owner authorized the scoped initial GitHub release; staged contents and resulting commit are audited separately. |
| Original preservation | SHA256 verified for all 39 original source/history files; nine root scripts backed up privately |
| Architecture scenes | Seven handwritten final-state snapshots; 26 canonical reveal states passed geometry, binding and source checks |
| Architecture exports and presentation | All 26 reveal exports visually reviewed; browser navigation, theme, notes, marker toggle, hide/restore and end boundary checked |
| Local documentation links | All relative Markdown links resolve |
| Cloud actions during packaging | None |
| Screenshot inclusion | None; original attachment pixels were unavailable |

The 32 tests exercise real loopback HTTP for successful JSON, authentication headers, redirects, error suppression, size limits, malformed responses and POST failure behavior. Mocked tests cover readiness deadlines, 503-to-ready transitions, auth rejection/acceptance, script opt-in guards and the scoped audit detector. All requests remain local or mocked.

Historical Modal 200/401 responses and cost observations belong to Labs 5–6 and retain their conversation provenance in the experiment report. The changed client and server shutdown handling have not been rerun in the cloud. Native Excalidraw import/edit and appearance checks remain a recording preflight item; the available browser interface did not expose a working file import.

## Repeat local verification

```sh
python -m unittest discover -s tests -v
python scripts/audit_secrets.py
python scripts/audit_secrets.py --include-private
```

Run the private-inclusive audit privately; it reports locations and categories only. Current zero findings do not clear unseen screenshot pixels or future staged changes. Recheck the exact publication set before posting.
