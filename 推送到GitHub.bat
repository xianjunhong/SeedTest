@echo off
chcp 65001 >nul
echo ========================================
echo   SeedTest 推送到GitHub
echo ========================================
echo.

:: 检查Git是否已安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Git，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git已安装
echo.

:: 检查Git LFS
git lfs version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  未检测到Git LFS
    echo.
    echo 正在安装Git LFS...
    git lfs install
    if %errorlevel% neq 0 (
        echo ❌ Git LFS安装失败
        echo 请手动安装: https://git-lfs.com/
        pause
        exit /b 1
    )
    echo ✅ Git LFS安装成功
) else (
    echo ✅ Git LFS已安装
)
echo.

:: 检查是否已初始化Git仓库
if not exist .git (
    echo 📁 初始化Git仓库...
    git init
    echo ✅ Git仓库初始化完成
) else (
    echo ✅ Git仓库已存在
)
echo.

:: 配置Git LFS
echo 📦 配置Git LFS追踪.pt文件...
git lfs install
git lfs track "*.pt"
echo ✅ Git LFS配置完成
echo.

:: 检查是否已配置用户信息
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  未配置Git用户信息
    echo.
    set /p username="请输入你的GitHub用户名: "
    set /p email="请输入你的GitHub邮箱: "
    git config user.name "%username%"
    git config user.email "%email%"
    echo ✅ 用户信息配置完成
) else (
    for /f "delims=" %%a in ('git config user.name') do set current_user=%%a
    echo ✅ 当前用户: %current_user%
)
echo.

:: 检查远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  未配置远程仓库
    echo.
    echo 请先在GitHub上创建仓库，然后输入仓库地址
    echo 例如: https://github.com/username/SeedTest.git
    echo 或: git@github.com:username/SeedTest.git
    echo.
    set /p remote_url="远程仓库地址: "
    git remote add origin %remote_url%
    echo ✅ 远程仓库配置完成
) else (
    for /f "delims=" %%a in ('git remote get-url origin') do set current_remote=%%a
    echo ✅ 远程仓库: %current_remote%
)
echo.

echo ========================================
echo   开始推送
echo ========================================
echo.

:: 添加文件
echo 📋 添加文件到Git...
git add .gitignore
git add .gitattributes
git add README.md
git add start.py
git add common/
git add modules/
git add frank/
git add models/
git add icons/
git add *.bat
git add *.txt
git add *.md
git add *.yaml
git add *.spec
git add *.iss

echo ✅ 文件添加完成
echo.

:: 查看状态
echo 📊 当前状态:
git status --short
echo.

:: 提交
echo 💾 提交到本地仓库...
git commit -m "Initial commit: SeedTest seed inspection platform

Features:
- Image acquisition module with Hikvision camera support
- Seed inspection module with YOLOv8 models  
- Settings module for camera and balance configuration
- Automatic packaging scripts for Windows installer
- Git LFS for large model files"

if %errorlevel% neq 0 (
    echo ⚠️  没有新的更改需要提交
) else (
    echo ✅ 提交成功
)
echo.

:: 推送
echo 🚀 推送到GitHub...
echo.
echo ⚠️  注意: 如果这是首次推送，可能需要登录GitHub
echo ⚠️  注意: 大文件(模型)上传可能需要几分钟
echo.
pause

git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  推送到main分支失败，尝试master分支...
    git push -u origin master
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 推送失败！
        echo.
        echo 可能的原因:
        echo 1. 网络问题
        echo 2. 需要先在GitHub创建仓库
        echo 3. 没有推送权限
        echo 4. 分支名称不匹配
        echo.
        echo 请检查错误信息并重试
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   ✅ 推送成功！
echo ========================================
echo.
echo 📝 下一步:
echo.
echo 1. 访问你的GitHub仓库页面
echo 2. 点击 "Releases" → "Create a new release"
echo 3. 上传安装包: installer_output\SeedTest_v2.0_Setup.exe
echo.
echo 详细说明请查看: 推送到GitHub指南.md
echo.
pause

