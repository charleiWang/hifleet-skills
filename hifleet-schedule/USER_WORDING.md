# User-facing language (mandatory)

## Default

- **Prefer English** for explanations, errors, and setup hints when locale is unknown.  
- **Translate** system/status text to the user’s agent UI language when locale is known (`LOCALIZATION.md`).  
- **Never translate** business data: vessel names, port names, cargo names, line names, API field values, IMO, dates in data rows.

## Forbidden → use instead

| Avoid | Use |
|-------|-----|
| workflow, schema, POST /schedules | **schedule query**, **HiFleet** |
| offset/limit, typeCode | **pagination**, **unlock contact details** |
| route B | **liner schedule** |

## Locked contacts

- ✅ “Contact details are masked; confirm to unlock with points.”  
- ❌ “Call POST /unlock with typeCode=…”
