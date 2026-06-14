# WeRead Scrapy Crawler

Scrapy crawler for the WeRead Agent API Gateway. It stores both normalized data and raw API responses into the local MySQL database `weread_api`.

## Configuration

Paste your API key into this config file:

```text
C:\Users\guoxi\Desktop\weread\weread_scrapy\.env
```

Replace the placeholder line:

```text
WEREAD_API_KEY=wrk-请替换成你的apikey
```

You can also set the API key in PowerShell before running:

```powershell
$env:WEREAD_API_KEY="wrk-xxxxxxxxxxxxxxxx"
```

Default MySQL connection:

```text
host: localhost
port: 3306
user: root
password: 111111
database: weread_api
```

You can override these with:

```powershell
$env:WEREAD_MYSQL_HOST="localhost"
$env:WEREAD_MYSQL_PORT="3306"
$env:WEREAD_MYSQL_USER="root"
$env:WEREAD_MYSQL_PASSWORD="111111"
$env:WEREAD_MYSQL_DATABASE="weread_api"
```

## Run

From this directory:

```powershell
python -m scrapy crawl weread_api
```

The default run is optimized for daily personal data sync. It fetches shelf, book info, reading progress, personal bookmarks, personal notes, notebook overview, and monthly plus annual reading stats. It does not fetch recommendations, public reviews, chapter underline heat, or hot underline discussions unless you explicitly enable them.

With seed books and search keywords:

```powershell
python -m scrapy crawl weread_api -a book_ids="3300144307,3300207566" -a keywords="三体,人工智能" -a modes="weekly,monthly,annually,overall"
```

Or use the helper script:

```powershell
.\run_weread_crawler.ps1 -ApiKey "wrk-xxxxxxxxxxxxxxxx" -BookIds "3300144307" -Keywords "三体"
```

## Important arguments

- `book_ids`: comma-separated seed book IDs.
- `keywords`: comma-separated search keywords.
- `modes`: comma-separated reading-stat modes: `weekly`, `monthly`, `annually`, `overall`. Default: `monthly,annually`.
- `crawl_shelf`: `1` by default. Fetches `/shelf/sync` and expands books from your shelf.
- `crawl_recommend`: `0` by default. Set to `1` to fetch `/book/recommend` and `/book/similar`.
- `deep`: `1` by default. Fetches per-book detail endpoints.
- `max_pages`: pagination limit for list APIs. Default `1`.
- `crawl_chapters`: `0` by default. Set to `1` to fetch `/book/chapterinfo`.
- `crawl_chapter_underlines`: `0` by default. Set to `1` to fetch `/book/underlines`.
- `crawl_hot_bookmarks`: `0` by default. Set to `1` to fetch `/book/bestbookmarks`.
- `crawl_public_reviews`: `0` by default. Set to `1` to fetch `/review/list`.
- `crawl_review_details`: `0` by default. Set to `1` to fetch `/review/single` from note/review lists.
- `chapter_limit`: maximum chapters per book for `/book/underlines`; default `0`.
- `review_range_limit`: maximum hot underline ranges per book for `/book/readreviews`; default `0`.

Daily lightweight run:

```powershell
python -m scrapy crawl weread_api
```

Weekly medium run:

```powershell
python -m scrapy crawl weread_api -a crawl_chapters=1 -a max_pages=2
```

Manual deep run:

```powershell
python -m scrapy crawl weread_api -a crawl_chapters=1 -a crawl_hot_bookmarks=1 -a crawl_public_reviews=1 -a crawl_review_details=1 -a max_pages=2
```

Every response is stored in `api_responses`. Normalized processors also fill tables such as `books`, `chapters`, `shelf_books`, `user_bookmarks`, `reviews`, and `reading_stats`.

## Tencent Cloud / Baota Linux

See:

```text
deploy/baota-linux.md
```
