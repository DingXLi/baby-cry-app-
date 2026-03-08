#!/usr/bin/env python3
"""
混淆矩阵分析 - 诊断模型问题
🦞 虾虾开发

用法:
    python analyze_confusion.py
"""

import torch
import numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report
import json

# 配置
MODEL_PATH = 'models/final_model_v3.pth'
DATA_DIR = '/home/liding/.openclaw/workspace/baby-cry-app/ml/data/features'
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 简单的模型定义 (用于加载权重) - v3 版本
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            # Block 2
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            # Block 3
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(128, 4)
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def load_data(data_dir):
    """加载验证集数据"""
    data_path = Path(data_dir)
    print(f"   数据路径：{data_path}")
    data = []
    labels = []
    
    for label_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = data_path / class_name
        if not class_dir.exists():
            print(f"   ⚠️  不存在：{class_dir}")
            continue
        npy_files = list(class_dir.glob('*.npy'))
        print(f"   ✅ {class_name}: {len(npy_files)} 个文件")
        for npy_file in npy_files:
            data.append(np.load(npy_file))
            labels.append(label_idx)
    
    print(f"   总计：{len(data)} 样本")
    return np.array(data), np.array(labels)

def analyze():
    print("\n" + "=" * 60)
    print("🦞 混淆矩阵分析")
    print("=" * 60)
    
    # 加载模型
    print(f"\n📥 加载模型：{MODEL_PATH}")
    model = SimpleCNN()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.to(DEVICE)
    model.eval()
    print("✅ 模型加载完成")
    
    # 加载数据
    print(f"\n📂 加载数据：{DATA_DIR}")
    X, y_true = load_data(DATA_DIR)
    X = np.expand_dims(X, axis=1)  # 添加通道维度
    print(f"✅ 数据：{len(X)} 样本")
    
    # 预测
    print("\n🔮 进行预测...")
    X_tensor = torch.FloatTensor(X).to(DEVICE)
    y_true_tensor = torch.LongTensor(y_true).to(DEVICE)
    
    with torch.no_grad():
        outputs = model(X_tensor)
        _, y_pred = outputs.max(1)
    
    y_pred_np = y_pred.cpu().numpy()
    
    # 计算指标
    print("\n" + "=" * 60)
    print("📊 分类报告")
    print("=" * 60)
    print(classification_report(y_true, y_pred_np, target_names=CLASS_NAMES))
    
    # 混淆矩阵
    cm = confusion_matrix(y_true, y_pred_np)
    
    print("\n" + "=" * 60)
    print("🔥 混淆矩阵")
    print("=" * 60)
    print("\n预测 →")
    print("        ", "  ".join([f"{n[:6]:>8}" for n in CLASS_NAMES]))
    print()
    for i, name in enumerate(CLASS_NAMES):
        print(f"{name[:8]:>8}", "  ".join([f"{cm[i,j]:>8}" for j in range(len(CLASS_NAMES))]))
    
    # 分析
    print("\n" + "=" * 60)
    print("💡 分析结果")
    print("=" * 60)
    
    # 计算每类的召回率
    recalls = cm.diagonal() / cm.sum(axis=1)
    print("\n📈 各类召回率:")
    for i, name in enumerate(CLASS_NAMES):
        status = "✅" if recalls[i] > 0.5 else "⚠️" if recalls[i] > 0.3 else "❌"
        print(f"   {status} {name}: {recalls[i]*100:.1f}%")
    
    # 找出最容易混淆的类别对
    print("\n🔍 主要混淆问题:")
    cm_normalized = cm.astype('float') / cm.sum(axis=1, keepdims=True)
    max_confusion = 0
    confusion_pair = None
    
    for i in range(len(CLASS_NAMES)):
        for j in range(len(CLASS_NAMES)):
            if i != j and cm_normalized[i, j] > max_confusion:
                max_confusion = cm_normalized[i, j]
                confusion_pair = (i, j)
    
    if confusion_pair:
        i, j = confusion_pair
        print(f"   ⚠️  {CLASS_NAMES[i]} 经常被误判为 {CLASS_NAMES[j]} ({max_confusion*100:.1f}%)")
    
    # 保存报告
    report = {
        'overall_accuracy': float((cm.diagonal().sum() / cm.sum())),
        'per_class_recall': {name: float(recalls[i]) for i, name in enumerate(CLASS_NAMES)},
        'confusion_matrix': cm.tolist(),
        'main_confusion': {
            'from': CLASS_NAMES[confusion_pair[0]],
            'to': CLASS_NAMES[confusion_pair[1]],
            'rate': float(max_confusion)
        } if confusion_pair else None
    }
    
    with open('models/confusion_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 报告已保存：models/confusion_analysis.json")
    print("\n🎉 分析完成!")
    
    return report


if __name__ == '__main__':
    analyze()
