# Tencent Cloud deployment for WeRead Web

This guide deploys the Flask web app on a Tencent Cloud CVM with:

- gunicorn running the Flask app on `127.0.0.1:5050`
- systemd keeping the app alive
- nginx exposing the site on port `80`
- MySQL already prepared by the crawler deployment

Assumptions:

- Linux server, Ubuntu/Debian examples below.
- Project path on server: `/opt/weread/weread_web`
- Database is reachable from the web server.
- Tencent Cloud security group allows inbound `80` and, if using HTTPS later, `443`.

## 1. Upload the web project

From your local machine, upload only the web folder:

```bash
ssh root@YOUR_SERVER_IP "mkdir -p /opt/weread"
scp -r weread_web root@YOUR_SERVER_IP:/opt/weread/
```

Or on the server, place this folder at:

```text
/opt/weread/weread_web
```

## 2. Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx
```

## 3. Create Python virtual environment

```bash
cd /opt/weread/weread_web
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

If your service runs as `www-data`, make sure the app can read the project and `.env`:

```bash
sudo chown -R www-data:www-data /opt/weread/weread_web
```

On TencentOS/CentOS, the nginx worker user may be `nginx` instead of `www-data`. If so, edit `deploy/weread-web.service` and replace:

```text
User=www-data
Group=www-data
```

with:

```text
User=nginx
Group=nginx
```

## 4. Configure environment variables

```bash
cd /opt/weread/weread_web
cp .env.production.example .env
nano .env
```

Set these values to your deployed database:

```text
WEREAD_MYSQL_HOST=your-mysql-private-ip-or-127.0.0.1
WEREAD_MYSQL_PORT=3306
WEREAD_MYSQL_USER=your-db-user
WEREAD_MYSQL_PASSWORD=your-db-password
WEREAD_MYSQL_DATABASE=weread_api
WEREAD_WEB_HOST=127.0.0.1
WEREAD_WEB_PORT=5050
WEREAD_CACHE_TTL_SECONDS=600
```

If the crawler and web are on the same CVM and share `/opt/weread/weread_scrapy/.env`, the web app can also read that file. A local `/opt/weread/weread_web/.env` is still recommended for production clarity.

## 5. Test gunicorn manually

```bash
cd /opt/weread/weread_web
. .venv/bin/activate
gunicorn --workers 2 --threads 4 --bind 127.0.0.1:5050 app:app
```

Open another SSH session and test:

```bash
curl http://127.0.0.1:5050/
curl http://127.0.0.1:5050/api/summary
```

Stop the manual gunicorn process with `Ctrl+C`.

## 6. Install systemd service

```bash
sudo cp /opt/weread/weread_web/deploy/weread-web.service /etc/systemd/system/weread-web.service
sudo systemctl daemon-reload
sudo systemctl enable --now weread-web
sudo systemctl status weread-web
```

Logs:

```bash
journalctl -u weread-web -f
```

## 7. Install nginx reverse proxy

Edit `deploy/nginx-weread.conf` and replace:

```text
server_name example.com;
```

with your domain, or use your server IP temporarily:

```text
server_name _;
```

Then enable it:

```bash
sudo cp /opt/weread/weread_web/deploy/nginx-weread.conf /etc/nginx/sites-available/weread
sudo ln -s /etc/nginx/sites-available/weread /etc/nginx/sites-enabled/weread
sudo nginx -t
sudo systemctl reload nginx
```

On TencentOS/CentOS, nginx usually uses `/etc/nginx/conf.d/` instead:

```bash
sudo cp /opt/weread/weread_web/deploy/nginx-weread.conf /etc/nginx/conf.d/weread.conf
sudo nginx -t
sudo systemctl reload nginx
```

Visit:

```text
http://YOUR_SERVER_IP/
```

or:

```text
http://YOUR_DOMAIN/
```

## 8. Tencent Cloud checklist

- CVM security group: inbound TCP `80` open.
- If using HTTPS: inbound TCP `443` open.
- MySQL access:
  - same server: `WEREAD_MYSQL_HOST=127.0.0.1`
  - TencentDB/CDB: use private network address and allow the CVM security group/IP.
- Do not expose MySQL port `3306` to the public internet unless absolutely necessary.
- Do not expose Flask/Gunicorn port `5050` publicly; nginx should be the only public entry.

## 9. Optional HTTPS

If you have a domain pointed to this CVM, use Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 10. After crawler sync

The web app caches read-heavy APIs. Clear cache after crawler finishes:

```bash
curl -X POST http://127.0.0.1:5050/api/cache/clear
```

You can add that command to the crawler deploy script after a successful crawl.
