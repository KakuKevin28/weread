# WeRead 项目记忆

## 项目结构

- `C:\Users\guoxi\Desktop\weread\weread_scrapy` — Scrapy 爬虫，抓取微信读书数据存入 MySQL
- `C:\Users\guoxi\Desktop\weread\weread_web` — Flask 后端 + 静态前端数据看板（端口 5050）
- `C:\Users\guoxi\Desktop\weread\weread_schema.sql` — 数据库建表 SQL

## 服务器信息

- 腾讯云 CVM：140.143.249.151
- 面板：宝塔 Linux 面板
- 服务器路径：`/www/wwwroot/weread_web`，`/www/wwwroot/weread_scrapy`

## 架构

公网 80/443 → Nginx 反向代理 → gunicorn:5050 → Flask app.py → MySQL(weread_api)

## 部署脚本（2026-06-13 新增）

- `weread_web/deploy/upload-to-server.ps1` — 本地 Windows 上传脚本（SCP）
- `weread_web/deploy/server-setup.sh` — 服务器端一键安装脚本（venv + pip + 验证）
- `weread_web/deploy/baota-panel.md` — 完整宝塔部署文档

## 数据库默认配置

```
host: localhost / 127.0.0.1
port: 3306
user: weread
database: weread_api
```

## 注意事项

- 5050 端口不对外开放，只允许 nginx 本机访问
- .env 权限设 600
- 爬虫跑完后调 `/api/cache/clear` 清缓存
