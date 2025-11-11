# GitHub Actions Scripts

This directory contains automation scripts used by GitHub Actions workflows.

## sync_bootdev.py

**Purpose:** Automatically syncs Boot.dev learning progress to the repository.

**What it does:**
1. Fetches course completion data from [Boot.dev Public API](https://api.boot.dev/v1)
2. Updates [docs/progress/bootdev-progress.md](../../docs/progress/bootdev-progress.md) with latest progress
3. Updates [.github/bootdev-stats.json](../bootdev-stats.json) for badge generation
4. Updates Boot.dev badges in [README.md](../../README.md)

**Triggered by:**
- Daily at midnight UTC (cron schedule)
- Manual trigger via GitHub Actions tab
- Push to workflow files

**Files Modified:**
- `docs/progress/bootdev-progress.md` - Detailed course checklist
- `.github/bootdev-stats.json` - JSON stats for badges
- `README.md` - Badge URLs

**Environment Variables:**
- `BOOTDEV_USERNAME` - Boot.dev username (default: `aott33`)

**Dependencies:**
- Python 3.11+
- `requests` library

## Usage

### Manual Run (Local)

```bash
# Install dependencies
pip install requests

# Run sync script
python .github/scripts/sync_bootdev.py
```

### Manual Trigger (GitHub Actions)

1. Navigate to **Actions** tab
2. Select **Sync Boot.dev Progress** workflow
3. Click **Run workflow**

## Notes

- The script uses Boot.dev's public API (no authentication required)
- Progress is tracked against the "Python & Go Backend Track" curriculum
- Course names are normalized to handle API variations
