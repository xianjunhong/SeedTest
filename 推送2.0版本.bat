@echo off
chcp 65001 >nul
echo ========================================
echo   推送SeedTest 2.0到GitHub
echo ========================================
echo.
echo 你的GitHub仓库: https://github.com/xianjunhong/SeedTest
echo.
echo 说明：
echo - 这是2.0大改版，会覆盖GitHub上的旧代码
echo - 模型文件(.pt)会通过Git LFS上传
echo - 大约需要10-20分钟（取决于网速）
echo.
pause
echo.

:: 第一步：安装Git LFS
echo [步骤 1/6] 配置Git LFS...
git lfs install
if %errorlevel% neq 0 (
    echo ❌ Git LFS安装失败
    echo 请手动安装: https://git-lfs.com/
    pause
    exit /b 1
)
echo ✅ Git LFS配置完成
echo.

:: 第二步：初始化Git（如果还没有）
if not exist .git (
    echo [步骤 2/6] 初始化Git仓库...
    git init
    git branch -M main
    echo ✅ Git仓库初始化完成
) else (
    echo [步骤 2/6] Git仓库已存在
)
echo.

:: 第三步：配置远程仓库
echo [步骤 3/6] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/xianjunhong/SeedTest.git
echo ✅ 远程仓库配置完成
echo.

:: 第四步：添加所有文件
echo [步骤 4/6] 添加文件到Git...
echo.
echo 正在添加文件...
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

:: 第五步：提交到本地
echo [步骤 5/6] 提交到本地仓库...
git commit -m "Release v2.0: Major refactor

Breaking Changes:
- Complete UI redesign with PyQt5
- New modular architecture (image_acquisition, seed_inspection, settings)
- Integrated YOLOv8 models for seed detection
- Added Hikvision camera support
- Added serial balance integration
- Automatic installer with driver installation

Features:
- Image acquisition module with real-time preview
- Seed inspection with AI detection (soybean, wheat)
- Comprehensive settings module
- Excel report generation
- Professional Windows installer

Technical:
- Models tracked with Git LFS
- PyInstaller packaging
- Inno Setup installer
"

if %errorlevel% neq 0 (
    echo ⚠️ 没有新的更改或提交失败
    echo 继续推送...
)
echo ✅ 本地提交完成
echo.

:: 第六步：推送到GitHub
echo [步骤 6/6] 推送到GitHub...
echo.
echo ⚠️ 重要提示：
echo 1. 这会覆盖GitHub上的旧代码（因为是2.0大改版）
echo 2. 如果是首次推送，可能需要输入GitHub用户名和密码
echo 3. 密码建议使用Personal Access Token，不是GitHub密码
echo.
echo 如何获取Token：
echo    GitHub → 头像 → Settings → Developer settings 
echo    → Personal access tokens → Tokens(classic) → Generate new token
echo    → 勾选 repo 权限 → 复制token作为密码使用
echo.
echo 开始推送...
pause
echo.

:: 强制推送（覆盖旧代码）
git push -f origin main

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ 推送到main分支失败，尝试master分支...
    git push -f origin master
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 推送失败！
        echo.
        echo 常见问题：
        echo 1. 需要登录GitHub（输入用户名和Token）
        echo 2. 网络问题（检查网络连接）
        echo 3. Token权限不足（确保勾选了repo权限）
        echo.
        echo 如果看到authentication失败：
        echo - 用户名：xianjunhong
        echo - 密码：使用Personal Access Token（不是GitHub密码！）
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   ✅ 推送成功！
echo ========================================
echo.
echo 🎉 恭喜！SeedTest 2.0已成功推送到GitHub！
echo.
echo 📍 仓库地址: https://github.com/xianjunhong/SeedTest
echo.
echo ========================================
echo   下一步：上传安装包
echo ========================================
echo.
echo 1. 访问: https://github.com/xianjunhong/SeedTest/releases
echo 2. 点击 "Create a new release"
echo 3. 填写信息:
echo    - Tag: v2.0
echo    - Title: SeedTest v2.0 - Major Refactor
echo    - 描述: 见下方模板
echo 4. 上传文件: installer_output\SeedTest_v2.0_Setup.exe (909MB)
echo 5. 点击 "Publish release"
echo.
echo ========================================
echo   Release描述模板（复制下面的内容）
echo ========================================
echo.
type nul > release_notes_v2.0.txt
(
echo ## SeedTest v2.0 - Major Refactor
echo.
echo ### 🎉 What's New
echo.
echo This is a complete rewrite of SeedTest with modern architecture and features!
echo.
echo ### ✨ Features
echo.
echo - **📸 Image Acquisition Module**
echo   - Hikvision industrial camera support
echo   - Real-time preview and capture
echo   - Automatic image management
echo.
echo - **🔍 Seed Inspection Module** 
echo   - YOLOv8-powered AI detection
echo   - Support for soybean and wheat
echo   - Serial balance integration
echo   - Excel report generation
echo.
echo - **⚙️ Settings Module**
echo   - Camera configuration
echo   - Balance settings
echo   - Model management
echo.
echo ### 📦 Installation
echo.
echo 1. Download `SeedTest_v2.0_Setup.exe` below
echo 2. Right-click → "Run as administrator"
echo 3. Follow installation wizard
echo 4. **Important**: Driver installation takes 3-5 minutes, please be patient!
echo 5. Restart computer after installation
echo.
echo ### 📋 System Requirements
echo.
echo - Windows 10/11 ^(64-bit^)
echo - 4GB RAM ^(8GB recommended^)
echo - 2GB free disk space
echo - Administrator privileges
echo.
echo ### 🔧 What's Included
echo.
echo - SeedTest application
echo - Hikvision MVS SDK driver ^(auto-installed^)
echo - PL23XX serial driver ^(auto-installed^)
echo - YOLOv8 detection models
echo.
echo ### ⚠️ Important Notes
echo.
echo - This is a **breaking change** - not compatible with v1.x
echo - Backup your data before upgrading
echo - Driver installation may appear frozen - this is normal
echo.
echo ### 📸 Screenshots
echo.
echo ^(Add screenshots of your application here^)
echo.
echo ---
echo.
echo **Full Changelog**: https://github.com/xianjunhong/SeedTest/compare/v1.0...v2.0
) > release_notes_v2.0.txt

echo Release描述已保存到: release_notes_v2.0.txt
echo 你可以复制这个文件的内容到GitHub Release中
echo.
notepad release_notes_v2.0.txt
echo.
pause

