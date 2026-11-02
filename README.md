# Accord testing workspace

An empty implementation workspace for a ground-up RSR-based Accord redesign. No plugin implementation, session controls, intent model, hotbar logic or migration is included.

Stable Accord remains in kaldigo/FFXIVAccord with its own identity, versions and publish flow. Future testing builds use AccordRSRTesting in this repository so stable updates can continue independently.

The build workflow validates this workspace. The manual publish workflow is scaffolded but refuses to release anything until release-config.json names an implemented project. The install feed is currently empty. Previous 0.1.0.0 experiment releases are withdrawn.

The RSR fork retains its original RotationSolver identity, configuration and behaviour. Its only runtime addition is the settings interface described in the fork's SETTINGS-API.md. This workspace does not pin or bundle an engine yet. Migration is deferred.
