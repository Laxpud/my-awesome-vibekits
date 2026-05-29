---
name: zotero-tag-classifier
description: Classify and reorganize Zotero paper libraries with project-only Collections and tag-first knowledge organization. Use when an assistant needs to design a Zotero tagging scheme, classify papers from titles/abstracts/metadata, migrate messy Collections into Tags, or create prompts/workflows that assign Zotero tags for academic papers, especially aerospace, aircraft, control, navigation, aerodynamics, acoustics, mechanics, and related engineering literature.
---

# Zotero Tag Classifier

Use a tag-first model:

- **Collections** are project workspaces only: papers for a thesis chapter, manuscript, report, advisor export, reading batch, or temporary project.
- **Tags** are permanent knowledge classification: what the paper studies, how it studies it, what evidence it gives, and how the user uses it.

Do not classify papers by permanent topic Collections unless the user explicitly asks for Collection-based organization.

## Core Workflow

1. Inspect the paper metadata available: title, abstract, keywords, venue, year, notes, existing Collections, and existing Tags.
2. If classifying a library, first infer the user's recurring topics and vocabulary from the existing papers. Do not impose a large fixed taxonomy upfront.
3. Recommend project Collections only when a paper is actively used in a concrete project or writing workspace.
4. Assign required basic tags whenever enough information exists.
5. Add extra tags only when they are supported by the title, abstract, keywords, notes, or obvious domain context.
6. Keep tags conservative. Prefer fewer accurate tags over many speculative tags.
7. If information is insufficient, mark uncertainty and suggest what metadata is needed.

## Collection Rules

Use Collections for temporary or project-specific workspaces, for example:

- `P2026_helicopter_noise`
- `Paper_MPC_fault_tolerant_control`
- `Thesis_chapter_3`
- `Reading_batch_2026_summer`
- `To_export_for_advisor`

Avoid Collections such as `helicopter`, `MPC`, `review`, `aeroacoustics`, or `control` when they are meant as permanent knowledge categories. These belong in Tags.

## Required Basic Tags

Assign these basic tag types when enough information is available:

- `area:*` - broad research area, replacing old topic Collections.
- `task:*` - concrete research task or problem.
- `platform:*` - aircraft, vehicle, or target system.
- `method:*` - method, algorithm, theory, model, or tool used.
- `type:*` - document type.

Common examples:

- `area:modeling`, `area:aerodynamics`, `area:estimation-navigation`, `area:guidance-planning`, `area:control`, `area:fault-safety`, `area:experiment-data`, `area:tools`
- `task:system-identification`, `task:trajectory-tracking`, `task:path-planning`, `task:state-estimation`, `task:fault-detection`, `task:fault-tolerant-control`, `task:control-allocation`, `task:noise-prediction`, `task:vibration-suppression`
- `platform:helicopter`, `platform:multirotor`, `platform:fixed-wing`, `platform:tiltrotor`, `platform:eVTOL`, `platform:flapping-wing`, `platform:hypersonic`, `platform:spacecraft`, `platform:missile`, `platform:UAV`
- `method:MPC`, `method:RL`, `method:CFD`, `method:Kalman-filter`, `method:adaptive-control`, `method:sliding-mode`, `method:robust-control`, `method:observer`, `method:optimization`, `method:system-identification`
- `type:review`, `type:article`, `type:conference`, `type:book`, `type:standard`, `type:report`, `type:dataset`, `type:software`

## Extra Tags

Add these only when the paper provides enough information:

- `domain:*` - discipline or theoretical domain.
- `component:*` - physical component or subsystem.
- `phenomenon:*` - physical effect or observed phenomenon.
- `environment:*` - operating environment or scenario.
- `sensor:*` - sensor or data source.
- `evidence:*` - validation or evidence type.
- `status:*` - reading or usage status.
- `role:*` - the paper's role in the user's library.
- `project:*` - project identifier, if the user wants project linkage in tags as well as Collections.

Common examples:

