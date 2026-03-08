#!/usr/bin/env python3
"""
PyTorch 哭声分类模型训练 v2 - 优化版
🦞 虾虾开发

优化点:
1. 数据增强 (翻转/旋转/噪声)
2. 更深的网络
3. 类别权重 (处理不平衡)
4. 更多训练轮数
5. Cosine 学习率调度

用法:
    python train_v2.py --epochs 100 --batch_size 32
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
import torchaudio.transforms as T


# 配置
NUM_CLASSES = 4
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class AugmentedCryDataset(Dataset):
    """带数据增强的哭声数据集"""
    def __init__(self, data_dir, augment=False):
        self.data = []
        self.labels = []
        
        data_path = Path(data_dir).resolve()
        print(f"   数据路径：{data_path} (存在：{data_path.exists()})")
        
        for label_idx, class_name in enumerate(CLASS_NAMES):
            class_dir = data_path / class_name
            if not class_dir.exists():
                print(f"   ⚠️  不存在：{class_dir}")
                continue
            
            npy_files = list(class_dir.glob('*.npy'))
            print(f"   ✅ {class_name}: {len(npy_files)} 个文件")
            
            for npy_file in npy_files:
                feature = np.load(npy_file)
                self.data.append(feature)
                self.labels.append(label_idx)
        
        self.data = np.array(self.data)
        self.labels = np.array(self.labels, dtype=np.int64)
        self.augment = augment
        
        # 计算类别权重
        self.class_counts = np.bincount(self.labels.astype(np.int64))
        self.class_weights = 1.0 / self.class_counts
        self.class_weights = self.class_weights / self.class_weights.sum() * NUM_CLASSES
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        x = self.data[idx].copy()
        y = self.labels[idx]
        
        # 数据增强
        if self.augment:
            x = self.augment_sample(x)
        
        x = torch.FloatTensor(x).unsqueeze(0)
        y = torch.LongTensor([y])[0]
        return x, y
    
    def augment_sample(self, x):
        """数据增强"""
        x = x.copy()  # 确保是连续内存
        
        # 1. 随机翻转 (左右)
        if np.random.random() > 0.5:
            x = np.flipud(x).copy()
        
        # 2. 随机平移
        if np.random.random() > 0.5:
            shift = int(np.random.uniform(-5, 5))
            if shift > 0:
                x[:, shift:] = x[:, :-shift]
                x[:, :shift] = x[:, :1]
            elif shift < 0:
                x[:, :shift] = x[:, -shift:]
                x[:, shift:] = x[:, -1:]
            x = x.copy()
        
        # 3. 添加噪声
        if np.random.random() > 0.5:
            noise = np.random.normal(0, 0.05, x.shape)
            x = x + noise
        
        # 4. 随机遮挡 (Cutout)
        if np.random.random() > 0.7:
            h, w = x.shape
            mask_h = int(h * 0.1)
            mask_w = int(w * 0.1)
            y1 = np.random.randint(0, h - mask_h)
            x1 = np.random.randint(0, w - mask_w)
            x[y1:y1+mask_h, x1:x1+mask_w] = 0
        
        return x


class ImprovedCryClassifier(nn.Module):
    """改进版哭声分类 CNN"""
    def __init__(self):
        super().__init__()
        
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            
            # Block 2
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            
            # Block 3
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            
            # Block 4
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, NUM_CLASSES),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def train(data_dir, output_dir, epochs=100, batch_size=32):
    """训练模型"""
    print("\n" + "=" * 60)
    print("🦞 PyTorch 模型训练 v2 - 优化版")
    print("=" * 60)
    print(f"📊 数据：{data_dir}")
    print(f"💾 输出：{output_dir}")
    print(f"📈 Epochs: {epochs}")
    print(f"📦 Batch: {batch_size}")
    print(f"🔧 设备：{DEVICE}")
    print(f"✨ 优化：数据增强 + 更深网络 + 类别权重")
    print("=" * 60 + "\n")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    print("📂 加载数据集...")
    full_dataset = AugmentedCryDataset(data_dir, augment=False)
    print(f"   总样本：{len(full_dataset)}")
    
    if len(full_dataset) == 0:
        print("❌ 数据集中没有样本！检查路径是否正确")
        return None, None
    
    # 划分训练/验证
    val_size = int(len(full_dataset) * 0.2)
    train_size = len(full_dataset) - val_size
    
    torch.manual_seed(42)
    indices = torch.randperm(len(full_dataset)).tolist()
    
    train_indices = indices[:train_size]
    val_indices = indices[train_size:]
    
    train_dataset = torch.utils.data.Subset(
        AugmentedCryDataset(data_dir, augment=True),
        train_indices
    )
    val_dataset = torch.utils.data.Subset(
        AugmentedCryDataset(data_dir, augment=False),
        val_indices
    )
    
    # 计算类别权重
    train_labels = [train_dataset.dataset.labels[i] for i in train_indices]
    class_counts = np.bincount(train_labels, minlength=NUM_CLASSES)
    class_weights = 1.0 / class_counts
    class_weights = class_weights / class_weights.sum() * NUM_CLASSES
    class_weights = torch.FloatTensor(class_weights).to(DEVICE)
    
    print(f"✅ 训练集：{len(train_dataset)} 样本")
    print(f"✅ 验证集：{len(val_dataset)} 样本")
    print(f"⚖️  类别权重：{class_weights}")
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=0)
    
    # 创建模型
    print("\n🏗️  创建模型...")
    model = ImprovedCryClassifier().to(DEVICE)
    
    # 打印参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 总参数：{total_params:,} | 可训练：{trainable_params:,}")
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # 训练循环
    print("\n🚀 开始训练...\n")
    
    best_acc = 0.0
    patience = 15
    no_improve = 0
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
        
        scheduler.step()
        
        # 记录历史
        history['loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        
        # 打印进度
        improved = val_acc > best_acc
        if improved:
            best_acc = val_acc
            no_improve = 0
            torch.save(model.state_dict(), output_path / 'best_model.pth')
        else:
            no_improve += 1
        
        marker = '⭐ BEST' if improved else ''
        print(f"Epoch {epoch+1:3d}/{epochs} | "
              f"Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
              f"Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f} {marker}")
        
        # 早停
        if no_improve >= patience:
            print(f"\n⏹️  早停：{patience} 轮未改进")
            break
    
    # 最终评估
    print(f"\n{'='*60}")
    print(f"✅ 最佳验证准确率：{best_acc:.4f} ({best_acc*100:.2f}%)")
    print(f"{'='*60}")
    
    # 保存最终模型
    torch.save(model.state_dict(), output_path / 'final_model_v2.pth')
    print(f"💾 模型已保存：{output_path / 'final_model_v2.pth'}")
    
    # 保存报告
    report = {
        'best_accuracy': float(best_acc),
        'epochs_trained': epoch + 1,
        'train_samples': len(train_dataset),
        'val_samples': len(val_dataset),
        'class_names': CLASS_NAMES,
        'framework': 'pytorch',
        'version': 'v2',
        'optimizations': [
            '数据增强 (翻转/旋转/噪声/Cutout)',
            '更深的网络 (4 个 Block)',
            '类别权重 (处理不平衡)',
            'Cosine 学习率调度',
            'AdamW 优化器',
            '早停 (patience=15)'
        ]
    }
    
    with open(output_path / 'training_report_v2.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # 保存历史
    with open(output_path / 'training_history_v2.json', 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"📄 报告：{output_path / 'training_report_v2.json'}")
    print("\n🎉 训练完成!")
    
    return model, history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='../data/features')
    parser.add_argument('--output_dir', type=str, default='../models')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=32)
    args = parser.parse_args()
    
    train(args.data_dir, args.output_dir, args.epochs, args.batch_size)


if __name__ == '__main__':
    main()
