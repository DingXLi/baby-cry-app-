#!/usr/bin/env python3
"""
分批特征提取 - 避免 OOM
🦞 虾虾开发

用法:
    python extract_batch.py --dataset "Baby Crying Sounds"
"""

import argparse
from pathlib import Path
import numpy as np
import librosa
import gc
import json

RAW_DIR = '/home/liding/.openclaw/workspace/baby-cry-app/ml/data/raw'
OUTPUT_DIR = '/home/liding/.openclaw/workspace/baby-cry-app/ml/data/features_v2'

LABEL_MAPPING = {
    'hungry': ['hungry'],
    'sleepy': ['tired'],
    'uncomfortable': ['belly pain', 'discomfort', 'cold_hot'],
    'normal': ['burping', 'lonely', 'laugh'],
}

SR = 16000
DURATION = 5.0


def extract_features(audio_path):
    """提取 168 维特征"""
    try:
        y, sr = librosa.load(audio_path, sr=SR, duration=DURATION)
        
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta_mean = np.mean(mfcc_delta, axis=1)
        
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
        mfcc_delta2_mean = np.mean(mfcc_delta2, axis=1)
        
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)
        
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        mel_mean = np.mean(mel_db, axis=1)
        
        feature = np.concatenate([mfcc_mean, mfcc_delta_mean, mfcc_delta2_mean, [zcr_mean], mel_mean])
        return feature
    
    except Exception as e:
        return None


def process_dataset(dataset_name):
    """处理单个数据集"""
    print(f"\n{'='*60}")
    print(f"📁 处理数据集：{dataset_name}")
    print(f"{'='*60}")
    
    dataset_dir = Path(RAW_DIR) / dataset_name
    output_path = Path(OUTPUT_DIR)
    
    if not dataset_dir.exists():
        print(f"❌ 数据集不存在：{dataset_dir}")
        return 0
    
    stats = {name: 0 for name in LABEL_MAPPING.keys()}
    total = 0
    success = 0
    
    # 遍历所有类别
    for class_dir in dataset_dir.iterdir():
        if not class_dir.is_dir():
            continue
        
        class_name = class_dir.name
        
        # 找到目标标签
        target_label = None
        for label, sources in LABEL_MAPPING.items():
            if class_name in sources:
                target_label = label
                break
        
        if target_label is None:
            print(f"   ⏭️  跳过：{class_name}")
            continue
        
        # 创建输出目录
        output_class_dir = output_path / target_label
        output_class_dir.mkdir(exist_ok=True)
        
        # 处理音频文件
        audio_files = list(class_dir.glob('*.wav'))
        
        # 跳过已处理的文件
        existing = set(f.stem for f in output_class_dir.glob('*.npy'))
        new_files = [f for f in audio_files if f.stem not in existing]
        
        if len(new_files) == 0:
            print(f"   ✅ {class_name} → {target_label}: 已处理 ({len(audio_files)} 文件)")
            stats[target_label] += len(audio_files)
            total += len(audio_files)
            success += len(audio_files)
            continue
        
        print(f"   📁 {class_name} → {target_label}: 新增 {len(new_files)}/{len(audio_files)} 文件")
        
        # 分批处理（每 50 个文件 GC 一次）
        for i, audio_file in enumerate(new_files):
            feature = extract_features(audio_file)
            
            if feature is not None:
                output_file = output_class_dir / (audio_file.stem + '.npy')
                np.save(output_file, feature)
                success += 1
                stats[target_label] += 1
            
            total += 1
            
            # 每 50 个文件 GC 一次
            if (i + 1) % 50 == 0:
                gc.collect()
                print(f"      处理中：{i+1}/{len(new_files)} (GC)")
        
        gc.collect()
    
    return success, stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='Baby Crying Sounds',
                        choices=['Baby Cry Dataset', 'Baby Crying Sounds'])
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🦞 分批特征提取")
    print("=" * 60)
    print(f"📂 输出：{OUTPUT_DIR}")
    print("=" * 60)
    
    success, stats = process_dataset(args.dataset)
    
    print("\n" + "=" * 60)
    print("✅ 完成!")
    print("=" * 60)
    print(f"📊 新增：{success} 样本")
    print(f"\n📈 累计分布:")
    
    # 统计总数
    output_path = Path(OUTPUT_DIR)
    total_stats = {}
    for name in LABEL_MAPPING.keys():
        count = len(list((output_path / name).glob('*.npy')))
        total_stats[name] = count
        print(f"   {name}: {count} 样本")
    
    print(f"\n   总计：{sum(total_stats.values())} 样本")
    
    # 保存信息
    info = {
        'total_samples': sum(total_stats.values()),
        'new_samples': success,
        'class_distribution': total_stats,
        'feature_dim': 168
    }
    
    with open(output_path / 'feature_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n📄 信息：{output_path / 'feature_info.json'}")


if __name__ == '__main__':
    main()
