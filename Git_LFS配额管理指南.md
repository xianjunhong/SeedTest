# Git LFS 配额管理指南

## 📊 GitHub LFS 免费配额

### 免费账户
- **存储空间**: 1 GB
- **带宽**: 1 GB/月
- **超额费用**: $5/月 可获得额外 50GB 存储 + 50GB 带宽

---

## 🎯 你的文件情况

### 当前模型文件大小
- `soybean_obb.pt`: 101 MB
- `wheat_det.pt`: 130 MB
- **总计**: 231 MB

### 如果有1.0版本的模型
假设1.0版本也有2个模型（~230 MB），总计约 460 MB

✅ **好消息：完全在1GB免费配额内！**

---

## 🤔 需要删除1.0版本的模型吗？

### 情况1：1.0版本的模型还在用
**建议：保留**
- 如果用户还在用1.0，他们需要这些模型
- 你可以保留1.0作为历史版本

### 情况2：2.0完全替代1.0，不再维护1.0
**建议：删除**
- 节省空间
- 简化仓库
- 用户直接用2.0

### 情况3：2.0是大改版（你的情况）
**建议：用强制推送覆盖（推荐）**
- 直接用2.0替换整个仓库
- 旧版本不再保留
- 最简单直接

---

## 🛠️ 如何删除旧版本LFS文件

### 方法1：强制推送（推荐，最简单）

这就是我在`推送2.0版本.bat`中做的：

```bash
# 完全用新代码替换旧代码
git push -f origin main
```

这会：
- ✅ 删除所有旧文件（包括旧模型）
- ✅ 只保留2.0版本
- ✅ 释放LFS空间（旧模型不占用配额）

### 方法2：手动删除旧文件（如果要保留历史）

```bash
# 1. 克隆仓库
git clone https://github.com/xianjunhong/SeedTest.git
cd SeedTest

# 2. 删除旧模型文件
git rm models/old_model_v1.pt

# 3. 提交
git commit -m "Remove old models"

# 4. 清理LFS缓存
git lfs prune

# 5. 推送
git push
```

### 方法3：清理整个Git历史（彻底释放空间）

如果你确定不需要任何历史记录：

```bash
# 创建新的干净仓库
rm -rf .git
git init
git add .
git commit -m "Clean start with v2.0"
git remote add origin https://github.com/xianjunhong/SeedTest.git
git push -f origin main
```

---

## 💡 我的建议（针对你的情况）

### 推荐方案：强制推送2.0（最简单）

**原因：**
1. ✅ 2.0是大改版，跟1.0完全不一样
2. ✅ 不需要保留旧代码
3. ✅ 最简单直接
4. ✅ 自动删除旧模型，释放LFS空间

**操作：**
直接运行 `推送2.0版本.bat`，它会自动：
- 用2.0代码覆盖整个仓库
- 删除所有1.0的文件（包括旧模型）
- 只上传2.0的新模型（231 MB）

---

## 📈 如何查看LFS使用情况

### 方法1：GitHub网页查看

1. 访问：https://github.com/settings/billing
2. 查看 "Git LFS Data" 使用情况

### 方法2：命令行查看

```bash
# 查看仓库中的LFS文件
git lfs ls-files

# 查看LFS使用情况
git lfs fetch --all
git lfs status
```

---

## 🔮 未来如何管理模型文件

### 选项1：继续使用Git LFS（推荐）
**优点：**
- 集成在Git中，使用方便
- 你的模型只有231MB，完全够用
- 免费配额足够

**缺点：**
- 有1GB限制
- 超额需要付费

### 选项2：使用其他服务托管模型

**Hugging Face Hub（推荐）**
```python
# 上传模型
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj="models/soybean_obb.pt",
    path_in_repo="soybean_obb.pt",
    repo_id="xianjunhong/seedtest-models",
)

# 下载模型
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="xianjunhong/seedtest-models",
    filename="soybean_obb.pt",
    local_dir="models"
)
```

**其他选项：**
- Google Drive + 分享链接
- 百度网盘 + 分享链接
- 阿里云OSS
- AWS S3

### 选项3：在README中提供下载链接

```markdown
## Models

Due to file size limitations, please download models separately:

- Soybean model: [Download](https://your-link.com/soybean_obb.pt)
- Wheat model: [Download](https://your-link.com/wheat_det.pt)

Place them in the `models/` directory.
```

---

## ✅ 总结（针对你的情况）

### 回答你的问题：

**Q: 需要删除1.0版本的pt文件吗？**

**A: 是的，建议删除（通过强制推送）**

理由：
1. ✅ 2.0是大改版，完全替代1.0
2. ✅ 节省LFS配额（虽然你还很充足）
3. ✅ 避免混淆，保持仓库简洁
4. ✅ 最简单的方式：直接运行`推送2.0版本.bat`

### 配额情况：

```
你的使用: 231 MB (2.0版本的2个模型)
免费配额: 1000 MB
剩余: 769 MB
使用率: 23.1%
```

✅ **完全不用担心配额问题！**

即使将来再增加2-3个模型也完全没问题。

---

## 🚀 下一步操作

1. **运行** `推送2.0版本.bat`
2. **等待** 10-20分钟（模型上传需要时间）
3. **上传安装包** 到GitHub Releases
4. **完成！**

不需要手动删除任何东西，脚本会自动处理！

