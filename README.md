# VRChat AI Recovery

An AI-assisted workflow and offline tools for recovering editable Unity avatar assets from local evidence. The guide records a successful mesh, texture, full-rig and expression reconstruction, including the failures that initially produced an incomplete model.

**This is a recovery workbench, not a one-click VRChat client ripper.** It does not attach to VRChat, decrypt protected downloads, fetch avatars, or reconstruct an author's original Unity project. Build-specific live-object readers are not included. Bring files you are authorized to process.

## Quick start

Python 3.10 or newer; no dependencies, account, API key or network request required.

```sh
# Extract plausible plaintext UnityFS containers from a file you supply.
# The output directory must not already exist.
python3 recover.py carve /path/to/local-file --out work/bundles

# Inspect a reconstructed model, without printing its embedded names or paths.
python3 recover.py inspect /path/to/model.glb

# Create a brief for your existing local coding assistant.
python3 recover.py plan /path/to/model.glb > work/ai-brief.md

python3 -m unittest discover -s tests -v
```

Create `work/` before redirecting a brief there if it does not exist. Carving streams data in 1 MiB chunks, checks supported UnityFS header fields and declared file bounds, and records SHA-256 hashes. It does **not** decompress or validate bundle payloads; use a Unity-aware parser such as AssetRipper on the extracted copies. A protected/unsupported input may produce no readable bundles. The tool does not search for keys.

GLB inspection checks container/chunk layout and bufferView ranges, reports joint/morph/material/animation counts, and flags external URIs and material-pointer animation. It does not load external resources or prove valid skinning, accessor contents, shader fidelity or visual correctness. `plan` generates a deterministic evidence brief for an assistant you already use; it does not call an AI service or upload anything.

## The recovery workflow

Read [the complete recovery wiki](docs/vrchat-model-recovery.md) and [the assistant instructions](AGENTS.md).

1. Establish the selected avatar, exact source build and permission/provenance.
2. Prefer source packages or readable serialized bundles. Extract from copies.
3. Where permitted runtime evidence already exists, verify its structure against the exact engine build. This repository does not collect it from a protected client.
4. Rebuild geometry, skinning and the complete helper hierarchy. Recover matching texture pixels independently.
5. Identify how expressions actually work: morphs, bones, texture swaps or combinations.
6. Preserve source configuration separately from behaviours implemented in the destination.
7. Reopen, deform, render and reimport the result. Record uncertainties and confirmed failures.

The documented case recovered a 5,523-vertex model with 121 bones and 24 portable morph targets. Blink and speech used texture frames. Its GLB material animation worked in Blender 5.2; its Three.js VTuber integration required an explicit atlas adapter. SDK physics settings were preserved as data, not simulated. These are case results, not universal expectations.

## What is included

- `recover.py`: readable UnityFS carving, GLB inspection and local AI briefs.
- `docs/vrchat-model-recovery.md`: method, source contracts, verification, pitfalls and limits.
- `tests/`: synthetic fixtures generated in memory; no game files.
- `AGENTS.md`: workflow for AI coding assistants.

No extracted avatars, worlds, voice files, proprietary binaries, memory dumps, captures, private configuration or authoring packages are distributed. Project-relative evidence paths in the case study refer to private local records and are not included here. Public documentation is not a grant of rights to third-party assets.

## Contributing

Use synthetic test inputs. Keep real captures and exports outside version control. Before publication, scan the complete Git history and inspect configuration, archives and generated files for credentials and personal data. Never include client protection bypasses, credential extraction or unrelated account data.

This project is independent of VRChat, Unity, AssetRipper and avatar creators. Code and original documentation are MIT-licensed; third-party assets are excluded.
