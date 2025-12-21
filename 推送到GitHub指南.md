# 推送SeedTest到GitHub完整指南

## 📋 概述

### 文件大小问题
- ✅ 代码文件：正常推送
- ⚠️ 模型文件（.pt）：使用 **Git LFS**
- ❌ 安装包（.exe）：使用 **GitHub Releases**
- ❌ 驱动程序（.exe）：不推送，用户自行下载

---

## 📦 第一步：安装Git LFS

### Windows上安装Git LFS

```powershell
# 方法1：使用Git自带的
git lfs install

# 方法2：下载安装器
# 访问：https://git-lfs.com/
# 下载并安装
```

安装后验证：
```powershell
git lfs version
```

---

## 🚀 第二步：初始化Git仓库并配置

### 1. 初始化Git（如果还没有）

```powershell
cd C:\Users\Frank\OneDrive\Desktop\SeedTest

# 初始化
git init

# 配置用户信息（如果还没配置）
git config user.name "YourName"
git config user.email "your.email@example.com"
```

### 2. 启用Git LFS

```powershell
# 安装LFS钩子
git lfs install

# 追踪.pt文件（已在.gitattributes中配置）
git lfs track "*.pt"

# 验证LFS配置
git lfs track
```

### 3. 添加文件到Git

```powershell
# 添加.gitignore和.gitattributes
git add .gitignore
git add .gitattributes

# 添加所有项目文件
git add .

# 查看状态
git status
```

### 4. 提交

```powershell
git commit -m "Initial commit: SeedTest seed inspection platform

Features:
- Image acquisition module with Hikvision camera support
- Seed inspection module with YOLOv8 models
- Settings module for camera and balance configuration
- Automatic packaging scripts for Windows installer
"
```

---

## 🌐 第三步：创建GitHub仓库并推送

### 1. 在GitHub上创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`SeedTest` 或 `seed-inspection-platform`
3. 描述：`Seed inspection platform with YOLOv8, Hikvision camera support`
4. 选择 **Private**（如果不想公开）或 **Public**
5. **不要**勾选 "Initialize with README"（我们已有文件）
6. 点击 "Create repository"

### 2. 连接远程仓库

```powershell
# 添加远程仓库（替换YOUR_USERNAME和REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 或使用SSH（推荐）
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# 验证
git remote -v
```

### 3. 推送到GitHub

```powershell
# 推送（首次）
git push -u origin main

# 或者如果你的分支叫master
git push -u origin master
```

**注意**：Git LFS会自动上传大文件！

---

## 📢 第四步：发布安装包（GitHub Releases）

### 方法1：通过GitHub网页

1. 访问你的仓库页面
2. 点击右侧的 "Releases"
3. 点击 "Create a new release"
4. 填写信息：
   - **Tag**: `v2.0`
   - **Release title**: `SeedTest v2.0 - Initial Release`
   - **Description**:
     ```markdown
     ## SeedTest v2.0
     
     ### Features
     - Image acquisition with Hikvision camera support
     - Seed inspection using YOLOv8 models
     - Serial balance integration
     - Camera and balance configuration
     
     ### Installation
     1. Download `SeedTest_v2.0_Setup.exe`
     2. Right-click → "Run as administrator"
     3. Follow the installation wizard
     4. Restart your computer after installation
     
     ### System Requirements
     - Windows 10/11 (64-bit)
     - At least 2GB free disk space
     - Administrator privileges
     
     ### What's Included
     - SeedTest application
     - Hikvision MVS SDK driver (auto-installed)
     - PL23XX serial driver (auto-installed)
     - YOLOv8 models (soybean, wheat)
     
     ### Notes
     - Driver installation may take 3-5 minutes
     - Please be patient during installation
     ```
5. 拖拽上传 `SeedTest_v2.0_Setup.exe`
6. 点击 "Publish release"

### 方法2：使用GitHub CLI

```powershell
# 安装GitHub CLI (如果没有)
# 访问: https://cli.github.com/

# 登录
gh auth login

# 创建Release并上传安装包
gh release create v2.0 `
  installer_output/SeedTest_v2.0_Setup.exe `
  --title "SeedTest v2.0 - Initial Release" `
  --notes "See full release notes in repository"
```

---

## 📝 第五步：更新README

创建一个专业的README.md：

```powershell
# 我会为你创建一个README.md
```

---

## 🔄 后续更新流程

### 修改代码后推送

```powershell
# 1. 查看修改
git status

# 2. 添加修改的文件
git add .

# 3. 提交
git commit -m "描述你的修改"

# 4. 推送
git push
```

### 更新模型文件

```powershell
# Git LFS会自动处理
git add models/*.pt
git commit -m "Update models"
git push
```

### 发布新版本安装包

```powershell
# 重新打包
.\重新打包.bat
.\make_installer.bat

# 创建新Release
gh release create v2.1 `
  installer_output/SeedTest_v2.1_Setup.exe `
  --title "SeedTest v2.1" `
  --notes "What's new in v2.1..."
```

---

## ⚠️ 重要注意事项

### 1. 不要推送的文件（已在.gitignore）
- ✅ `dist/` - PyInstaller输出
- ✅ `build/` - 构建缓存
- ✅ `installer_output/` - 安装包（用Releases）
- ✅ `data/` - 用户数据
- ✅ `config.ini` - 可能包含敏感信息

### 2. Git LFS配额
- GitHub Free: 1GB存储 + 1GB/月带宽
- 超额后需要付费或删除旧版本

### 3. 驱动程序
- `MVS_STD_4.4.0_240913.exe`（307MB）
- `PL23XX-M_LogoDriver_Setup_408_20220725.exe`（13MB）
- **建议**：不推送到GitHub，在README中提供下载链接

---

## 📊 文件大小总结

| 文件 | 大小 | 处理方式 |
|------|------|---------|
| `soybean_obb.pt` | 101 MB | Git LFS ✅ |
| `wheat_det.pt` | 130 MB | Git LFS ✅ |
| `SeedTest_v2.0_Setup.exe` | 909 MB | GitHub Releases ✅ |
| `MVS_STD_*.exe` | 307 MB | 不推送，提供链接 ✅ |
| `PL23XX*.exe` | 13 MB | 不推送，提供链接 ✅ |
| 其他代码文件 | < 10 MB | 正常Git ✅ |

---

## 🆘 常见问题

### Q: Git LFS推送很慢？
**A**: 正常的，大文件需要时间。可以：
- 使用有线网络
- 分多次推送
- 考虑使用其他模型托管服务（如Hugging Face）

### Q: 超过LFS配额怎么办？
**A**: 
1. 删除旧版本模型
2. 使用`git lfs prune`清理
3. 考虑外部存储（Google Drive, 百度网盘等）

### Q: 如何分享项目给别人？
**A**:
1. 分享GitHub仓库链接
2. 用户clone后会自动下载LFS文件
3. 从Releases下载安装包

---

## ✅ 完整检查清单

推送前确认：
- [ ] 已安装Git LFS
- [ ] 已创建`.gitignore`
- [ ] 已创建`.gitattributes`
- [ ] 已提交所有必要文件
- [ ] 已在GitHub创建仓库
- [ ] 已推送代码
- [ ] 已创建Release并上传安装包
- [ ] 已更新README.md

---

**现在可以开始推送了！** 🚀

