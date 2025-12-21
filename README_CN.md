# 🌾 SeedTest - 种子检测平台

专业的种子检测平台，具有自动化图像采集、AI驱动的种子检测和集成测量系统。

## ✨ 功能特性

### 📸 图像采集模块
- 海康威视工业相机支持
- 实时预览和快照捕获
- 自动图像保存和管理
- 相机参数配置

### 🔍 种子检测模块
- 基于YOLOv8的种子检测
- 多种作物支持（大豆、小麦）
- 定向边界框检测
- 自动计数和测量
- 串口天平集成，用于重量测量
- Excel报告生成

### ⚙️ 设置模块
- 相机配置（曝光、增益、ROI）
- 天平通信设置
- 模型选择和管理
- 用户友好的界面

## 🖥️ 系统要求

- **操作系统**: Windows 10/11 (64位)
- **内存**: 最低4GB RAM（推荐8GB）
- **存储空间**: 2GB可用磁盘空间
- **相机**: 海康威视工业相机（可选）
- **天平**: 带PL23XX驱动的串口天平（可选）

## 📦 安装

### 方式一：下载安装包（推荐）

1. 从 [Releases](https://github.com/xianjunhong/SeedTest/releases) 下载最新的 `SeedTest_vX.X_Setup.exe`
2. 右键安装包 → "以管理员身份运行"
3. 按照安装向导操作
4. 安装程序将自动安装：
   - SeedTest应用程序
   - 海康威视MVS SDK驱动
   - PL23XX串口驱动
5. 安装完成后重启计算机

**注意**：驱动安装可能需要3-5分钟。安装程序在此期间可能看起来卡住 - 这是正常现象，请耐心等待。

### 方式二：从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/xianjunhong/SeedTest.git
cd SeedTest

# 2. 安装Git LFS（模型文件必需）
# Windows: 从 https://git-lfs.com/ 下载
# 安装后运行：
git lfs install

# 3. 下载模型文件（重要！）
git lfs pull

# 4. 验证模型是否正确下载
# 检查文件大小（应该约为100-130 MB）
ls -lh models/*.pt
# 预期：soybean_obb.pt (~101 MB), wheat_det.pt (~130 MB)

# 5. 创建conda环境
conda env create -f environment.yaml
conda activate SeedTest

# 6. 运行应用程序
python start.py
```

**重要提示**：
- **模型文件由Git LFS管理**。克隆后必须运行 `git lfs pull` 来下载实际的模型文件。
- 如果模型文件看起来很小（< 1 MB），说明还没有下载。请运行 `git lfs pull`。
- 如果从源码运行，需要手动安装海康威视MVS SDK和PL23XX驱动。

## 📥 下载模型文件

本项目使用 **Git LFS** 管理大型模型文件。克隆仓库后，您需要单独下载模型。

### 自动下载（推荐）

如果已安装Git LFS，模型会在克隆时自动下载：

```bash
git clone https://github.com/xianjunhong/SeedTest.git
cd SeedTest
git lfs pull  # 如果模型没有自动下载
```

### 手动下载

如果自动下载失败或未安装Git LFS：

```bash
# 1. 安装Git LFS（如果未安装）
# Windows: https://git-lfs.com/
# 安装后：
git lfs install

# 2. 克隆仓库
git clone https://github.com/xianjunhong/SeedTest.git
cd SeedTest

# 3. 下载LFS文件
git lfs pull
```

### 验证模型

检查模型是否正确下载：

```bash
# 检查LFS文件状态
git lfs ls-files

# 检查文件大小（应该约为100-130 MB）
ls -lh models/*.pt
```

**预期的模型文件**：
- `models/soybean_obb.pt` (~101 MB)
- `models/wheat_det.pt` (~130 MB)

### 故障排除

**问题**：模型文件很小（< 1 MB）  
**解决方案**：运行 `git lfs pull` 下载实际文件

**问题**：`git lfs: command not found`  
**解决方案**：从 https://git-lfs.com/ 安装Git LFS

**问题**：LFS下载失败  
**解决方案**：
- 检查网络连接
- 验证GitHub LFS配额（免费版：1GB存储，1GB/月带宽）
- 重试：`git lfs pull`

## 🚀 快速开始

1. **启动SeedTest** 从开始菜单或桌面快捷方式

2. **配置相机**（设置模块）：
   - 选择您的海康威视相机
   - 调整曝光和增益
   - 如需要，设置ROI

3. **采集图像**（图像采集模块）：
   - 点击"预览"开始实时查看
   - 点击"捕获"拍摄快照
   - 图像自动保存

4. **检测种子**（种子检测模块）：
   - 加载捕获的图像
   - 选择适当的模型（大豆/小麦）
   - 点击"检测"进行分析
   - 查看结果并导出到Excel

## 📁 项目结构

```
SeedTest/
├── start.py                 # 主入口点
├── common/                  # 通用模块
│   ├── camera_base.py      # 相机接口
│   ├── balance_manager.py  # 天平通信
│   ├── config_manager.py   # 配置处理
│   └── ...
├── modules/                 # 应用模块
│   ├── image_acquisition/  # 图像采集模块
│   ├── seed_inspection/    # 种子检测模块
│   └── settings/           # 设置模块
├── models/                  # YOLOv8模型（Git LFS）
│   ├── soybean_obb.pt     # 大豆检测模型 (~101 MB)
│   └── wheat_det.pt       # 小麦检测模型 (~130 MB)
├── icons/                   # UI图标
├── 重新打包.bat            # 完整重建脚本
├── 快速更新代码.bat        # 快速更新脚本
└── make_installer.bat      # 创建安装包
```

## 🔧 开发

### 从源码构建

```bash
# 激活环境
conda activate SeedTest

# 完整重建（清理 + 构建 + 复制资源）
.\重新打包.bat

# 快速更新（仅代码更改）
.\快速更新代码.bat

# 创建安装包
.\make_installer.bat
```

安装包将在 `installer_output/` 目录中生成。

### 技术栈

- **GUI框架**: PyQt5
- **AI模型**: YOLOv8 (Ultralytics)
- **相机SDK**: 海康威视MVS SDK
- **串口通信**: pyserial
- **打包工具**: PyInstaller + Inno Setup

## 📝 许可证

本软件仅供学术和研究用途。

作者：JinLab  
版权所有 (c) 2025 JinLab。保留所有权利。

## 🤝 贡献

欢迎贡献！请随时提交Pull Request。

## 📧 联系方式

如需技术支持或有问题，请在GitHub上提交issue。

## 🙏 致谢

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - 目标检测框架
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [Hikvision](https://www.hikvision.com/) - 工业相机SDK

## 📸 截图

> 在此处添加应用程序的截图

---

**由 JinLab 用 ❤️ 制作**

