import os
from pathlib import Path


def load_dotenv(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

BOT_NAME = "weread_crawler"

SPIDER_MODULES = ["weread_crawler.spiders"]
NEWSPIDER_MODULE = "weread_crawler.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = int(os.getenv("WEREAD_CONCURRENT_REQUESTS", "4"))
DOWNLOAD_DELAY = float(os.getenv("WEREAD_DOWNLOAD_DELAY", "0.25"))
RETRY_ENABLED = True
RETRY_TIMES = int(os.getenv("WEREAD_RETRY_TIMES", "3"))
RETRY_HTTP_CODES = [408, 425, 429, 500, 502, 503, 504]

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

ITEM_PIPELINES = {
    "weread_crawler.pipelines.WereadMysqlPipeline": 300,
}

WEREAD_API_GATEWAY = os.getenv(
    "WEREAD_API_GATEWAY",
    "https://i.weread.qq.com/api/agent/gateway",
)
WEREAD_API_KEY = os.getenv("WEREAD_API_KEY", "")
WEREAD_SKILL_VERSION = os.getenv("WEREAD_SKILL_VERSION", "1.0.3")

WEREAD_MYSQL = {
    "host": os.getenv("WEREAD_MYSQL_HOST", "localhost"),
    "port": int(os.getenv("WEREAD_MYSQL_PORT", "3306")),
    "user": os.getenv("WEREAD_MYSQL_USER", "root"),
    "password": os.getenv("WEREAD_MYSQL_PASSWORD", "111111"),
    "database": os.getenv("WEREAD_MYSQL_DATABASE", "weread_api"),
    "charset": "utf8mb4",
    "autocommit": False,
}

LOG_LEVEL = os.getenv("WEREAD_LOG_LEVEL", "INFO")

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
