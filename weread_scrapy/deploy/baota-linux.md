# 宝塔 Linux 部署说明

本文档适用于腾讯云 CVM + 宝塔面板 Linux 版本。

## 1. 宝塔面板准备

在宝塔软件商店安装：

- Python 项目管理器，或系统 Python 3.10+
- MySQL 8.0 或 MariaDB 10.6+
- Supervisor 管理器，可选，用于常驻或手动任务管理

如果你只想定时同步数据，推荐用宝塔「计划任务」，不需要让 Scrapy 常驻运行。

## 2. 上传项目

建议上传到：

```bash
/www/wwwroot/weread_scrapy
```

你可以在宝塔「文件」里上传整个 `weread_scrapy` 文件夹，也可以用 `scp`：

```bash
scp -r weread_scrapy root@你的服务器IP:/www/wwwroot/weread_scrapy
```

上传后进入服务器：

```bash
cd /www/wwwroot/weread_scrapy
```

## 3. 创建虚拟环境并安装依赖

```bash
cd /www/wwwroot/weread_scrapy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

验证 Scrapy 能识别爬虫：

```bash
python -m scrapy list
```

应该看到：

```text
weread_api
```

## 4. 创建 MySQL 数据库和用户

如果你已经在本地创建过库，服务器上也需要创建一次。

宝塔面板路径：

```text
数据库 -> 添加数据库
```

建议：

```text
数据库名：weread_api
用户名：weread
密码：设置一个强密码
访问权限：本地服务器
编码：utf8mb4
```

然后导入建表 SQL：

```bash
mysql -u weread -p weread_api < /www/wwwroot/weread_scrapy/weread_schema.sql
```

如果项目目录里还没有 `weread_schema.sql`，从本机这个文件上传到服务器项目根目录：

```text
C:\Users\guoxi\Documents\Codex\2026-06-09\files-mentioned-by-the-user-api\outputs\weread_schema.sql
```

## 5. 配置 .env

在服务器项目根目录创建 `.env`：

```bash
cd /www/wwwroot/weread_scrapy
cp .env.linux.example .env
vim .env
```

填写：

```text
WEREAD_API_KEY=wrk-你的真实apikey
WEREAD_MYSQL_HOST=localhost
WEREAD_MYSQL_PORT=3306
WEREAD_MYSQL_USER=weread
WEREAD_MYSQL_PASSWORD=你的数据库密码
WEREAD_MYSQL_DATABASE=weread_api
```

保存后建议限制权限：

```bash
chmod 600 .env
chmod +x run_weread_crawler.sh
```

## 6. 先做小范围验证

```bash
cd /www/wwwroot/weread_scrapy
source .venv/bin/activate
./run_weread_crawler.sh -a crawl_shelf=0 -a crawl_recommend=0 -a deep=0 -a modes=monthly
```

成功时你会看到：

- HTTP 200
- `item_scraped_count: 1`
- MySQL 中 `api_responses`、`reading_stats` 有新增记录

查询：

```bash
mysql -u weread -p -e "SELECT api_name, COUNT(*) FROM weread_api.api_responses GROUP BY api_name;"
```

## 7. 完整运行

首次完整抓取：

```bash
cd /www/wwwroot/weread_scrapy
source .venv/bin/activate
./run_weread_crawler.sh
```

如果书架很大，建议先限制范围：

```bash
./run_weread_crawler.sh
```

后续再逐步放大：

```bash
./run_weread_crawler.sh -a crawl_chapters=1 -a crawl_hot_bookmarks=1 -a crawl_public_reviews=1 -a max_pages=2
```

## 8. 宝塔计划任务

宝塔面板路径：

```text
计划任务 -> 添加任务
```

任务类型：

```text
Shell 脚本
```

每天凌晨 3 点运行示例。推荐使用项目里的每日脚本，它会写日志并用锁防止重复运行：

```bash
cd /www/wwwroot/weread_scrapy
chmod +x run_daily_default.sh
./run_daily_default.sh
```

小范围阅读统计每日同步：

```bash
cd /www/wwwroot/weread_scrapy
source .venv/bin/activate
./run_weread_crawler.sh -a crawl_shelf=0 -a deep=0 -a modes=monthly >> /www/wwwlogs/weread_scrapy_health.log 2>&1
```

## 9. 常见问题

### 找不到 scrapy

先确认虚拟环境已激活：

```bash
source /www/wwwroot/weread_scrapy/.venv/bin/activate
python -m scrapy list
```

### MySQL 连接失败

检查 `.env` 里的账号、密码、库名。若使用腾讯云 CDB，需要在安全组和 CDB 白名单里放行服务器内网 IP。

### API key 无效

运行小范围验证，看日志里的 `errcode` 和 `errmsg`。确认 `.env` 中没有多余空格或引号。

### 第一次完整运行很慢

这是正常的。完整模式会从书架扩展抓取书籍详情、章节、进度、划线、点评和统计。建议先降低：

```bash
-a crawl_chapters=0 -a crawl_hot_bookmarks=0 -a crawl_public_reviews=0 -a crawl_review_details=0
```
