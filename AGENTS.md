# Accord RSR testing

This independent repository is the RSR redesign. Stable Accord remains in kaldigo/FFXIVAccord and must retain its own release history, identity and updater. Never publish this project as Accord or replace the stable feed. Assembly/config identity: AccordRSRTesting. Command: /accordtest.

Use the full engine commit in engine-validation.ref. Do not inherit the Wrath preset pack, hotbar assignments or four automation switches by default. The initial client is a native-RSR baseline and selector workbench. Real intent execution and policy redesign are subsequent work, not existing features.

Runtime consent is session-only. Never persist it or start a session on login. Preserve engine identity/version checks, lease heartbeats and explicit End. Keep stock and experimental settings independent. Do not read personal plugin configurations into this repository.

Build with tools/build.ps1, run the engine lease suite, and use tools/package.py to validate isolated packages before release. Releases use their own opt-in feed, not Dalamud's testing-version field for stable Accord. Publication is manual during the redesign. Do not overwrite published versions. Native acceptance must be reported separately.
