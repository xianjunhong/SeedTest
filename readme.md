# 🌾 SeedTest - Seed Inspection Platform

A professional seed inspection platform with automated image acquisition, AI-powered seed detection, and integrated measurement systems.

## ✨ Features

### 📸 Image Acquisition Module
- Hikvision industrial camera support
- Real-time preview and snapshot capture
- Automatic image saving and management
- Camera parameter configuration

### 🔍 Seed Inspection Module
- YOLOv8-based seed detection
- Multiple crop support (soybean, wheat)
- Oriented bounding box detection
- Automatic counting and measurement
- Serial balance integration for weight measurement
- Excel report generation

### ⚙️ Settings Module
- Camera configuration (exposure, gain, ROI)
- Balance communication settings
- Model selection and management
- User-friendly interface

## 🖥️ System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free disk space
- **Camera**: Hikvision industrial camera (optional)
- **Balance**: Serial port balance with PL23XX driver (optional)

## 📦 Installation

### Option 1: Download Installer (Recommended)

1. Download the latest `SeedTest_vX.X_Setup.exe` from [Releases](../../releases)
2. Right-click the installer → "Run as administrator"
3. Follow the installation wizard
4. The installer will automatically install:
   - SeedTest application
   - Hikvision MVS SDK driver
   - PL23XX serial port driver
5. Restart your computer after installation

**Note**: Driver installation may take 3-5 minutes. The installer may appear frozen during this time - this is normal, please be patient.

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/SeedTest.git
cd SeedTest

# Create conda environment
conda env create -f environment.yaml
conda activate SeedTest

# Run the application
python start.py
```

**Note**: You'll need to install Hikvision MVS SDK and PL23XX driver manually if running from source.

## 🚀 Quick Start

1. **Launch SeedTest** from the Start Menu or desktop shortcut

2. **Configure Camera** (Settings Module):
   - Select your Hikvision camera
   - Adjust exposure and gain
   - Set ROI if needed

3. **Acquire Images** (Image Acquisition Module):
   - Click "Preview" to start live view
   - Click "Capture" to take snapshot
   - Images are automatically saved

4. **Inspect Seeds** (Seed Inspection Module):
   - Load captured images
   - Select appropriate model (soybean/wheat)
   - Click "Detect" to analyze
   - View results and export to Excel

## 📁 Project Structure

```
SeedTest/
├── start.py                 # Main entry point
├── common/                  # Common modules
│   ├── camera_base.py      # Camera interface
│   ├── balance_manager.py  # Balance communication
│   ├── config_manager.py   # Configuration handler
│   └── ...
├── modules/                 # Application modules
│   ├── image_acquisition/  # Image acquisition module
│   ├── seed_inspection/    # Seed inspection module
│   └── settings/           # Settings module
├── models/                  # YOLOv8 models
│   ├── soybean_obb.pt     # Soybean detection model
│   └── wheat_det.pt       # Wheat detection model
├── icons/                   # UI icons
├── 重新打包.bat            # Full rebuild script
├── 快速更新代码.bat        # Quick update script
└── make_installer.bat      # Create installer

```

## 🔧 Development

### Building from Source

```bash
# Activate environment
conda activate SeedTest

# Full rebuild (clean + build + copy assets)
.\重新打包.bat

# Quick update (code changes only)
.\快速更新代码.bat

# Create installer
.\make_installer.bat
```

The installer will be generated in `installer_output/` directory.

### Tech Stack

- **GUI Framework**: PyQt5
- **AI Model**: YOLOv8 (Ultralytics)
- **Camera SDK**: Hikvision MVS SDK
- **Serial Communication**: pyserial
- **Packaging**: PyInstaller + Inno Setup

## 📝 License

This software is for academic and research purposes only.

Author: JinLab  
Copyright (c) 2025 JinLab. All rights reserved.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For technical support or questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection framework
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Hikvision](https://www.hikvision.com/) - Industrial camera SDK

## 📸 Screenshots

> Add screenshots of your application here

---

**Made with ❤️ by JinLab**
