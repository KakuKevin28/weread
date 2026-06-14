# WeRead Web - 上传项目到腾讯云服务器
# 在本地 Windows 上运行此脚本
#
# 用法：
#   .\deploy\upload-to-server.ps1 -ServerIP "140.143.249.151" -User "root"
#
# 前提：本地已安装 ssh / scp（Windows 10 自带）

param(
    [string]$ServerIP = "140.143.249.151",
    [string]$User = "root",
    [string]$RemotePath = "/www/wwwroot/weread_web"
)

$LocalPath = Split-Path -Parent $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WeRead Web 上传到腾讯云服务器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "本地路径 : $LocalPath"
Write-Host "目标服务器: $User@$ServerIP"
Write-Host "远程路径 : $RemotePath"
Write-Host ""

# 先在服务器创建目标目录
Write-Host "[1/3] 在服务器创建目录..." -ForegroundColor Yellow
ssh "$User@$ServerIP" "mkdir -p $RemotePath"

# 上传项目文件（排除不必要的文件）
Write-Host "[2/3] 上传项目文件（排除 .venv、__pycache__、*.log）..." -ForegroundColor Yellow
scp -r `
    "$LocalPath/app.py" `
    "$LocalPath/requirements.txt" `
    "$LocalPath/static" `
    "$LocalPath/templates" `
    "$LocalPath/deploy" `
    "$User@$ServerIP`:$RemotePath/"

# 提示下一步
Write-Host ""
Write-Host "[3/3] 上传完成！" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  下一步：SSH 进服务器执行安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ssh $User@$ServerIP" -ForegroundColor White
Write-Host "  bash $RemotePath/deploy/server-setup.sh" -ForegroundColor White
Write-Host ""
Write-Host "记得在服务器上创建 .env 文件，参考：" -ForegroundColor Yellow
Write-Host "  $RemotePath/deploy/baota-panel.md" -ForegroundColor White
