#!/usr/bin/env python3
"""
哭声分类器训练脚本（sklearn + ONNX 导出）
🦞 虾虾开发

支持真实数据（npy 特征文件）和合成数据。
训练后自动导出 ONNX 模型供移动端使用。

用法:
    python train_classifier.py --data_dir ../data/features --output_dir ../models
    python train_classifier.py --synthetic --samples_per_class 300
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

CLASSES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
CLASSES_CN = {'hungry': '饿了', 'sleepy': '困了', 'uncomfortable': '不舒服', 'normal': '正常'}


# ─── Data Loading ────────────────────────────────────────────────────────────

def load_from_npy_dir(data_dir: str):
    """Load npy features from per-class subdirectories."""
    data_path = Path(data_dir)

    # Fast path: pre-combined X.npy / y.npy
    if (data_path / 'X.npy').exists() and (data_path / 'y.npy').exists():
        X = np.load(data_path / 'X.npy')
        y = np.load(data_path / 'y.npy')
        print(f"📂 加载预合并数据集：{X.shape}")
        return X, y

    X_list, y_list = [], []
    for label_idx, cls in enumerate(CLASSES):
        cls_dir = data_path / cls
        if not cls_dir.exists():
            print(f"⚠️  跳过：{cls}")
            continue
        files = sorted(cls_dir.glob('*.npy'))
        for f in files:
            X_list.append(np.load(f).flatten())
            y_list.append(label_idx)
        print(f"   {cls}: {len(files)} 个样本")

    return np.array(X_list, dtype=np.float32), np.array(y_list)


def load_synthetic(samples_per_class: int):
    sys.path.insert(0, str(Path(__file__).parent))
    from generate_synthetic_data import generate_mfcc_features

    X_list, y_list = [], []
    for label_idx, cls in enumerate(CLASSES):
        feats = generate_mfcc_features(cls, samples_per_class, seed=42 + label_idx)
        X_list.append(feats)
        y_list.extend([label_idx] * samples_per_class)

    return np.vstack(X_list), np.array(y_list)


# ─── Training ─────────────────────────────────────────────────────────────────

def train(X, y, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n📊 数据集：{len(X)} 样本，{X.shape[1]} 维特征")
    for i, cls in enumerate(CLASSES):
        n = (y == i).sum()
        print(f"   {cls}（{CLASSES_CN[cls]}）：{n} 个")

    # Train / val split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n🔀 训练集：{len(X_train)}  验证集：{len(X_val)}")

    # Model pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42,
            verbose=0,
        )),
    ])

    print("\n🚀 开始训练 GradientBoosting 分类器...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    print(f"\n✅ 验证集准确率：{acc:.4f} ({acc*100:.2f}%)")
    print("\n📊 分类报告：")
    print(classification_report(y_val, y_pred, target_names=CLASSES))

    # Cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
    print(f"📊 5折交叉验证：{cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred)
    print(f"\n🔢 混淆矩阵：\n{cm}")

    # ─── ONNX Export ──────────────────────────────────────────────────────────
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType

        initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
        onnx_model = convert_sklearn(pipeline, initial_types=initial_type,
                                     target_opset=11)

        onnx_path = output_path / 'cry_classifier.onnx'
        with open(onnx_path, 'wb') as f:
            f.write(onnx_model.SerializeToString())

        size_kb = onnx_path.stat().st_size / 1024
        print(f"\n📱 ONNX 模型导出：{onnx_path} ({size_kb:.1f} KB)")

        # Verify ONNX
        import onnx
        onnx.checker.check_model(str(onnx_path))
        print("✅ ONNX 验证通过")

        # Mobile assets
        mobile_assets = Path(__file__).parent.parent.parent / 'mobile' / 'assets'
        mobile_assets.mkdir(exist_ok=True)
        import shutil
        shutil.copy(onnx_path, mobile_assets / 'cry_classifier.onnx')
        print(f"📲 已复制到移动端：{mobile_assets / 'cry_classifier.onnx'}")

    except Exception as e:
        print(f"⚠️  ONNX 导出失败：{e}")

    # ─── Save metadata ────────────────────────────────────────────────────────
    report = {
        'model_type': 'GradientBoosting',
        'input_dim': int(X.shape[1]),
        'num_classes': len(CLASSES),
        'classes': CLASSES,
        'classes_cn': CLASSES_CN,
        'val_accuracy': float(acc),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
    }
    with open(output_path / 'training_report.json', 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Class mapping for mobile
    mapping = {
        'classes': CLASSES,
        'classes_cn': CLASSES_CN,
        'input_dim': int(X.shape[1]),
        'model_version': '1.0',
        'accuracy': float(acc),
    }
    mobile_assets_dir = Path(__file__).parent.parent.parent / 'mobile' / 'assets'
    mobile_assets_dir.mkdir(exist_ok=True)
    with open(mobile_assets_dir / 'class_mapping.json', 'w') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n📄 训练报告：{output_path / 'training_report.json'}")
    print("🎉 训练完成！")

    return pipeline, report


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='婴儿哭声分类器训练')
    parser.add_argument('--data_dir', default='../data/features', help='特征数据目录')
    parser.add_argument('--output_dir', default='../models', help='模型输出目录')
    parser.add_argument('--synthetic', action='store_true', help='使用合成数据')
    parser.add_argument('--samples_per_class', type=int, default=300, help='合成数据每类样本数')
    args = parser.parse_args()

    print("=" * 60)
    print("🦞 婴儿哭声分类器训练")
    print("=" * 60)

    if args.synthetic or not Path(args.data_dir).exists():
        if not args.synthetic:
            print(f"⚠️  数据目录不存在，使用合成数据")
        print(f"\n🔬 生成合成数据（{args.samples_per_class} 样本/类）...")
        X, y = load_synthetic(args.samples_per_class)
    else:
        X, y = load_from_npy_dir(args.data_dir)

    train(X, y, args.output_dir)


if __name__ == '__main__':
    main()
