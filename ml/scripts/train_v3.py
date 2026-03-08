#!/usr/bin/env python3
"""
PyTorch 哭声分类 v3 - 使用 168 维新特征
🦞 虾虾开发

用法:
    python train_v3.py --epochs 100
"""

import argparse
from pathlib import Path
import numpy as np
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

NUM_CLASSES = 4
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
INPUT_DIM = 168  # 新特征维度
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class CryFeatureDataset(Dataset):
    def __init__(self, data_dir):
        self.data = []
        self.labels = []
        
        for label_idx, class_name in enumerate(CLASS_NAMES):
            class_dir = Path(data_dir) / class_name
            if not class_dir.exists():
                continue
            for npy_file in class_dir.glob('*.npy'):
                self.data.append(np.load(npy_file))
                self.labels.append(label_idx)
        
        self.data = np.array(self.data, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        x = torch.FloatTensor(self.data[idx])
        y = torch.LongTensor([self.labels[idx]])[0]
        return x, y


class FeatureClassifier(nn.Module):
    def __init__(self, input_dim=168):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, NUM_CLASSES),
        )
    
    def forward(self, x):
        return self.net(x)


def train(data_dir, output_dir, epochs=100, batch_size=32):
    print("\n" + "=" * 60)
    print("🦞 PyTorch 训练 v3 - 168 维新特征")
    print("=" * 60)
    print(f"📊 数据：{data_dir}")
    print(f"🔢 特征维度：{INPUT_DIM}")
    print(f"📈 Epochs: {epochs}")
    print(f"🔧 设备：{DEVICE}")
    print("=" * 60)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    dataset = CryFeatureDataset(data_dir)
    print(f"\n📂 总样本：{len(dataset)}")
    
    # 划分训练/验证
    val_size = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_ds, val_ds = torch.utils.data.random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    
    print(f"✅ 训练：{len(train_ds)} | 验证：{len(val_ds)}")
    
    # 创建模型
    model = FeatureClassifier(INPUT_DIM).to(DEVICE)
    params = sum(p.numel() for p in model.parameters())
    print(f"🏗️  参数量：{params:,}")
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # 训练
    print("\n🚀 开始训练...\n")
    
    best_acc = 0
    patience = 20
    no_improve = 0
    history = {'loss': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)
        
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                val_loss += criterion(outputs, labels).item()
                _, pred = outputs.max(1)
                total += labels.size(0)
                correct += pred.eq(labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = correct / total
        scheduler.step()
        
        history['loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        if val_acc > best_acc:
            best_acc = val_acc
            no_improve = 0
            torch.save(model.state_dict(), output_path / 'best_model_v3.pth')
            print(f"Epoch {epoch+1:3d}/{epochs} | Loss: {train_loss:.4f} | Val: {val_loss:.4f} | Acc: {val_acc:.4f} ⭐")
        else:
            no_improve += 1
            print(f"Epoch {epoch+1:3d}/{epochs} | Loss: {train_loss:.4f} | Val: {val_loss:.4f} | Acc: {val_acc:.4f}")
        
        if no_improve >= patience:
            print(f"\n⏹️  早停 @ epoch {epoch+1}")
            break
    
    print(f"\n{'='*60}")
    print(f"✅ 最佳验证准确率：{best_acc:.4f} ({best_acc*100:.2f}%)")
    print(f"{'='*60}")
    
    # 保存
    torch.save(model.state_dict(), output_path / 'final_model_v3.pth')
    
    report = {
        'best_accuracy': float(best_acc),
        'epochs_trained': epoch + 1,
        'model': 'FeatureClassifier',
        'version': 'v3',
        'feature_dim': INPUT_DIM,
        'notes': '168 维特征 (MFCC+Delta+ZCR+Mel)'
    }
    
    with open(output_path / 'training_report_v3.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    with open(output_path / 'training_history_v3.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"💾 模型：{output_path / 'final_model_v3.pth'}")
    print(f"📄 报告：{output_path / 'training_report_v3.json'}")
    print("\n🎉 完成!")
    
    return best_acc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='/home/liding/.openclaw/workspace/baby-cry-app/ml/data/features_v2')
    parser.add_argument('--output_dir', type=str, default='/home/liding/.openclaw/workspace/baby-cry-app/ml/models')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=32)
    args = parser.parse_args()
    train(args.data_dir, args.output_dir, args.epochs, args.batch_size)
