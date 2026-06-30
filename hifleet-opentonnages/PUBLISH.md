# Publish

```bash
clawhub publish ./hifleet-opentonnages --name hifleet-opentonnages --version 1.0.0
```

**v1.0.0**: Public open vessel (`POST /vessels/search`) + public cargo (`POST /cargo/search`); **fully open** (no `/unlock`); optional **`enrich-row`** bundle; separate from **hifleet-mytonnages** and **hifleet-schedule**.
