# RSR intent redesign

The goal is a better intent-button experience backed by RSR, with stable Accord available independently. Existing Wrath switches and button groupings are evidence about useful control, not a required RSR design.

## Decisions already implemented

- Separate client source, plugin/configuration identity, command and distribution feed.
- Separate engine identity and configuration, with upstream source history retained.
- Session-only opt-in and automatic stop on lost heartbeat or conflicting loaded stable plugins.
- Native RSR rotation baseline and read-only observation of existing cached selectors.
- No stable settings import, hotbar writes, or changes to stable release workflows.

## Design to explore

Model three distinct choices: which intent a button expresses; which responsibilities the player delegates automatically; and how the engine continues an accepted sequence. Do not require a single toggle to own all three.

Candidate intents are damage with ST/AoE preference, targeted healing, party healing, personal protection, party protection, burst initiation, job-mechanic initiation, mobility, recovery and utility. These are evaluation categories, not a final button count or a commitment to one control per category. Invulnerability, channels, ground placement and short ally protection require individual treatment.

RSR's healing, defence and movement selectors are starting points. Its emergency methods mix burst initiation, resource preparation and survival actions. Its defence routines can include recovery tools. AST draw initiation appears in multiple paths, and NIN maintains mutable mudra aims. Ownership must be applied at the actual action decision, including countdown, emergency, general and duty paths.

A future intent request needs recipient preference, damage targeting preference, automatic versus deliberate origin, resource/reserve policy, and initiation permissions. A selected decision must capture the action, exact recipient or ground position, and state/revision needed to reject stale execution. Preview calls must not accept a sequence. Execution must revalidate eligibility against the same recipient and confirm action effects before granting continuation. Do not execute mutable cached preview objects directly.

Start with WHM and PLD, then DNC and BLM. Compare native RSR and modified intent behaviour for manual burst holds, damage during held mechanics, healing choice, recipient selection, mitigation overlap, movement and recovery. Check targeted and party healing independently of automatic healing. Review other jobs, PvP and noncombat coverage before considering replacement of stable Accord.

## Release independence

The stable repository, package identity, version stream and feed remain unchanged. This repository owns AccordRSRTesting and a feed containing AccordRSRTesting/AccordRSREngine only. No experimental version is published under Accord's identity or its TestingAssemblyVersion. Stable hotfixes never need an experimental merge. Experimental publication remains manual while native validation and design are evolving.
