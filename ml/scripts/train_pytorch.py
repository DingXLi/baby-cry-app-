#!/usr/bin/env python3
"""
PyTorch 哭声分类模型训练
🦞 虾虾开发

用法:
    python train_pytorch.py --data_dir ../data/features --epochs 30
"""

import argparse
import os
from pathlib import Path
import numpy as np
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


# 配置
NUM_CLASSES = 4
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class CryDataset(Dataset):
    """哭声数据集"""
    def __init__(self, data_dir):
        self.data = []
        self.labels = []
        
        for label_idx, class_name in enumerate(CLASS_NAMES):
            class_dir = Path(data_dir) / class_name
            if not class_dir.exists():
                continue
            
            for npy_file in class_dir.glob('*.npy'):
                feature = np.load(npy_file)
                self.data.append(feature)
                self.labels.append(label_idx)
        
        self.data = np.array(self.data)
        self.labels = np.array(self.labels)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        x = self.data[idx]
        x = torch.FloatTensor(x).unsqueeze(0)  # 添加通道维度
        y = torch.LongTensor([self.labels[idx]])[0]
        return x, y


class CryClassifier(nn.Module):
    """哭声分类 CNN"""
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
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
        )
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, NUM_CLASSES),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def train(data_dir, output_dir, epochs=30, batch_size=32):
    """训练模型"""
    print("\n" + "=" * 60)
    print("🦞 PyTorch 模型训练")
    print("=" * 60)
    print(f"📊 数据：{data_dir}")
    print(f"💾 输出：{output_dir}")
    print(f"📈 Epochs: {epochs}")
    print(f"📦 Batch: {batch_size}")
    print(f"🔧 设备：{DEVICE}")
    print("=" * 60 + "\n")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    print("📂 加载数据集...")
    dataset = CryDataset(data_dir)
    
    # 划分训练/验证
    val_size = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    print(f"✅ 训练集：{len(train_dataset)} 样本")
    print(f"✅ 验证集：{len(val_dataset)} 样本")
    
    # 创建模型
    print("\n🏗️  创建模型...")
    model = CryClassifier().to(DEVICE)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5
    )
    
    # 训练循环
    print("\n🚀 开始训练...\n")
    
    best_acc = 0.0
    history = {'loss': [], 'val_loss': [], 'acc': [], 'val_acc': []}
    
    for epoch in range(epochs):
        # 训练
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        
        train_loss /= len(train_loader)
        train_acc = correct / total
        
        # 验证
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = correct / total
        
        scheduler.step(val_loss)
        
        # 记录历史
        history['loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        
        # 打印进度
        print(f"Epoch {epoch+1:3d}/{epochs} | "
              f"Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f}"
              f"{' ⭐' if val_acc > best_acc else ''}")
        
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), output_path / 'best_model.pth')
    
    # 最终评估
    print(f"\n✅ 最佳验证准确率：{best_acc:.4f} ({best_acc*100:.2f}%)")
    
    # 保存最终模型
    torch.save(model.state_dict(), output_path / 'final_model.pth')
    print(f"💾 模型已保存：{output_path / 'final_model.pth'}")
    
    # 保存报告
    report = {
        'best_accuracy': float(best_acc),
        'epochs_trained': epochs,
        'train_samples': len(train_dataset),
        'val_samples': len(val_dataset),
        'class_names': CLASS_NAMES,
        'framework': 'pytorch',
    }
    
    with open(output_path / 'training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # 保存历史
    with open(output_path / 'training_history.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"📄 报告：{output_path / 'training_report.json'}")
    print("\n🎉 训练完成!")
    
    return model, history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='../data/features')
    parser.add_argument('--output_dir', type=str, default='../models')
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch_size', type=int, default=32)
    args = parser.parse_args()
    
    train(args.data_dir, args.output_dir, args.epochs, args.batch_size)


if __name__ == '__main__':
    main()
