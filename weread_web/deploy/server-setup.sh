#!/bin/bash
# WeRead Web - 服务器端一键安装脚本
# 适用于：腾讯云 CVM + 宝塔面板
#
# 使用方法（SSH 进服务器后执行）：
#   cd /www/wwwroot/weread_web
#   bash deploy/server-setup.sh
#
# 执行前请先创建 .env 文件（参考 deploy/baota-panel.md）

set -e

PROJECT_DIR="/www/wwwroot/weread_web"
VENV_DIR="$PROJECT_DIR/.venv"
PORT=5050

echo "========================================"
echo "  WeRead Web 服务器安装脚本"
echo "========================================"
echo ""

# ── 检查项目目录 ──────────────────────────────
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "[错误] 找不到 $PROJECT_DIR/app.py"
    echo "请先上传项目文件，或检查路径是否正确"
    exit 1
fi

cd "$PROJECT_DIR"
echo "[OK] 项目目录: $PROJECT_DIR"

# ── 检查 .env ────────────────────────────────
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "[警告] 未找到 .env 文件！"
    echo "请创建 $PROJECT_DIR/.env，内容示例："
    echo ""
    echo "  WEREAD_MYSQL_HOST=127.0.0.1"
    echo "  WEREAD_MYSQL_PORT=3306"
    echo "  WEREAD_MYSQL_USER=weread"
    echo "  WEREAD_MYSQL_PASSWORD=你的数据库密码"
    echo "  WEREAD_MYSQL_DATABASE=weread_api"
    echo "  WEREAD_WEB_HOST=127.0.0.1"
    echo "  WEREAD_WEB_PORT=5050"
    echo "  WEREAD_CACHE_TTL_SECONDS=600"
    echo ""
    read -p "是否继续安装（先不配 .env）？[y/N] " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "已取消。请先创建 .env 再运行此脚本。"
        exit 0
    fi
fi

# ── 创建虚拟环境 ──────────────────────────────
echo ""
echo "[1/4] 创建 Python 虚拟环境..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "[OK] 虚拟环境已创建: $VENV_DIR"
else
    echo "[OK] 虚拟环境已存在，跳过创建"
fi

# ── 安装依赖 ──────────────────────────────────
echo ""
echo "[2/4] 安装 Python 依赖..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
echo "[OK] 依赖安装完成"

# ── 设置文件权限 ──────────────────────────────
echo ""
echo "[3/4] 设置文件权限..."
if [ -f "$PROJECT_DIR/.env" ]; then
    chmod 600 "$PROJECT_DIR/.env"
    echo "[OK] .env 权限已设为 600"
fi
chmod +x "$PROJECT_DIR/deploy/server-setup.sh" 2>/dev/null || true

# ── 快速验证 ──────────────────────────────────
echo ""
echo "[4/4] 验证 Flask 能启动..."
source "$VENV_DIR/bin/activate"

# 后台启动 gunicorn 做快速测试
"$VENV_DIR/bin/gunicorn" \
    --workers 1 \
    --bind 127.0.0.1:$PORT \
    --timeout 10 \
    --daemon \
    --pid /tmp/weread_web_test.pid \
    app:app 2>/tmp/weread_web_test.log || {
    echo "[错误] gunicorn 启动失败，查看日志："
    cat /tmp/weread_web_test.log
    exit 1
}

sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/" 2>/dev/null || echo "000")

# 停掉测试进程
if [ -f /tmp/weread_web_test.pid ]; then
    kill "$(cat /tmp/weread_web_test.pid)" 2>/dev/null || true
    rm -f /tmp/weread_web_test.pid
fi

if [ "$HTTP_CODE" = "200" ]; then
    echo "[OK] Flask 启动验证成功 (HTTP 200)"
else
    echo "[警告] HTTP 状态码: $HTTP_CODE（可能是数据库未就绪，稍后再验证）"
fi

# ── 完成提示 ──────────────────────────────────
echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "接下来在宝塔面板配置："
echo ""
echo "【Python 项目管理器】添加项目："
echo "  项目路径: $PROJECT_DIR"
echo "  启动命令: $VENV_DIR/bin/gunicorn --workers 2 --threads 4 --timeout 60 --bind 127.0.0.1:$PORT app:app"
echo ""
echo "【网站】添加站点 -> 反向代理："
echo "  目标 URL: http://127.0.0.1:$PORT"
echo ""
echo "参考完整文档: $PROJECT_DIR/deploy/baota-panel.md"
echo ""
