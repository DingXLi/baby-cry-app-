# 📊 数据集划分方案

**策略:** 2 个训练集 + 1 个验证集

---

## 🎯 数据集分配

| 用途 | 数据集 | 作者 | 说明 |
|------|--------|------|------|
| **训练** | Baby Cry Sense | mennaahmed23 | 主训练集 |
| **训练** | Baby Crying Sounds | mennaahmed23 | 补充训练集 |
| **验证** | Infant Cry Dataset | sanmithasadhish | 独立验证集 |

---

## 📁 目录结构

```
ml/data/
├── raw/                          # 原始数据（下载后解压）
│   ├── train_raw/                # 训练数据（合并 2 个数据集）
│   │   ├── baby-cry-sense/
│   │   └── baby-crying-sounds/
│   └── val_raw/                  # 验证数据（1 个数据集）
│       └── infant-cry/
│
├── processed/                    # 预处理后数据
│   ├── train/                    # 训练集（Mel 频谱图）
│   │   ├── hungry/
│   │   ├── sleepy/
│   │   ├── uncomfortable/
│   │   └── normal/
│   └── val/                      # 验证集（Mel 频谱图）
│       ├── hungry/
│       ├── sleepy/
│       ├── uncomfortable/
│       └── normal/
│
└── metadata/
    ├── train_stats.json          # 训练集统计
    ├── val_stats.json            # 验证集统计
    └── class_mapping.json        # 标签映射
```

---

## 🔧 数据处理流程

### 步骤 1: 下载数据集

```bash
cd baby-cry-app/ml/data/raw

# 训练集
kaggle datasets download -d mennaahmed23/baby-cry-sense-dataset
unzip baby-cry-sense-dataset.zip
mv baby-cry-sense-dataset train_raw/

kaggle datasets download -d mennaahmed23/baby-crying-sounds-dataset
unzip baby-crying-sounds-dataset.zip
mv baby-crying-sounds-dataset train_raw/

# 验证集
kaggle datasets download -d sanmithasadhish/infant-cry-dataset
unzip infant-cry-dataset.zip
mv infant-cry-dataset val_raw/
```

### 步骤 2: 探索数据

```bash
cd ../../
python scripts/explore_data.py --data_dir data/raw/train_raw
python scripts/explore_data.py --data_dir data/raw/val_raw
```

### 步骤 3: 预处理

```bash
# 预处理训练集
python scripts/preprocess_audio.py \
  --input_dir data/raw/train_raw \
  --output_dir data/processed/train

# 预处理验证集
python scripts/preprocess_audio.py \
  --input_dir data/raw/val_raw \
  --output_dir data/processed/val
```

### 步骤 4: 提取特征

```bash
python scripts/extract_features.py \
  --input_dir data/processed/train \
  --output_dir data/features/train

python scripts/extract_features.py \
  --input_dir data/processed/val \
  --output_dir data/features/val
```

### 步骤 5: 训练模型

```bash
cd training
python train.py \
  --data_dir ../data/features/train \
  --val_dir ../data/features/val \
  --epochs 50 \
  --batch_size 32
```

---

## 📊 预期数据量

| 数据集 | 预计样本数 | 用途 |
|--------|-----------|------|
| Baby Cry Sense | ~500-1000 | 训练 |
| Baby Crying Sounds | ~500-1000 | 训练 |
| Infant Cry Dataset | ~200-500 | 验证 |
| **总计** | **~1200-2500** | - |

**训练/验证比例:** 约 80/20

---

## ✅ 优势

1. **独立验证集** - 验证集来自不同作者，避免过拟合
2. **数据量充足** - 两个训练集合并，样本量更大
3. **泛化能力强** - 验证集来自不同来源，测试模型泛化能力
4. **可对比效果** - 可以对比单数据集 vs 双数据集的效果

---

## ⚠️ 注意事项

1. **标签对齐** - 确保训练集和验证集的标签映射一致
2. **采样率统一** - 所有音频预处理为 16kHz
3. **格式统一** - 统一为 WAV 格式，单声道
4. **类别平衡** - 检查各类别样本数量，避免严重不平衡

---

## 🦞 下一步

1. 下载三个数据集
2. 按上述结构组织目录
3. 运行探索脚本确认数据
4. 开始预处理 → 训练

---

🦞 虾虾 2026-02-27