- `domain:acoustics`, `domain:aeroacoustics`, `domain:flight-mechanics`, `domain:fluid-mechanics`, `domain:solid-mechanics`, `domain:structural-dynamics`, `domain:aeroelasticity`, `domain:vibration`, `domain:signal-processing`, `domain:optimization`, `domain:control-theory`, `domain:machine-learning`
- `component:rotor`, `component:blade`, `component:wing`, `component:propeller`, `component:fuselage`, `component:landing-gear`, `component:actuator`, `component:motor`, `component:battery`, `component:IMU`
- `phenomenon:rotor-wake`, `phenomenon:downwash`, `phenomenon:blade-vortex-interaction`, `phenomenon:ground-effect`, `phenomenon:stall`, `phenomenon:flutter`, `phenomenon:noise`, `phenomenon:vibration`, `phenomenon:turbulence`
- `environment:wind`, `environment:gps-denied`, `environment:urban`, `environment:indoor`, `environment:gust`, `environment:ground-effect`, `environment:formation-flight`
- `sensor:IMU`, `sensor:GNSS`, `sensor:camera`, `sensor:lidar`, `sensor:radar`, `sensor:microphone`, `sensor:pressure`, `sensor:strain-gauge`
- `evidence:theory`, `evidence:simulation`, `evidence:experiment`, `evidence:flight-test`, `evidence:wind-tunnel`, `evidence:benchmark`
- `status:unread`, `status:reading`, `status:read`, `status:skimmed`, `status:important`, `status:to-cite`
- `role:key-paper`, `role:baseline`, `role:method-source`, `role:background`, `role:comparison`, `role:dataset`, `role:writing-citation`

## Naming Rules

- Use lowercase English tag values by default.
- Use hyphens for multiword values, for example `task:trajectory-tracking`.
- Keep prefixes singular: `area:`, not `areas:`.
- Reuse existing user vocabulary when it is clean and consistent.
- Normalize near-duplicates, for example `method:mpc`, `method:model-predictive-control`, and `method:MPC` should become one chosen form.
- Do not create a new tag for every minor phrase in the abstract.

## Classification Priorities

When several dimensions compete:

1. Use `area:*` and `task:*` for the main research problem.
2. Use `platform:*` for the studied aircraft or system.
3. Use `method:*` for the method used to solve or analyze the task.
4. Use `domain:*`, `component:*`, and `phenomenon:*` to capture important cross-cutting scientific context.
5. Use `type:*`, `evidence:*`, `status:*`, and `role:*` for bibliographic, validation, and workflow context.

Examples:

- A paper on quadrotor adaptive MPC for trajectory tracking:
  - Tags: `area:control`, `task:trajectory-tracking`, `platform:multirotor`, `method:MPC`, `method:adaptive-control`, `domain:control-theory`, `type:article`, `evidence:simulation`
- A review of helicopter rotor aeroacoustic noise:
  - Tags: `area:aerodynamics`, `task:noise-prediction`, `platform:helicopter`, `component:rotor`, `domain:aeroacoustics`, `phenomenon:rotor-noise`, `type:review`
- A dataset paper for UAV visual-inertial navigation:
  - Tags: `area:experiment-data`, `area:estimation-navigation`, `task:state-estimation`, `platform:UAV`, `sensor:camera`, `sensor:IMU`, `type:dataset`, `evidence:benchmark`, `role:dataset`

## Output Format

For library-level work:

```text
Recommended Tag Taxonomy:
- Required basic tags:
- Extra tags:

Collection Policy:
- Project/workspace Collections to keep:
- Topic Collections to migrate into Tags:

Migration Suggestions:
- Merge:
- Rename:
- Convert Collection to Tag:
- Needs manual review:
```

For single-paper classification:

```text
Title:

Project Collection:
- None / existing project collection / suggested project collection

Required Basic Tags:
- area:
- task:
- platform:
- method:
- type:

Extra Tags:
- domain:
- component:
- phenomenon:
- environment:
- sensor:
- evidence:
- status:
- role:

Reason:

Confidence:
High / Medium / Low
```

If a tag type is not supported by the available metadata, omit it or write `unknown` only when the user needs a completeness audit.
