@echo off
chcp 65001 >nul
echo ========================================
echo 考种平台 - 启动程序
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [信息] Python 已安装
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [信息] 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
) else (
    echo [提示] 未检测到虚拟环境，使用全局 Python
)

echo.
echo [信息] 正在启动考种平台...
echo.

REM 启动程序
python start.py

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    echo.
    echo 可能的原因：
    echo 1. 缺少依赖包，请运行: pip install -r requirements.txt
    echo 2. 配置文件错误，请检查 config_new.ini
    echo 3. 模型文件缺失，请将 .pt 文件放入 models/ 文件夹
    echo.
    pause
    exit /b 1
)

echo.
echo [信息] 程序已正常关闭
pause

