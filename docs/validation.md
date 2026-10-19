# Validation

I ran the local checks with Python 3.14.2 and Modal 1.6.2. The remote image uses Python 3.12.

| Check | Result |
| --- | --- |
| HTTP, readiness, authentication and audit regression tests | 33 passed |
| Modal deployment definitions | Imported with Modal 1.6.2 |
| Python source syntax | Passed |
| Markdown file links | Passed |
| Credential audit | Zero findings in the reviewed release |
| Diagram structure | Unique IDs, text bounds and reciprocal arrow bindings passed |
| Progressive drawings | 26 reveal exports rendered and visually reviewed |
| Presentation controls | Navigation, theme, notes, marker toggle and hide/restore checked |
| Published screenshots | Four exports reviewed visually and with OCR; original retained pixels verified |

## Run the tests

```sh
python -m unittest discover -s tests -v
python scripts/audit_secrets.py
```

The tests use a loopback HTTP server and mocked readiness clocks. They cover successful responses, authentication headers, blocked redirects, safe error messages, response limits, malformed JSON, readiness deadlines and single-submission chat behavior.

The [experiment report](experiment-report.md) records the cloud run and its measurements. The screenshot and billing files are linked from the [evidence index](../evidence/README.md).
