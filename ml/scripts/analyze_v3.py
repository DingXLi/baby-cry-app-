#!/usr/bin/env python3
"""
v3 模型分析 - 混淆矩阵
🦞 虾虾开发
"""

import torch
import numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report
import json

MODEL_PATH = '/home/liding/.openclaw/workspace/baby-cry-app/ml/models/best_model_v3.pth'
DATA_DIR = '/home/liding/.openclaw/workspace/baby-cry-app/ml/data/features_v2'
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
INPUT_DIM = 168
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class FeatureClassifier(torch.nn.Module):
    def __init__(self, input_dim=168):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 256),
            torch.nn.BatchNorm1d(256),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(256, 128),
            torch.nn.BatchNorm1d(128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(128, 64),
            torch.nn.BatchNorm1d(64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(64, 4),
        )
    
    def forward(self, x):
        return self.net(x)


def analyze():
    print("\n" + "=" * 60)
    print("🦞 v3 模型分析 - 混淆矩阵")
    print("=" * 60)
    
    # 加载模型
    model = FeatureClassifier(INPUT_DIM)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.to(DEVICE)
    model.eval()
    print(f"✅ 模型加载：{MODEL_PATH}")
    
    # 加载数据
    data = []
    labels = []
    for label_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = Path(DATA_DIR) / class_name
        if not class_dir.exists():
            continue
        for npy_file in class_dir.glob('*.npy'):
            data.append(np.load(npy_file))
            labels.append(label_idx)
    
    data = np.array(data, dtype=np.float32)
    labels = np.array(labels, dtype=np.int64)
    print(f"📂 数据：{len(data)} 样本")
    
    # 预测
    X_tensor = torch.FloatTensor(data).to(DEVICE)
    with torch.no_grad():
        outputs = model(X_tensor)
        _, preds = outputs.max(1)
    
    preds_np = preds.cpu().numpy()
    
    # 分类报告
    print("\n" + "=" * 60)
    print("📊 分类报告")
    print("=" * 60)
    print(classification_report(labels, preds_np, target_names=CLASS_NAMES))
    
    # 混淆矩阵
    cm = confusion_matrix(labels, preds_np)
    
    print("\n" + "=" * 60)
    print("🔥 混淆矩阵")
    print("=" * 60)
    print("\n预测 →")
    print("        ", "  ".join([f"{n[:8]:>10}" for n in CLASS_NAMES]))
    print()
    for i, name in enumerate(CLASS_NAMES):
        row = "  ".join([f"{cm[i,j]:>10}" for j in range(len(CLASS_NAMES))])
        print(f"{name[:8]:>8}  {row}")
    
    # 分析
    print("\n" + "=" * 60)
    print("💡 分析")
    print("=" * 60)
    
    recalls = cm.diagonal() / cm.sum(axis=1)
    print("\n📈 各类召回率:")
    for i, name in enumerate(CLASS_NAMES):
        status = "✅" if recalls[i] > 0.5 else "⚠️" if recalls[i] > 0.3 else "❌"
        print(f"   {status} {name}: {recalls[i]*100:.1f}%")
    
    # 找出主要混淆
    cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)
    max_confusion = 0
    confusion_pair = None
    
    for i in range(len(CLASS_NAMES)):
        for j in range(len(CLASS_NAMES)):
            if i != j and cm_norm[i, j] > max_confusion:
                max_confusion = cm_norm[i, j]
                confusion_pair = (i, j)
    
    if confusion_pair:
        i, j = confusion_pair
        print(f"\n⚠️  主要混淆：{CLASS_NAMES[i]} → {CLASS_NAMES[j]} ({max_confusion*100:.1f}%)")
    
    # 保存报告
    report = {
        'overall_accuracy': float(cm.diagonal().sum() / cm.sum()),
        'per_class_recall': {name: float(recalls[i]) for i, name in enumerate(CLASS_NAMES)},
        'confusion_matrix': cm.tolist(),
        'main_confusion': {
            'from': CLASS_NAMES[confusion_pair[0]],
            'to': CLASS_NAMES[confusion_pair[1]],
            'rate': float(max_confusion)
        } if confusion_pair else None
    }
    
    with open('/home/liding/.openclaw/workspace/baby-cry-app/ml/models/analysis_v3.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 报告：/home/liding/.openclaw/workspace/baby-cry-app/ml/models/analysis_v3.json")
    print("\n🎉 完成!")
    
    return report


if __name__ == '__main__':
    analyze()
