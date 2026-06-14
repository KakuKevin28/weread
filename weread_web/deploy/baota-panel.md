# 宝塔面板部署 WeRead Web

适用于：腾讯云 CVM + 宝塔 Linux 面板。  
你的爬虫和数据库已经部署好时，网站项目只需要连接同一个 MySQL 数据库即可。

推荐架构：

```text
公网 80/443 -> 宝塔 nginx 网站 -> 反向代理 127.0.0.1:5050 -> gunicorn -> Flask app -> MySQL
```

不要把 `5050` 暴露到公网，公网只开放 `80` 和 `443`。

## 1. 宝塔安装软件

宝塔软件商店安装：

- Nginx
- Python 项目管理器
- MySQL，如果数据库也在这台服务器

腾讯云安全组放行：

- TCP `80`
- TCP `443`，如果要开 HTTPS

如果数据库在腾讯云 CDB，确认 CDB 白名单或安全组允许当前 CVM 内网 IP 访问。

## 2. 上传网站项目

建议上传到：

```text
/www/wwwroot/weread_web
```

可以用宝塔「文件」上传，也可以用本地命令：

```bash
scp -r weread_web root@你的服务器IP:/www/wwwroot/weread_web
```

如果你已经把爬虫放在：

```text
/www/wwwroot/weread_scrapy
```

也可以把网站和爬虫放成并列目录：

```text
/www/wwwroot/weread_scrapy
/www/wwwroot/weread_web
```

## 3. 配置网站 .env

在服务器创建：

```text
/www/wwwroot/weread_web/.env
```

内容示例：

```text
WEREAD_MYSQL_HOST=127.0.0.1
WEREAD_MYSQL_PORT=3306
WEREAD_MYSQL_USER=你的数据库用户
WEREAD_MYSQL_PASSWORD=你的数据库密码
WEREAD_MYSQL_DATABASE=weread_api
WEREAD_WEB_HOST=127.0.0.1
WEREAD_WEB_PORT=5050
WEREAD_CACHE_TTL_SECONDS=600
```

如果数据库是腾讯云 CDB：

```text
WEREAD_MYSQL_HOST=你的CDB内网地址
```

建议限制权限：

```bash
chmod 600 /www/wwwroot/weread_web/.env
```

## 4. 安装 Python 依赖

在宝塔终端执行：

```bash
cd /www/wwwroot/weread_web
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

验证 Flask 能连数据库：

```bash
source /www/wwwroot/weread_web/.venv/bin/activate
cd /www/wwwroot/weread_web
gunicorn --workers 2 --threads 4 --bind 127.0.0.1:5050 app:app
```

另开一个终端测试：

```bash
curl http://127.0.0.1:5050/
curl http://127.0.0.1:5050/api/summary
```

测试成功后，回到运行 gunicorn 的终端按 `Ctrl+C` 停止。

## 5. 用宝塔 Python 项目管理器启动

宝塔路径：

```text
软件商店 -> Python 项目管理器 -> 添加项目
```

推荐填写：

```text
项目名称：weread-web
项目路径：/www/wwwroot/weread_web
Python 版本：选择 3.10+，或选择项目里的 .venv
启动方式：命令启动
启动命令：/www/wwwroot/weread_web/.venv/bin/gunicorn --workers 2 --threads 4 --timeout 60 --bind 127.0.0.1:5050 app:app
端口：5050
```

如果面板要求填写启动文件，可以填：

```text
app.py
```

但生产环境仍推荐用上面的 gunicorn 启动命令。

启动后看项目日志，确认没有报错。

## 6. 宝塔添加网站和反向代理

宝塔路径：

```text
网站 -> 添加站点
```

填写你的域名，或者先用服务器 IP 测试。根目录可以随便指向一个空目录，例如：

```text
/www/wwwroot/weread_site
```

然后进入这个站点：

```text
设置 -> 反向代理 -> 添加反向代理
```

填写：

```text
代理名称：weread-web
目标 URL：http://127.0.0.1:5050
发送域名：$host
```

保存后访问：

```text
http://你的域名/
```

或：

```text
http://服务器IP/
```

## 7. 可选：静态文件缓存

宝塔反向代理已经可以直接访问静态资源。  
如果你想让 nginx 直接托管静态文件，可以在站点 nginx 配置中加入：

```nginx
location /static/ {
    alias /www/wwwroot/weread_web/static/;
    access_log off;
    expires 7d;
    add_header Cache-Control "public";
}
```

再测试并重载 nginx：

```bash
nginx -t
/etc/init.d/nginx reload
```

## 8. 配置 HTTPS

宝塔路径：

```text
网站 -> 你的站点 -> SSL
```

可以用：

- 宝塔 Let's Encrypt
- 腾讯云 SSL 证书

申请成功后开启强制 HTTPS。

## 9. 爬虫同步后清缓存

网站接口有 600 秒缓存。爬虫跑完后可以清一次：

```bash
curl -X POST http://127.0.0.1:5050/api/cache/clear
```

可以把这句放到爬虫计划任务最后。

全年热力图依赖 `reading_stats` / `reading_stat_daily_times` 里的年度或全量阅读统计。宝塔计划任务里不要只跑 `modes=monthly`，否则新数据库可能只显示最近两周或当前月数据。

推荐爬虫计划任务至少包含：

```bash
cd /www/wwwroot/weread_scrapy
source .venv/bin/activate
./run_weread_crawler.sh -a modes=monthly,annually,overall
curl -X POST http://127.0.0.1:5050/api/cache/clear
```

如果你想先只同步统计数据做验证，可以用：

```bash
cd /www/wwwroot/weread_scrapy
source .venv/bin/activate
python -m scrapy crawl weread_api -a crawl_shelf=0 -a deep=0 -a modes=monthly,annually,overall
curl -X POST http://127.0.0.1:5050/api/cache/clear
```

检查数据库里是否已有年度/全量日数据：

```bash
mysql -u 你的数据库用户 -p -e "
SELECT rs.mode,
       COUNT(*) AS rows_count,
       MIN(DATE(FROM_UNIXTIME(dt.day_timestamp))) AS first_day,
       MAX(DATE(FROM_UNIXTIME(dt.day_timestamp))) AS last_day
FROM weread_api.reading_stat_daily_times dt
JOIN weread_api.reading_stats rs ON rs.id = dt.reading_stat_id
GROUP BY rs.mode
ORDER BY rs.mode;
"
```

## 10. 常见问题

### 访问网站 502

通常是 Python 项目没启动或端口不对：

```bash
curl http://127.0.0.1:5050/
```

如果不通，回宝塔 Python 项目管理器看日志。

### `/api/summary` 报错

多半是数据库连接问题。检查：

```text
/www/wwwroot/weread_web/.env
```

确认数据库地址、用户、密码、库名正确。

### 腾讯云 CDB 连不上

检查：

- 使用 CDB 内网地址
- CDB 和 CVM 在同一个 VPC 或网络可达
- CDB 安全组/白名单允许 CVM 内网 IP
- 不建议用公网地址连数据库

### 静态资源不更新

本项目前端资源带版本号，例如：

```text
styles.css?v=10
app.js?v=9
```

部署新版本后，如果浏览器仍旧显示旧样式，清理浏览器缓存或确认服务器文件已覆盖。

### 不要开放 5050

宝塔安全、腾讯云安全组里不要开放 `5050`。  
`5050` 只给本机 nginx 访问即可。
