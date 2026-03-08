#!/usr/bin/env python3
"""
简化版模型训练脚本 - 使用 CPU 训练
🦞 虾虾开发

用法:
    python train_simple.py --data_dir ../data/features --epochs 30
"""

import argparse
import os
import sys
from pathlib import Path
import numpy as np
import json

print("🦞 正在加载 TensorFlow...")

# 禁用 GPU 避免兼容性问题
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import tensorflow as tf
from tensorflow import keras

# 禁用详细日志
tf.get_logger().setLevel('ERROR')

print("✅ TensorFlow 加载完成")


# 模型配置
INPUT_SHAPE = (128, 128, 1)
NUM_CLASSES = 4
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']


def create_model():
    """创建轻量级 CNN 模型"""
    inputs = keras.Input(shape=INPUT_SHAPE)
    
    # Block 1
    x = keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.MaxPooling2D((2, 2))(x)
    x = keras.layers.Dropout(0.25)(x)
    
    # Block 2
    x = keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.MaxPooling2D((2, 2))(x)
    x = keras.layers.Dropout(0.25)(x)
    
    # Block 3
    x = keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.MaxPooling2D((2, 2))(x)
    x = keras.layers.Dropout(0.25)(x)
    
    # Global Average Pooling
    x = keras.layers.GlobalAveragePooling2D()(x)
    
    # Dense layers
    x = keras.layers.Dense(128, activation='relu')(x)
    x = keras.layers.Dropout(0.5)(x)
    
    # Output
    outputs = keras.layers.Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = keras.Model(inputs, outputs)
    
    return model


def load_features(data_dir):
    """加载特征数据"""
    print(f"📂 加载特征：{data_dir}")
    
    data_path = Path(data_dir)
    class_names = ['hungry', 'sleepy', 'uncomfortable', 'normal']
    
    X_list = []
    y_list = []
    
    for label_idx, class_name in enumerate(class_names):
        class_dir = data_path / class_name
        if not class_dir.exists():
            continue
        
        npy_files = list(class_dir.glob('*.npy'))
        print(f"   {class_name}: {len(npy_files)} 个样本")
        
        for npy_file in npy_files:
            feature = np.load(npy_file)
            X_list.append(feature)
            y_list.append(label_idx)
    
    X = np.array(X_list)
    y = np.array(y_list)
    X = np.expand_dims(X, axis=-1)
    
    print(f"✅ 加载完成：{X.shape[0]} 个样本")
    return X, y


def train(data_dir, output_dir, epochs=30, batch_size=32):
    """训练模型"""
    print("\n" + "=" * 60)
    print("🦞 模型训练开始")
    print("=" * 60)
    print(f"📊 数据：{data_dir}")
    print(f"💾 输出：{output_dir}")
    print(f"📈 Epochs: {epochs}")
    print(f"📦 Batch: {batch_size}")
    print("=" * 60 + "\n")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    X, y = load_features(data_dir)
    
    # 打乱
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    # 划分训练/验证
    val_split = 0.2
    val_size = int(len(X) * val_split)
    X_train, X_val = X[val_size:], X[:val_size]
    y_train, y_val = y[val_size:], y[:val_size]
    
    print(f"\n📊 训练集：{len(X_train)} 样本")
    print(f"📊 验证集：{len(X_val)} 样本")
    
    # One-hot
    y_train_cat = keras.utils.to_categorical(y_train, NUM_CLASSES)
    y_val_cat = keras.utils.to_categorical(y_val, NUM_CLASSES)
    
    # 创建模型
    print("\n🏗️  创建模型...")
    model = create_model()
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # 回调
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=str(output_path / 'best_model.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
    ]
    
    # 训练
    print("\n🚀 开始训练...\n")
    history = model.fit(
        X_train, y_train_cat,
        validation_data=(X_val, y_val_cat),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks
    )
    
    # 评估
    print("\n📊 评估...")
    test_loss, test_acc = model.evaluate(X_val, y_val_cat, verbose=0)
    print(f"\n✅ 验证集准确率：{test_acc:.4f} ({test_acc*100:.2f}%)")
    
    # 保存
    model.save(output_path / 'final_model.h5')
    print(f"💾 模型已保存：{output_path / 'final_model.h5'}")
    
    # 保存报告
    report = {
        'final_accuracy': float(test_acc),
        'epochs_trained': len(history.history['loss']),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'class_names': CLASS_NAMES,
    }
    
    with open(output_path / 'training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
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
