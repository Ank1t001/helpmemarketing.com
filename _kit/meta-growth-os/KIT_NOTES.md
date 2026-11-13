# Meta Growth OS skills package (private)

The package itself is **not in this repository**. The repository is public on GitHub, so the package is kept in Google Drive instead (founder, 2026-11-13), in the same folder as the Meta Growth OS PDF overview:

- Current version: **1.5.0** (2026-11-13), Drive file `meta-growth-os-v1.5.0.zip`, ID `1yBmWGllusgdlrknVgczmMx2z7-OMOogr`, owner-only sharing. SHA-256 `885973c530367948dbc84d5b3c57d60660b8abad6b75bb6ec8536707ec5363e2`.
- Version 1.4.0 was a public download until 2026-11-12 and remains in this repository's git history (`meta-growth-os.zip`, removed in `fb050e0`); `/meta-growth-os.zip` now 301s to `/meta-growth-os`.

Never commit the package, its skill files or a zip of it here, on any branch: every branch of a public repository is readable.

## What 1.5.0 changed (from 1.4.0)

- One small-sample rule, the judgement window in `meta-benchmarks/references/benchmarks.md`: at least 7 days **and** ~50 conversions of the result being judged, counted at the level being judged, outside the learning phase (founder, 2026-11-13). Other skills refer to it and never restate a different threshold. Faults (delivery errors, disapprovals, learning status changes, stopped CAPI streams, events that stopped firing, attribution changes) are exempt and reported immediately.
- `meta-drift` separates faults from performance regressions and never filters a fault as noise.
- Every Phase 3 tracking check leaves an evidence record (inspected, source, basis: observed behaviour, inspected configuration or user statement, observed, observed at, status); a check without one is `Needs Confirmation`.
- Every account or tracking change carries a verification spec before approval (expected result, method, when, pass or fail), and its outcome is recorded as Verified, Failed, Too early or Could not check. The drift baseline is captured only after the configuration check passes.
- A schedule is tested end to end (lookup, comparison, notification rule, delivery) before it counts as set up; otherwise its receipt says "created, not tested".
- The README's requirements now match `meta-setup`: Drive always required, the Meta connector required except in Limited Mode, CRM or store optional but always asked about; the local vault is only an outage fallback.

## Rules for a new version

- Edit from the newest Drive zip, bump `plugin.json` and the `meta-growth-os` skill version together plus each edited skill's `version`, and add the changes to the package README.
- Upload the new zip to the same Drive folder with owner-only sharing, then update the version, file ID and hash above.
- Keep package changes separate from page work. Change `/meta-growth-os` and its PDF overview only to describe what the installed package documents. With 1.5.0 installed, the package documents a post-change check, so the page may then describe approved changes as verified (founder decides when).
