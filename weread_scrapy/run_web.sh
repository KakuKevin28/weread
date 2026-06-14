#!/bin/bash
# 微信读书 Web 仪表盘启动脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../weread_web"

# 如果使用虚拟环境，取消下一行注释
# source ../weread_scrapy/.venv/bin/activate

# 检查依赖
python3 -c "import flask" 2>/dev/null || {
    echo "请先安装依赖: python3 -m pip install -r requirements.txt"
    exit 1
}

# 用 gunicorn 生产模式启动（推荐）
# gunicorn -w 2 -b 0.0.0.0:5050 app:app --daemon --access-logfile gunicorn_access.log --error-logfile gunicorn_error.log

# 或用 Flask 开发模式启动
nohup python3 app.py > flask_out.log 2>&1 &

echo "Web 服务已启动，访问 http://$(hostname -I | awk '{{print $1}}'):5050"
