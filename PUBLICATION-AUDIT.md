# Initial publication audit

Audit date: 2026-11-09.

The initial publication contains original Python source, synthetic tests, a recovery field note, assistant instructions, a README, this audit and the MIT license. No extracted avatar/world data, voice files, screenshots, captures, process snapshots, archives, third-party binaries or credentials are included.

Checks performed before the initial public push:

- All published source and documentation scanned with `detect-secrets`; no findings.
- Separate inspection for private user paths, account/deployment configuration, nonpublic hosts, local network addresses, cloud/device identifiers and credential files.
- Every file in the initial commit and source archive reviewed; only the documented source files are included.
- All local Git refs and commit metadata checked. Fresh history contains one initial commit with a generic contributor identity; no imported project history or private branches/tags.
- Ignore rules exclude common local evidence, credential, export and capture formats. Ignore rules were not used as a substitute for checking published content.
- Synthetic tests passed. A local GLB inspection was exercised without copying that model or its generated report into the repository.

Project-relative case-study evidence paths identify files not distributed here. The engine binary hash identifies an analyzed software build, not a personal device. Synthetic test strings are deliberately generic. Public upstream/project names are intentional attribution.

This record describes the initial publication, not an automatic guarantee for later changes. Repeat the scans and configuration/content review for every public update, branch, tag, source archive and release artifact.
