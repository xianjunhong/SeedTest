@echo off
chcp 65001 >nul
echo ========================================
echo    快速更新 - 只更新Python代码
echo ========================================
echo.
echo 💡 说明：
echo   - 适用于只修改了Python代码的情况
echo   - 比完整打包快10倍（约1分钟）
echo   - 不重新打包PyTorch、OpenCV等大库
echo.
pause

echo.
echo [1/3] 激活环境...
call conda activate SeedTest

echo.
echo [2/3] 删除旧的Python代码...
if exist "dist\SeedTest\common" rmdir /s /q "dist\SeedTest\common"
if exist "dist\SeedTest\modules" rmdir /s /q "dist\SeedTest\modules"
if exist "dist\SeedTest\frank" rmdir /s /q "dist\SeedTest\frank"
if exist "dist\SeedTest\start.py" del /q "dist\SeedTest\start.py"
if exist "dist\SeedTest\until.py" del /q "dist\SeedTest\until.py"
echo ✅ 已删除旧代码

echo.
echo [3/3] 复制新代码...
xcopy "common" "dist\SeedTest\common\" /E /I /Y >nul
xcopy "modules" "dist\SeedTest\modules\" /E /I /Y >nul
xcopy "frank" "dist\SeedTest\frank\" /E /I /Y >nul
copy "start.py" "dist\SeedTest\" >nul
copy "until.py" "dist\SeedTest\" >nul
copy "config.ini" "dist\SeedTest\" >nul
echo ✅ 新代码已复制

echo.
echo ========================================
echo ✅ 快速更新完成！
echo ========================================
echo.
echo 测试: cd dist\SeedTest ^&^& SeedTest.exe
echo.
pause

