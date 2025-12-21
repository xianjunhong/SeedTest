@echo off
chcp 65001 >nul
echo ========================================
echo    考种平台 - 重新打包脚本
echo ========================================
echo.

echo [1/6] 激活conda环境...
call conda activate SeedTest
if errorlevel 1 (
    echo ❌ 激活环境失败
    pause
    exit /b 1
)
echo ✅ 环境已激活

echo.
echo [2/6] 清理旧的打包文件...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "KaoZhong.spec" del /q KaoZhong.spec
echo ✅ 清理完成

echo.
echo [3/6] 开始打包（10-15分钟）...
echo 请耐心等待...
echo.

pyinstaller ^
  --name="SeedTest" ^
  --windowed ^
  --icon="icons/app_icon.png" ^
  --add-data="icons;icons" ^
  --add-data="models;models" ^
  --add-data="config.ini;." ^
  --hidden-import=ultralytics ^
  --hidden-import=torch ^
  --hidden-import=torchvision ^
  --hidden-import=cv2 ^
  --hidden-import=PyQt5 ^
  --hidden-import=serial ^
  --hidden-import=pandas ^
  --hidden-import=openpyxl ^
  --hidden-import=shapely ^
  --collect-data=ultralytics ^
  --noconfirm ^
  start.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    pause
    exit /b 1
)

echo.
echo ✅ 打包完成

echo.
echo [4/6] 复制海康SDK的DLL...
copy "C:\Program Files (x86)\Common Files\MVS\Runtime\Win64_x64\*.dll" "dist\SeedTest\" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  自动复制失败，请手动复制DLL
) else (
    echo ✅ 海康DLL已复制
)

echo.
echo [5/6] 确保icons和models目录存在...
if not exist "dist\SeedTest\icons" (
    xcopy "icons" "dist\SeedTest\icons\" /E /I /Y >nul
    echo ✅ icons已复制
)

if not exist "dist\SeedTest\models" (
    mkdir "dist\SeedTest\models" 2>nul
    copy "models\*.pt" "dist\SeedTest\models\" >nul 2>&1
    copy "models\*.csv" "dist\SeedTest\models\" >nul 2>&1
    echo ✅ models已复制
)

echo.
echo [6/6] 复制配置文件...
copy "config.ini" "dist\SeedTest\" >nul 2>&1
echo ✅ config.ini已复制

echo.
echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.
echo 输出目录: dist\SeedTest\
echo 主程序: dist\SeedTest\SeedTest.exe
echo.
echo 💡 下一步：
echo   1. 测试: cd dist\SeedTest ^&^& SeedTest.exe
echo   2. 分发: 压缩 dist\SeedTest\ 文件夹
echo.
pause

