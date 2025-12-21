@echo off
chcp 65001 >nul
echo ======================================
echo    制作考种平台安装包
echo ======================================
echo.

echo [检查] Inno Setup...
set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

if not exist "%INNO_PATH%" (
    echo.
    echo ❌ 未找到 Inno Setup！
    echo.
    echo 请先安装 Inno Setup 6:
    echo 下载地址: https://jrsoftware.org/isdl.php
    echo.
    echo 或修改此脚本中的 INNO_PATH 路径
    pause
    exit /b 1
)

echo [检查] 打包文件...
if not exist "dist\SeedTest\SeedTest.exe" (
    echo.
    echo ❌ 未找到打包好的程序！
    echo 请先运行 重新打包.bat 打包程序
    pause
    exit /b 1
)

echo.
echo [创建] 安装前说明文件...

REM 创建 LICENSE.txt
echo 考种平台使用许可协议 > LICENSE.txt
echo. >> LICENSE.txt
echo 本软件仅供学习和科研使用。 >> LICENSE.txt
echo 作者：JinLab >> LICENSE.txt
echo. >> LICENSE.txt

REM 创建 INSTALL_NOTES.txt
echo 安装说明 > INSTALL_NOTES.txt
echo. >> INSTALL_NOTES.txt
echo 1. 本软件需要安装海康威视相机驱动（MVS SDK）才能使用相机功能 >> INSTALL_NOTES.txt
echo. >> INSTALL_NOTES.txt
echo 2. 如果使用串口天平，需要安装PL23XX串口驱动 >> INSTALL_NOTES.txt
echo. >> INSTALL_NOTES.txt
echo 3. 安装程序会自动安装这些驱动（需要管理员权限） >> INSTALL_NOTES.txt
echo. >> INSTALL_NOTES.txt
echo 4. 首次运行时，请在"设置"模块中配置相机和天平参数 >> INSTALL_NOTES.txt
echo. >> INSTALL_NOTES.txt
echo 5. 详细使用说明请查看安装目录中的"使用说明.md" >> INSTALL_NOTES.txt
echo. >> INSTALL_NOTES.txt

echo [编译] 安装包...
"%INNO_PATH%" installer_script.iss

if errorlevel 1 (
    echo.
    echo ❌ 制作安装包失败！
    pause
    exit /b 1
)

echo.
echo ======================================
echo ✅ 安装包制作完成！
echo ======================================
echo.
echo 输出位置: installer_output\
echo 文件名: SeedTest_v2.0_Setup.exe
echo.
echo 📦 安装包包含:
echo   - SeedTest主程序
echo   - 海康威视相机驱动（MVS SDK）
echo   - PL23XX串口驱动
echo.
echo 💡 分发给用户时，只需提供这一个安装包文件即可！
echo.
pause


