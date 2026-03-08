#!/usr/bin/env python3
"""
模型训练脚本 - 训练哭声分类 CNN 模型
🦞 虾虾开发

用法:
    python train_model.py --data_dir ../data/features --epochs 50 --batch_size 32
"""

import argparse
import os
import sys
from pathlib import Path
import numpy as np
import json

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from models.cry_classifier import create_model, compile_model, export_to_tflite, CLASS_NAMES


def load_features(data_dir):
    """
    加载提取的特征
    
    Returns:
        X: 特征数组 (samples, 128, 128, 1)
        y: 标签数组 (samples,)
    """
    print(f"📂 加载特征数据：{data_dir}")
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"特征目录不存在：{data_path}")
    
    # 类别顺序
    class_names = ['hungry', 'sleepy', 'uncomfortable', 'normal']
    
    X_list = []
    y_list = []
    
    for label_idx, class_name in enumerate(class_names):
        class_dir = data_path / class_name
        if not class_dir.exists():
            print(f"⚠️  跳过不存在的类别：{class_name}")
            continue
        
        npy_files = list(class_dir.glob('*.npy'))
        print(f"   {class_name}: {len(npy_files)} 个样本")
        
        for npy_file in npy_files:
            feature = np.load(npy_file)
            X_list.append(feature)
            y_list.append(label_idx)
    
    X = np.array(X_list)
    y = np.array(y_list)
    
    # 添加通道维度 (batch, 128, 128) -> (batch, 128, 128, 1)
    X = np.expand_dims(X, axis=-1)
    
    print(f"\n✅ 加载完成：{X.shape[0]} 个样本，形状 {X.shape}")
    
    return X, y


def train_model(data_dir, output_dir, epochs=50, batch_size=32, val_split=0.2):
    """
    训练模型
    
    Args:
        data_dir: 特征数据目录
        output_dir: 模型输出目录
        epochs: 训练轮数
        batch_size: 批次大小
        val_split: 验证集比例
    """
    import tensorflow as tf
    from tensorflow import keras
    
    print("🦞 模型训练工具")
    print("=" * 60)
    print(f"📊 数据目录：{data_dir}")
    print(f"💾 输出目录：{output_dir}")
    print(f"📈 Epochs: {epochs}")
    print(f"📦 Batch size: {batch_size}")
    print(f"🔀 验证集比例：{val_split}")
    print("=" * 60)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    X, y = load_features(data_dir)
    
    # 打乱数据
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    # 划分训练集和验证集
    val_size = int(len(X) * val_split)
    X_train, X_val = X[val_size:], X[:val_size]
    y_train, y_val = y[val_size:], y[:val_size]
    
    print(f"\n📊 数据集划分:")
    print(f"   训练集：{len(X_train)} 个样本")
    print(f"   验证集：{len(X_val)} 个样本")
    
    # 标签转换为 one-hot
    num_classes = len(CLASS_NAMES)
    y_train_cat = keras.utils.to_categorical(y_train, num_classes)
    y_val_cat = keras.utils.to_categorical(y_val, num_classes)
    
    # 创建模型
    print("\n🏗️  创建模型...")
    model = create_model()
    model = compile_model(model, learning_rate=0.001)
    model.summary()
    
    # 回调函数
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
    
    # 数据增强
    data_augmentation = keras.Sequential([
        keras.layers.RandomFlip("horizontal", input_shape=(128, 128, 1)),
        keras.layers.RandomRotation(0.05),
        keras.layers.RandomZoom(0.1),
    ], name="data_augmentation")
    
    # 训练
    print("\n🚀 开始训练...")
    history = model.fit(
        X_train, y_train_cat,
        validation_data=(X_val, y_val_cat),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks
    )
    
    # 评估
    print("\n📊 评估模型...")
    test_loss, test_acc, test_prec, test_rec = model.evaluate(X_val, y_val_cat, verbose=0)
    print(f"\n✅ 验证集结果:")
    print(f"   准确率：{test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"   精确率：{test_prec:.4f}")
    print(f"   召回率：{test_rec:.4f}")
    
    # 保存最终模型
    model.save(output_path / 'final_model.h5')
    print(f"\n💾 模型已保存：{output_path / 'final_model.h5'}")
    
    # 导出到 TFLite
    print("\n📱 导出 TensorFlow Lite 模型...")
    export_to_tflite(model, str(output_path / 'cry_classifier.tflite'))
    
    # 保存训练历史
    import pickle
    with open(output_path / 'training_history.pkl', 'wb') as f:
        pickle.dump(history.history, f)
    
    # 保存训练报告
    report = {
        'final_accuracy': float(test_acc),
        'final_precision': float(test_prec),
        'final_recall': float(test_rec),
        'epochs_trained': len(history.history['loss']),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'model_config': {
            'input_shape': (128, 128, 1),
            'num_classes': num_classes,
            'class_names': CLASS_NAMES,
        }
    }
    
    with open(output_path / 'training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 训练报告：{output_path / 'training_report.json'}")
    print("\n🎉 训练完成!")
    
    return model, history


def main():
    parser = argparse.ArgumentParser(description='训练哭声分类模型')
    parser.add_argument('--data_dir', type=str, default='../data/features',
                        help='特征数据目录')
    parser.add_argument('--output_dir', type=str, default='../models',
                        help='模型输出目录')
    parser.add_argument('--epochs', type=int, default=50,
                        help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='批次大小')
    parser.add_argument('--val_split', type=float, default=0.2,
                        help='验证集比例')
    args = parser.parse_args()
    
    train_model(
        args.data_dir,
        args.output_dir,
        args.epochs,
        args.batch_size,
        args.val_split
    )


if __name__ == '__main__':
    # 设置 GPU 内存增长
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✅ 检测到 {len(gpus)} 个 GPU，已启用内存增长")
        except RuntimeError as e:
            print(f"⚠️  GPU 配置警告：{e}")
    
    main()
