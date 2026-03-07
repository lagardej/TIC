# TIC — Feature List

Features describe what TIC does for the player.
Implementation order and infrastructure are covered in ROADMAP.md.

---

## F0 — Campaign Metadata

Displays the current campaign context: game date, player faction, difficulty,
scenario, selected factions, and key game settings (research speed, alien
progression speed, CP maintenance bonuses).

Sources: `TIMetadataState`, `TITimeState`, `TIGlobalValuesState`,
`TIGlobalResearchState`.

---

## F1 — Nation Control Overview

All nations in a single view. For each nation: name, total CP count, which
faction owns each CP slot, CP type (Executive, Aristocracy, etc.), and which
slots are unowned. Replaces clicking into each nation individually in the
game UI.

Sources: `TINationState`, `TIControlPoint`, `TIFactionState`.

---

## F2 — Faction CP Summary

Per faction: total CPs held, broken down by nation. Shows which factions
are land-rich or geographically concentrated versus thinly spread.

Sources: `TIFactionState`, `TIControlPoint`, `TINationState`.

---

## F3 — Executive Control Status

Nations flagged by executive CP situation:
- Executive held but no other CPs in that nation (can be challenged immediately)
- Faction one CP away from executive eligibility
- Executive unowned

Sources: `TIControlPoint` (`controlPointType`, `positionInNation`).

---

## F4 — Unrest & Cohesion Watch

Nations ranked by unrest and cohesion, with owning faction shown. High
unrest signals coup vulnerability. Useful both as offensive target
identification and defensive early warning.

Sources: `TINationState` (`unrest`, `cohesion`).

---

## F5 — Boost Producer Ranking

Nations ranked by boost output, cross-referenced with the controlling
faction. Key for identifying sabotage targets or defending your own
launch capacity.

Sources: `TINationState` (`historyBoost`), `TILaunchFacilityState`.

---

## F6 — Contested & Uncontested Nations

Two views:
- **Contested:** nations where multiple factions hold CPs, sorted by
  number of competing factions. Active battlegrounds.
- **Uncontested:** nations where no faction holds any CP. Expansion
  opportunities with no immediate opposition.

Sources: `TIControlPoint`.

---

## F7 — Faction Resource Snapshot

Current resource levels per faction: Money, Influence, Operations, Boost,
Research, and space resources. Indicates who can afford to act aggressively.

Sources: `TIFactionState` (`resources`, `baseIncomes_year`).

---

## F8 — Historical Trends

Charts tracking key values across imported saves, per nation or per faction:
GDP, unrest, cohesion, boost output, CP count.

Sources: event store (cross-save history), `TINationState` history arrays.

---

## F9 — Save Import & Auto-watch

- Manual import of any `.json` or `.gz` save file.
- Automatic ingestion via file watcher on the autosave directory
  (`Autosave.gz`, `Autosave2.gz`).
