# Evidence and screenshot provenance

`results.json` contains historical observations with per-claim source IDs and evidence classes. `economics.csv` records the app's rounded compute totals. These files are transcriptions of accessible conversation results, not raw logs or dashboard exports.

## Attachment access

The referenced conversation was read through the supported conversation reader. Its returned page had no older cursor. Image messages were returned as notices such as “User attached 5 images; image contents were not included.” No screenshot pixels or downloadable attachment paths were exposed. No screenshots were present in the lab directory. Earlier attachments in the full conversation could not be inspected. **No conversation screenshot has been included in this public package.**

The exact retrieved conversation response, original file SHA256 inventory and credential findings are preserved under ignored `.private/`; that directory must never be uploaded. Original code is separate from the revised working files.

## Screenshots to supply for a visual evidence edition

| Priority | Image | Retain only |
| --- | --- | --- |
| 1 | Successful direct cloud response | HTTP 200, generated response, 42/126/168 token usage and 161.44s if visible |
| 1 | Invalid-token test | Deliberately fake input label, HTTP 401, PASS line |
| 1 | App usage resource breakdown | $0.18 app cost and $0.13/$0.04/$0.01 resource rows |
| 2 | T4 / deployment view | GPU type, app role and running-state evidence |
| 2 | Local Unsloth response/API monitoring | Model format, successful request/response |

Supply the original attached images, ideally all of them, so each selected crop can be checked in context. Do not recreate terminal outputs or substitute screenshots of this report as execution evidence.

## Sanitization procedure

1. Store originals under `.private/raw-evidence/` and record SHA256, byte count, source message ID and capture date when known. Never edit the original.
2. Inspect the complete original at full resolution before selecting it. Omit an image if its sensitive content cannot be isolated reliably.
3. Crop to the evidence-bearing panel. Remove browser chrome, profiles, workspace/account names, usernames, home paths, notification banners, sidebars, personal tabs, balances, payment details, account IDs and token-bearing URLs.
4. Use solid opaque masks for any residual credentials, secrets, API keys, endpoint identities, signed links or personal identifiers. Do not use blur or translucent overlays. Keep the experiment's $0.18 resource cost; remove account balances and payment data.
5. Flatten into a fresh PNG, remove metadata and inspect the actual exported file at normal and enlarged zoom. Run OCR as a second check, then inspect visually again. Verify each output against its original and the disclosure list.
6. Add only reviewed exports to `evidence/screenshots/`. Record source hash, output hash, crop/mask description, reviewer and review outcome in a manifest. Replace “conversation-reported” labels only for claims directly verified against the supplied pixels.
7. Review the final Git diff/export, rendered README, video frames and captions. Do not publish raw logs, shell history, raw screenshots or private provenance files.

No sanitization or screenshot review is claimed until that export-and-inspection process is complete.
