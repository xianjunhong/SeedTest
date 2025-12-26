# SeedTest - Rebuild Script
# Full rebuild with PyInstaller

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "   SeedTest - Full Rebuild"  -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

# Step 1: Activate conda environment
Write-Host "[1/6] Activating conda environment..." -ForegroundColor Yellow
& conda activate SeedTest
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate environment" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "Environment activated" -ForegroundColor Green
Write-Host ""

# Step 2: Clean old files
Write-Host "[2/6] Cleaning old build files..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "SeedTest.spec") { Remove-Item -Force "SeedTest.spec" }
Write-Host "Cleanup complete" -ForegroundColor Green
Write-Host ""

# Step 3: Run PyInstaller
Write-Host "[3/6] Running PyInstaller (10-15 minutes)..." -ForegroundColor Yellow
Write-Host "Please wait..." -ForegroundColor Gray
Write-Host ""

pyinstaller `
  --name="SeedTest" `
  --windowed `
  --icon="icons/app_icon.png" `
  --add-data="icons;icons" `
  --add-data="models;models" `
  --add-data="config.ini;." `
  --hidden-import=ultralytics `
  --hidden-import=torch `
  --hidden-import=torchvision `
  --hidden-import=cv2 `
  --hidden-import=PyQt5 `
  --hidden-import=serial `
  --hidden-import=pandas `
  --hidden-import=openpyxl `
  --hidden-import=shapely `
  --collect-data=ultralytics `
  --noconfirm `
  start.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "PyInstaller failed!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "PyInstaller completed" -ForegroundColor Green

# Step 4: Copy Hikvision DLLs
Write-Host ""
Write-Host "[4/6] Copying Hikvision SDK DLLs..." -ForegroundColor Yellow
$dllPath = "C:\Program Files (x86)\Common Files\MVS\Runtime\Win64_x64\*.dll"
$targetPath = "dist\SeedTest\"
try {
    Copy-Item -Path $dllPath -Destination $targetPath -ErrorAction Stop
    Write-Host "Hikvision DLLs copied" -ForegroundColor Green
} catch {
    Write-Host "Warning: Auto-copy failed, please copy DLLs manually" -ForegroundColor Yellow
}

# Step 5: Copy icons and models
Write-Host ""
Write-Host "[5/6] Ensuring icons and models exist..." -ForegroundColor Yellow
if (-not (Test-Path "dist\SeedTest\icons")) {
    Copy-Item -Recurse -Force "icons" "dist\SeedTest\icons\"
    Write-Host "Icons copied" -ForegroundColor Green
}

if (-not (Test-Path "dist\SeedTest\models")) {
    New-Item -ItemType Directory -Path "dist\SeedTest\models" -Force | Out-Null
    Copy-Item "models\*.pt" "dist\SeedTest\models\" -ErrorAction SilentlyContinue
    Copy-Item "models\*.csv" "dist\SeedTest\models\" -ErrorAction SilentlyContinue
    Write-Host "Models copied" -ForegroundColor Green
}

# Step 6: Copy config
Write-Host ""
Write-Host "[6/6] Copying config file..." -ForegroundColor Yellow
Copy-Item "config.ini" "dist\SeedTest\" -Force
Write-Host "config.ini copied" -ForegroundColor Green

# Done
Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "Output directory: dist\SeedTest\" -ForegroundColor White
Write-Host "Main executable: dist\SeedTest\SeedTest.exe" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test: cd dist\SeedTest; .\SeedTest.exe" -ForegroundColor Gray
Write-Host "  2. Distribute: Compress the dist\SeedTest\ folder" -ForegroundColor Gray
Write-Host ""
pause

