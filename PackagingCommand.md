# 步骤1: PyInstaller 打包 (10-15分钟)
powershell -ExecutionPolicy Bypass -File .\rebuild.ps1

# 步骤2: 制作安装包 (2-5分钟)
powershell -ExecutionPolicy Bypass -File .\make_installer.ps1