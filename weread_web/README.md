# WeRead Web MVP

Lightweight personal web dashboard for the local WeRead MySQL database.

## Run locally

```powershell
cd C:\Users\guoxi\Desktop\weread\weread_web
python app.py
```

Open:

```text
http://127.0.0.1:5050
```

The app reads database settings from `.env` in this folder first, then falls back to `../weread_scrapy/.env`. You can copy `.env.example` to `.env` in this folder and edit it.

## Deploy

See [`deploy/tencent-cloud.md`](deploy/tencent-cloud.md) for Tencent Cloud CVM deployment with gunicorn, systemd, and nginx.

If you use 宝塔面板, see [`deploy/baota-panel.md`](deploy/baota-panel.md).

## MVP features

- Dashboard counts for books, reading progress, bookmarks, notes.
- Latest reading stats from `reading_stats`.
- Book detail drawer from currently-reading cards, with progress, personal bookmarks, and personal notes.
- Category distribution, with a compact dashboard pie chart and a full category page.
- Vue component-style frontend with tabbed subpages: dashboard, categories, notes.
- Fun dashboard blocks: reading heatmap and currently reading.
- Compact annual reading heatmap from `reading_stat_daily_times`, with month tabs and hover tooltip for daily duration.

## Cache

The MVP uses a small in-memory TTL cache for these read-heavy APIs:

- `/api/summary`
- `/api/categories`
- `/api/recent-notes`
- `/api/currently-reading`
- `/api/reading-heatmap`

Default TTL is 600 seconds. Override it in `.env`:

```text
WEREAD_CACHE_TTL_SECONDS=600
```

Clear cache manually after a crawler run:

```powershell
curl -X POST http://127.0.0.1:5050/api/cache/clear
```
