# 项目名称: 大豆表型信息提取软件

本项目旨在提供一套大豆考种场景下的表型信息提取与分析工具，集成图像处理、模型推理、数据管理等模块。

---

## 📦 环境安装

### 使用 conda 一些环境

```bash
conda env create -f environment.yaml
conda activate SeedTest
```

### 使用 pip 装一些环境

```bash
pip install -r requirements.txt
```

---

## 🚀 如何运行

```bash
python start_v2.py
```

---

## 📁 注意事项：模型文件为 Git LFS 存储

本项目包含大体积模型文件（如 `model/soybean_best.pt`），已通过 [Git LFS](https://git-lfs.com/) 管理。

### 第一次克隆项目时，请执行以下命令安装 Git LFS：

```bash
# 安装 Git LFS（只需一次）
git lfs install
```

然后正常克隆项目：

```bash
git clone git@github.com:xianjunhong/SeedTest.git
cd SeedTest
```

### 若克隆后模型文件大小只有 1KB，请手动拉取真实模型文件：

```bash
git lfs pull
```

---

## 💡 建议

- 请勿直接在 Git 中添加超过 100MB 的文件，否则 GitHub 将拒绝推送。
- 对模型文件的更新请参考 Git LFS 使用规范。

---

## 📞 联系方式

如有任何问题或合作意向，欢迎联系项目作者：[@xianjunhong](https://github.com/xianjunhong)
邮箱：xian_junhong@163.com



| 时间点 | 绿叶面积 | 黄叶面积 | 小区面积（可省略） |
| --- | ---- | ---- | --------- |
| 1   | 0.30 | 0.05 | 1.0       |
| 2   | 0.35 | 0.10 | 1.0       |
| 3   | 0.32 | 0.20 | 1.0       |
| ... | ...  | ...  | ...       |
