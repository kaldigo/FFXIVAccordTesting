# Accord RSR Test

An opt-in RSR-based Accord redesign, independent of [stable Accord](https://github.com/kaldigo/FFXIVAccord). Stable fixes and updates can continue without merging this experiment. The client is built from new source rather than inheriting the Wrath settings and hotbar implementation.

## Initial testing build

This build provides an isolated test session, native RSR rotation controls and observations of RSR's existing intent selectors. It is a baseline for redesigning intent buttons and automation ownership. It does not yet apply hotbars, execute intent buttons or reproduce Accord's four automation switches. RSR's own detailed settings govern rotation, healing and defence during the experiment.

Both packages have separate identities and configuration stores:

| Plugin | Internal identity | Command |
|---|---|---|
| Accord RSR Test | AccordRSRTesting | /accordtest |
| Rotation Solver Reborn - Accord Test | AccordRSREngine | /rsrtest or /rotationtest |
| Stable Accord, unchanged | Accord | /accord |

The testing feed is published only after package checks pass. It contains only the two experimental identities. It does not use the testing-version mechanism for stable Accord, so opting in cannot replace stable Accord or hold back its updates.

## Testing

1. Install both experimental packages from the separate testing feed.
2. Disable stock RSR before loading the fork. Disable stable Accord and Wrath before enabling a test session.
3. Open `/accordtest` and enable the session. Configure the engine through `/rsrtest`.
4. Start the rotation when ready. Manual enemy targeting still automatically executes actions. Existing RSR auto-start options also apply within an enabled session.
5. Open the engine's full control window to populate cached healing, defence and movement suggestions. These observations are not executable intent buttons.
6. End the session before returning to stable Accord/Wrath. Disable the experimental plugins and re-enable the stable plugins; their settings were not migrated.

Consent resets on client load. Loss of the client heartbeat stops execution after four seconds. A loaded stable Accord/Wrath/stock RSR or PvP also blocks execution. Nothing is installed or enabled by building this repository.

## Development

Use .NET 10 and Dalamud API 15. `tools/build.ps1` accepts the independent engine checkout and builds both plugins plus the engine's session tests. The release pair is pinned by `engine-validation.ref`. `tools/package.py` makes the two isolated archives, checksums, and a separate feed. The GitHub build workflow produces candidate artifacts only; it does not publish or modify a stable feed.

Native acceptance remains pending. Start with session expiry, reload/load order, conflicting plugins and PvP transitions before combat comparisons. [Design direction](docs/design.md) records the redesign boundaries.
