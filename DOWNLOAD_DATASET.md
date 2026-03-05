# 📥 数据集下载指南

🦞 按步骤操作，5 分钟搞定！

---

## 步骤 1: 获取 Kaggle API Token

1. 打开 https://www.kaggle.com/account
2. 点击 **"Create New API Token"**
3. 下载 `kaggle.json` 文件

---

## 步骤 2: 配置 API Token

### macOS / Linux

```bash
# 创建目录
mkdir -p ~/.kaggle

# 移动 kaggle.json 文件
mv ~/Downloads/kaggle.json ~/.kaggle/

# 设置权限（重要！）
chmod 600 ~/.kaggle/kaggle.json
```

### Windows

```powershell
# 创建目录
mkdir C:\Users\<你的用户名>\.kaggle

# 移动 kaggle.json 到该目录
```

---

## 步骤 3: 安装 Kaggle CLI

```bash
pip install kaggle
```

---

## 步骤 4: 下载数据集

```bash
# 进入项目目录
cd baby-cry-app/ml/data/raw

# 下载数据集 1
kaggle datasets download -d mennaahmed23/baby-crying-sounds-dataset
unzip baby-crying-sounds-dataset.zip

# 下载数据集 2 (可选)
kaggle datasets download -d sanmithasadhish/infant-cry-dataset
unzip infant-cry-dataset.zip
```

---

## 步骤 5: 验证数据

```bash
cd baby-cry-app/ml
python scripts/explore_data.py
```

看到类似输出就成功了：
```
🦞 数据集探索工具
============================================================
📂 数据目录：../data/raw
============================================================
📊 数据集统计
------------------------------------------------------------
🎵 音频文件总数：XXX
...
```

---

## 步骤 6: 预处理音频

```bash
cd baby-cry-app/ml
python scripts/preprocess_audio.py
```

---

## ❓ 常见问题

### Q: `kaggle: command not found`
**A:** 确保已安装：`pip install kaggle`

### Q: `Permission denied`
**A:** 设置正确权限：`chmod 600 ~/.kaggle/kaggle.json`

### Q: 下载速度慢
**A:** Kaggle 免费账户有限速，可以：
- 用浏览器下载（点击数据集页面的 Download 按钮）
- 解压到 `ml/data/raw/` 目录

### Q: 找不到音频文件
**A:** 检查解压后的目录结构，确保 `.wav` 文件在 `ml/data/raw/` 下

---

## 🎯 下一步

数据准备好后，就可以开始训练模型了：

```bash
cd baby-cry-app/ml
python training/train.py --data_dir data/processed --epochs 50
```

---

🦞 有问题随时问虾虾！
