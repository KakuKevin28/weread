param(
  [string]$ApiKey = $env:WEREAD_API_KEY,
  [string]$BookIds = "",
  [string]$Keywords = "",
  [string]$Modes = "monthly,annually",
  [int]$MaxPages = 1,
  [int]$ChapterLimit = 0,
  [int]$ReviewRangeLimit = 0
)

if (-not $ApiKey) {
  Write-Error "Please set WEREAD_API_KEY or pass -ApiKey wrk-xxxxxxxx."
  exit 1
}

$env:WEREAD_API_KEY = $ApiKey
$env:WEREAD_MYSQL_HOST = "localhost"
$env:WEREAD_MYSQL_PORT = "3306"
$env:WEREAD_MYSQL_USER = "root"
$env:WEREAD_MYSQL_PASSWORD = "111111"
$env:WEREAD_MYSQL_DATABASE = "weread_api"

python -m scrapy crawl weread_api `
  -a book_ids="$BookIds" `
  -a keywords="$Keywords" `
  -a modes="$Modes" `
  -a max_pages="$MaxPages" `
  -a chapter_limit="$ChapterLimit" `
  -a review_range_limit="$ReviewRangeLimit" `
  -a crawl_recommend=0
