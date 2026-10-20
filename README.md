# Tiny Spark – live files

Public files the Tiny Spark app downloads. **Never put secrets here** – everything in this repo is public.

| File | What it is |
|---|---|
| `announcements.json` | Messages shown in the game's **Inbox → Announcements** tab |
| `img/` | Banner images for announcements (PNG/JPG, max 300 KB, about 1000×300 px looks best) |
| `tools/check_announcements.py` | Checks the file (run automatically on every push) |
| `.github/workflows/check.yml` | Runs the check, then publishes to GitHub Pages only if it passes |

## One-time setup

1. Copy these files into the repo and push to `main`.
2. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Wait for the "Check and publish" action to finish (Actions tab), then open `https://<user>.github.io/<repo>/announcements.json` in a browser.
4. Give that base URL (`https://<user>.github.io/<repo>/`) to the game: `data/inbox.json` → `"feed_base_url"`.
5. Recommended: two-step verification on your GitHub account, and branch protection on `main` (require the "check" job).

## Add an announcement

Add an entry to the `announcements` list, commit, push. Players see it the next time they open the game (Pages updates in about 1–10 minutes; the game re-checks at most every 6 hours, or when the player taps Refresh).

```json
{
  "id": "2026-11-world16",
  "kind": "new_levels",
  "title": "World 16 is here!",
  "body": "40 brand-new levels. Update and give them a try.",
  "date": "2026-11-01",
  "image": "img/world16.png",
  "button": {"label": "Play now", "route": "continue"},
  "start": "2026-11-01",
  "end": "2026-12-01",
  "min_version": 10200
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique, never reuse one. A new id makes the card "NEW" again. |
| `kind` | yes | `new_app`, `critical`, `new_levels`, `event`, `info` |
| `title` / `body` | yes | Plain text. Title ≤ 60, body ≤ 600 characters. |
| `date` | no | Shown on the card; newest first. |
| `image` | no | `img/name.png` in this repo, or an https URL. |
| `button` | no | `{"label", "url"}` (https or `market://details?id=…`), or `{"label", "route"}` (`continue`, `daily`, `shop`, `achievements`, `wallet`, `home`, `level:<id>`), or `{"label", "action": "update"}` |
| `start` / `end` | no | Only shown between these dates (player's local date). |
| `min_version` / `max_version` | no | App version codes (1.2.0 = 10200). |
| `pinned` | no | Always on top. |
| `important` | no | Stays "NEW" until the player opens it. Use for critical updates. |

Check locally before pushing: `python3 tools/check_announcements.py announcements.json`

## Remove an announcement

Delete its entry (or set an `end` date) and push.
