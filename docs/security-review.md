# Secret audit and publication review

## Findings

The original `auth_test.py` contains the deliberately fake value `invalid-test-key`, also present in two editor-history copies. It is a negative authentication-test fixture. The revised script preserves this purpose and returns a failing exit status if the local server accepts it.

No live API credential, Modal proxy-token literal or account-token literal was identified in the scoped lab files, editor history or available Git objects. Real credentials in the original positive clients were supplied through hidden prompts or runtime environment variables. The available conversation text omits screenshot pixels, so exposure in those images cannot be assessed. Revoke any credential that appeared visibly in the original images before reusing it.

## Git boundary

At inspection, the lab had no `.git` directory. Git resolved to an unrelated parent repository in the home directory. Path-scoped status showed the lab untracked, and path-scoped all-ref object enumeration found no lab objects or commits. No parent Git files, remotes, branches or history were modified. Lab 7 initialized a separate local repository, preventing accidental home-directory staging. The owner subsequently authorized a scoped initial publication to `Etherlabs-dev/domainos-inference-lab`.

The audit checks the new repository's working publication set, index, all-ref and reflog-reachable blobs, and dangling blob objects. At the initial audit there were no commits or historical lab blobs; the publication audit is repeated against the actual staged and committed tree. It does not scan unrelated home-repository objects, shell history or account-wide configuration. It does scan the lab's original `.history/`, source, discovered env/log/text/capture files and private preservation set separately, reporting paths and line numbers only. The lab contained no raw screenshots, terminal captures, `.env` files or logs outside the excluded installed environment.

`.venv/` is installed third-party code and is excluded from publication, along with its machine-specific configuration. The public package excludes environment files, private provenance, caches, credentials, model weights, raw recordings, marketing drafts and private production plans. The bundled Virgil font is byte-matched against a reviewed asset manifest and includes its original font license. Never upload the whole directory as an unfiltered archive.

## Client controls

- Runtime credential input replaces literals; exceptions show status or a generic transport message, without raw response bodies or URLs.
- Cloud origins must use HTTPS Modal hosts; loopback HTTP is limited to the local path.
- Redirects and ambient proxies are disabled so authorization headers are not forwarded through them.
- Response bytes are capped; JSON structure and expected served-model identity are checked.
- Readiness polls 503 only with an explicit wait flag; chat POSTs are never automatically retried.
- Authentication test rejects unexpected results and includes a valid-key positive control.
- Cloud scripts and remote check entrypoints require explicit `--allow-cloud`. Deployment itself remains a deliberate Modal CLI action.

These are local code controls and regression checks. Historical HTTP 200/401 results establish basic proxy authentication, not customer isolation or a full production security audit.

## Safe publication procedure

1. Review the original images for credential exposure when supplied. Rotate or revoke any exposed credential and confirm that privately; never paste the replacement into this repository.
2. Keep inaccessible screenshots out. Any later images must pass the complete export-and-inspection workflow in `evidence/README.md`.
3. Run `python scripts/audit_secrets.py` and inspect the intended public paths. Run `python scripts/audit_secrets.py --include-private` only privately; any newly discovered findings produce a failing exit status; the exact invalid test fixture is allowed.
4. Review the exact candidate files, not the entire folder. `.gitignore` cannot remove previously tracked files; inspect the index and Git audit after any future staging or commits.
5. Select the project's redistribution license and validate the chosen release file set. Inspect the rendered README, SVG and final recording frames. Do not include private backups, editor history, shell captures, account balances, raw credentials or unreviewed screenshots.
6. Obtain separate user approval before creating a public remote, committing/pushing or posting the case study/video. The owner authorized the scoped initial GitHub commit/push; that does not authorize future cloud spending or unrelated publication.

The included scanner is a local pattern/assignment detector, not a proof that arbitrary text or imagery contains no secret. Manual candidate-file review and image inspection are required at the actual publication step.
