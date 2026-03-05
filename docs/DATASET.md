# 📊 数据集调研与下载指南

**最后更新:** 2026-02-27

---

## 🎯 已选定的数据集

### 1. Baby Crying Sounds Dataset (Menna Ahmed)

**链接:** https://www.kaggle.com/datasets/mennaahmed23/baby-crying-sounds-dataset

**特点:**
- 专门针对婴儿哭声分类
- 包含多种哭声类型
- 格式：WAV/MP3

**待确认:**
- [ ] 具体分类标签
- [ ] 数据量大小
- [ ] 采样率

---

### 2. Infant Cry Dataset (Sanmitha Sadish)

**链接:** https://www.kaggle.com/datasets/sanmithasadhish/infant-cry-dataset

**特点:**
- 学术用途数据集
- 可能有详细标注

**待确认:**
- [ ] 分类标签
- [ ] 数据量
- [ ] 许可证

---

## 📥 下载方法

### 方法 A: Kaggle CLI (推荐)

```bash
# 1. 安装 Kaggle CLI
pip install kaggle

# 2. 配置 API Token
# 去 https://www.kaggle.com/account -> Create New API Token
# 下载 kaggle.json，放到 ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json

# 3. 下载数据集
cd baby-cry-app/ml/data/raw

# 数据集 1
kaggle datasets download -d mennaahmed23/baby-crying-sounds-dataset
unzip baby-crying-sounds-dataset.zip

# 数据集 2
kaggle datasets download -d sanmithasadhish/infant-cry-dataset
unzip infant-cry-dataset.zip
```

### 方法 B: 浏览器下载

1. 打开数据集链接
2. 点击 "Download" 按钮
3. 解压到 `ml/data/raw/` 目录

---

## 📁 数据目录结构

```
ml/data/
├── raw/                    # 原始数据（下载后）
│   ├── baby-crying-sounds-dataset/
│   └── infant-cry-dataset/
│
├── processed/              # 处理后数据（运行预处理脚本后）
│   ├── train/
│   │   ├── hungry/
│   │   ├── sleepy/
│   │   ├── uncomfortable/
│   │   └── normal/
│   └── val/
│       ├── hungry/
│       ├── sleepy/
│       ├── uncomfortable/
│       └── normal/
│
└── metadata/
    ├── class_mapping.json
    └── dataset_stats.json
```

---

## 🔧 数据预处理

### 步骤 1: 探索数据集

```bash
cd baby-cry-app/ml
python scripts/explore_data.py
```

### 步骤 2: 预处理音频

```bash
python scripts/preprocess_audio.py \
  --input_dir data/raw \
  --output_dir data/processed \
  --target_sr 16000 \
  --duration 5
```

### 步骤 3: 提取特征

```bash
python scripts/extract_features.py \
  --input_dir data/processed \
  --output_dir data/features \
  --n_mels 128
```

---

## 🏷️ 分类标签映射

根据我们的需求，需要将数据集标签映射到：

| 内部标签 | 可能的原始标签 | 说明 |
|----------|---------------|------|
| `hungry` | hungry, hunger, feeding | 饿了 |
| `sleepy` | sleepy, tired, sleep | 困了 |
| `uncomfortable` | pain, discomfort, sick | 不舒服/疼痛 |
| `normal` | normal, neutral, baseline | 正常哭声 |

---

## 📊 数据集统计（待更新）

下载并探索后运行：
```bash
python scripts/dataset_stats.py
```

预期输出：
```json
{
  "total_samples": 0,
  "total_duration_hours": 0,
  "class_distribution": {},
  "average_duration_seconds": 0,
  "sample_rate": 0,
  "format": ""
}
```

---

## ⚠️ 注意事项

1. **许可证:** 确认数据集允许商用/修改
2. **隐私:** 婴儿音频数据需妥善处理
3. **质量:** 检查音频质量（噪音、采样率）
4. **平衡:** 各类别样本数量是否平衡

---

## 🦞 下一步

1. **Li 下载数据集** - 用 Kaggle CLI 或浏览器
2. **放到 `ml/data/raw/`** - 解压
3. **运行探索脚本** - `python scripts/explore_data.py`
4. **确认标签映射** - 根据实际数据集调整
5. **开始预处理** - 提取 Mel 频谱特征

---

## 📚 参考资源

- **Kaggle API 文档:** https://www.kaggle.com/docs/api
- **Librosa 文档:** https://librosa.org/doc/latest/
- **音频特征提取:** https://www.tensorflow.org/tutorials/audio/transfer_learning_audio
