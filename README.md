# clash-rules

Self-hosted **Clash / Mihomo rule-providers** mirror for Ryukyou.

Upstream rule links often break, rate-limit, or stop updating.  
This repo downloads them into `rules/` on a schedule so your client only depends on **your** GitHub raw URLs.

## How it works

1. Edit `sources.txt` — each line: `filename|upstream_url|behavior`
2. GitHub Actions runs `scripts/sync_rules.py` daily (or manually)
3. Files land in `rules/` and are committed
4. Point your YAML `rule-providers` at this repo

## Client URL (use these)

```text
https://raw.githubusercontent.com/RyuKyou/clash-rules/main/rules/<filename>
```

CN-friendly mirror:

```text
https://cdn.jsdelivr.net/gh/RyuKyou/clash-rules@main/rules/<filename>
```

Example `rule-providers` entry:

```yaml
  Steam:
    type: http
    behavior: classical
    path: ./RuleSet/Steam.yaml
    url: https://raw.githubusercontent.com/RyuKyou/clash-rules/main/rules/Steam.yaml
    interval: 86400
```

## Add a new rule set you found online

1. Open `sources.txt`
2. Append:
   ```text
   MyRule.yaml|https://example.com/path/to/rule.yaml|classical
   ```
3. Commit / push, or run Actions → **Sync rule providers** → Run workflow
4. After sync succeeds, use:
   `https://raw.githubusercontent.com/RyuKyou/clash-rules/main/rules/MyRule.yaml`

## Manual update when upstream is dead

1. Put a file under `rules/YourName.yaml` (same format as Clash rule list)
2. Commit
3. Comment out the upstream line in `sources.txt` so a failed sync will not try to replace your file (script keeps old file on failure anyway)

## Status

- `INDEX.txt` — human-readable sync status
- `sync_meta.txt` — sizes / short hashes

## License / disclaimer

Mirrored content belongs to original authors (blackmatrix7, Loyalsoldier, MetaCubeX, etc.).  
For personal backup and reliability only.
