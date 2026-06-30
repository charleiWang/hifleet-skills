# Skill context

## Positioning

- **Route A**: User’s **mailbox** open tonnage / cargo → local SQLite + optional memory search.  
- **Route C**: **Pre-arrival** vessels at a port (HiFleet API).  
- **Liner schedules** (bulk, Ro-Ro, container): skill **`hifleet-schedule`** (separate install).

## Requirements

| Capability | Needs |
|------------|--------|
| A (mailbox) | Email IMAP + optional memory-lancedb-pro |
| A enrich / C | `hifleet_api_key` |

## One-liner

**A = my mail tonnage/cargo; C = pre-arrival at port; schedules = hifleet-schedule.**
