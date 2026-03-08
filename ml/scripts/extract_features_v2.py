#!/usr/bin/env python3
"""
特征提取 v2 - 从原始音频提取 MFCC+Delta+ZCR 多特征融合
🦞 虾虾开发

用法:
    python extract_features_v2.py
"""

from pathlib import Path
import numpy as np
import librosa
from tqdm import tqdm
import json

# 原始数据目录
RAW_DIR = '/home/liding/.openclaw/workspace/baby-cry-app/ml/data/raw'
OUTPUT_DIR = '/home/liding/.openclaw/workspace/baby-cry-app/ml/data/features_v2'

# 类别映射 (原始标签 → 我们的标签)
LABEL_MAPPING = {
    'hungry': ['hungry'],
    'sleepy': ['tired'],
    'uncomfortable': ['belly pain', 'discomfort', 'cold_hot'],
    'normal': ['burping', 'lonely', 'laugh'],
}

# 音频配置
SR = 16000
DURATION = 5.0


def extract_features(audio_path):
    """提取多特征融合：MFCC(13) + Delta(13) + Delta2(13) + ZCR(1) + Mel(128) = 168 维"""
    try:
        y, sr = librosa.load(audio_path, sr=SR, duration=DURATION)
        
        # MFCC (13 维)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # MFCC Delta (13 维)
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta_mean = np.mean(mfcc_delta, axis=1)
        
        # MFCC Delta2 (13 维)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
        mfcc_delta2_mean = np.mean(mfcc_delta2, axis=1)
        
        # ZCR (1 维)
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)
        
        # Mel 频谱 (128 维)
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        mel_mean = np.mean(mel_db, axis=1)
        
        # 拼接
        feature = np.concatenate([mfcc_mean, mfcc_delta_mean, mfcc_delta2_mean, [zcr_mean], mel_mean])
        
        return feature
    
    except Exception as e:
        return None


def main():
    print("\n" + "=" * 60)
    print("🦞 特征提取 v2 - 多特征融合")
    print("=" * 60)
    print(f"📂 输入：{RAW_DIR}")
    print(f"📂 输出：{OUTPUT_DIR}")
    print(f"🎯 特征：168 维 (MFCC+Delta+ZCR+Mel)")
    print("=" * 60)
    
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 遍历两个数据集
    dataset_dirs = [
        Path(RAW_DIR) / 'Baby Cry Dataset',
        Path(RAW_DIR) / 'Baby Crying Sounds',
    ]
    
    stats = {name: 0 for name in LABEL_MAPPING.keys()}
    total = 0
    success = 0
    failed = 0
    
    for dataset_dir in dataset_dirs:
        if not dataset_dir.exists():
            print(f"\n⚠️  跳过：{dataset_dir.name}")
            continue
        
        print(f"\n📁 处理数据集：{dataset_dir.name}")
        
        # 遍历所有类别目录
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
            print(f"   📁 {class_name} → {target_label}: {len(audio_files)} 个文件")
            
            for audio_file in tqdm(audio_files, desc=f"   {class_name}", leave=False):
                feature = extract_features(audio_file)
                
                if feature is not None:
                    output_file = output_class_dir / (audio_file.stem + '.npy')
                    np.save(output_file, feature)
                    success += 1
                    stats[target_label] += 1
                else:
                    failed += 1
                
                total += 1
    
    print("\n" + "=" * 60)
    print("✅ 特征提取完成!")
    print("=" * 60)
    print(f"📊 成功：{success}/{total} ({success*100/total:.1f}%)")
    print(f"❌ 失败：{failed}")
    print(f"\n📈 类别分布:")
    for name, count in stats.items():
        print(f"   {name}: {count} 样本")
    print(f"\n📂 输出：{OUTPUT_DIR}")
    
    # 保存信息
    info = {
        'total_samples': success,
        'failed_samples': failed,
        'feature_dim': 168,
        'class_distribution': stats,
        'features': {
            'mfcc': 13,
            'mfcc_delta': 13,
            'mfcc_delta2': 13,
            'zcr': 1,
            'mel': 128
        }
    }
    
    with open(output_path / 'feature_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n📄 信息：{output_path / 'feature_info.json'}")


if __name__ == '__main__':
    main()
