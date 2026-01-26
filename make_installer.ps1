# SeedTest - Create Installer Script
# Compile the Inno Setup installer

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "   SeedTest - Create Installer"  -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""

# Check Inno Setup
Write-Host "[1/4] Checking Inno Setup..." -ForegroundColor Yellow
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $innoPath)) {
    Write-Host ""
    Write-Host "ERROR: Inno Setup not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Inno Setup 6:" -ForegroundColor Yellow
    Write-Host "Download: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or update the innoPath variable in this script" -ForegroundColor Gray
    pause
    exit 1
}
Write-Host "Inno Setup found" -ForegroundColor Green

# Check packaged files
Write-Host ""
Write-Host "[2/4] Checking packaged files..." -ForegroundColor Yellow
if (-not (Test-Path "dist\SeedTest\SeedTest.exe")) {
    Write-Host ""
    Write-Host "ERROR: SeedTest.exe not found!" -ForegroundColor Red
    Write-Host "Please run rebuild.ps1 first to package the application" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "Packaged files found" -ForegroundColor Green

# Create license and install notes
Write-Host ""
Write-Host "[3/4] Creating license and install notes..." -ForegroundColor Yellow

# Create LICENSE.txt (English)
$licenseContent = @"
SeedTest Software License Agreement

This software is for educational and research purposes only.
Author: JinLab

"@
Set-Content -Path "LICENSE.txt" -Value $licenseContent -Encoding UTF8

# Create INSTALL_NOTES.txt (English)
$installNotesContent = @"
Installation Instructions

1. This software requires Hikvision MVS SDK driver for camera functionality

2. If using serial port balance, PL23XX driver is required

3. The installer will automatically install these drivers (requires admin privileges)

4. IMPORTANT: If the camera or serial port is not working after installation, 
   please restart your computer manually to complete driver installation

5. On first run, please configure camera and balance parameters in Settings module

6. For detailed instructions, see the documentation in the installation directory

"@
Set-Content -Path "INSTALL_NOTES.txt" -Value $installNotesContent -Encoding UTF8

Write-Host "License and notes created" -ForegroundColor Green

# Compile installer
Write-Host ""
Write-Host "[4/4] Compiling installer with Inno Setup..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

& $innoPath "installer_script.iss"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Installer compilation failed!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "Installer Created Successfully!" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "Output location: installer_output\" -ForegroundColor White
Write-Host "Filename: SeedTest_v2.0_Setup.exe" -ForegroundColor White
Write-Host ""
Write-Host "Installer includes:" -ForegroundColor Yellow
Write-Host "  - SeedTest application" -ForegroundColor Gray
Write-Host "  - Hikvision MVS SDK driver" -ForegroundColor Gray
Write-Host "  - PL23XX serial port driver" -ForegroundColor Gray
Write-Host ""
Write-Host "Ready to distribute!" -ForegroundColor Green
Write-Host ""
pause

