#!/usr/bin/env python3
"""
特征提取脚本 - 从音频提取 Mel 频谱图
🦞 虾虾开发

用法:
    python extract_features.py --input_dir ../data/prepared --output_dir ../data/features
"""

import argparse
import os
from pathlib import Path
import numpy as np
import librosa
import matplotlib.pyplot as plt
from tqdm import tqdm


# 特征提取配置
CONFIG = {
    'sr': 16000,          # 采样率
    'n_mels': 128,        # Mel 频带数
    'hop_length': 512,    # 跳帧长度
    'n_fft': 2048,        # FFT 窗口大小
    'fmin': 0,            # 最小频率
    'fmax': 8000,         # 最大频率 (婴儿哭声主要频率范围)
}


def extract_mel_spectrogram(audio_path, config=CONFIG):
    """
    从音频文件提取 Mel 频谱图
    
    Args:
        audio_path: 音频文件路径
        config: 特征提取配置
    
    Returns:
        mel_spec: Mel 频谱图 (128 x time)
    """
    try:
        # 加载音频
        y, sr = librosa.load(audio_path, sr=config['sr'])
        
        # 提取 Mel 频谱图
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=config['n_mels'],
            hop_length=config['hop_length'],
            n_fft=config['n_fft'],
            fmin=config['fmin'],
            fmax=config['fmax']
        )
        
        # 转换为分贝刻度
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        return mel_spec_db
    
    except Exception as e:
        print(f"❌ 提取失败 {audio_path}: {e}")
        return None


def resize_to_fixed(mel_spec, target_width=128):
    """
    将 Mel 频谱图调整为固定宽度
    
    Args:
        mel_spec: Mel 频谱图 (128 x time)
        target_width: 目标宽度
    
    Returns:
        resized: 调整后的频谱图 (128 x target_width)
    """
    from scipy.ndimage import zoom
    
    current_height, current_width = mel_spec.shape
    zoom_factor = target_width / current_width
    
    # 只调整时间轴
    resized = zoom(mel_spec, (1, zoom_factor), order=1)
    
    # 确保宽度正确
    if resized.shape[1] > target_width:
        resized = resized[:, :target_width]
    elif resized.shape[1] < target_width:
        # 填充
        pad_width = target_width - resized.shape[1]
        resized = np.pad(resized, ((0, 0), (0, pad_width)), mode='edge')
    
    return resized


def extract_all_features(input_dir, output_dir):
    """
    批量提取所有音频的特征
    
    Args:
        input_dir: 输入目录 (prepared)
        output_dir: 输出目录 (features)
    """
    print("🦞 特征提取工具")
    print("=" * 60)
    print(f"📂 输入目录：{input_dir}")
    print(f"📂 输出目录：{output_dir}")
    print(f"🎯 配置：n_mels={CONFIG['n_mels']}, sr={CONFIG['sr']}Hz")
    print("=" * 60)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ 输入目录不存在：{input_path}")
        return
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 类别映射
    class_names = ['hungry', 'sleepy', 'uncomfortable', 'normal']
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}
    
    # 收集所有音频文件
    audio_files = []
    for class_name in class_names:
        class_dir = input_path / class_name
        if class_dir.exists():
            for audio_file in class_dir.glob('*.wav'):
                audio_files.append((audio_file, class_name))
    
    print(f"\n📊 找到 {len(audio_files)} 个音频文件")
    print("🚀 开始提取特征...\n")
    
    # 统计
    success_count = 0
    fail_count = 0
    features = []
    labels = []
    
    # 提取特征
    for audio_file, class_name in tqdm(audio_files, desc="提取中"):
        # 提取 Mel 频谱图
        mel_spec = extract_mel_spectrogram(audio_file)
        
        if mel_spec is None:
            fail_count += 1
            continue
        
        # 调整为固定大小
        mel_spec_fixed = resize_to_fixed(mel_spec, target_width=128)
        
        # 保存特征
        class_output_dir = output_path / class_name
        class_output_dir.mkdir(exist_ok=True)
        
        output_file = class_output_dir / (audio_file.stem + '.npy')
        np.save(output_file, mel_spec_fixed)
        
        features.append(mel_spec_fixed)
        labels.append(class_to_idx[class_name])
        success_count += 1
    
    # 保存数据集信息
    import json
    dataset_info = {
        'total_samples': success_count,
        'failed_samples': fail_count,
        'class_distribution': {
            name: sum(1 for l in labels if l == idx)
            for name, idx in class_to_idx.items()
        },
        'config': CONFIG,
        'feature_shape': (CONFIG['n_mels'], 128),
    }
    
    with open(output_path / 'dataset_info.json', 'w') as f:
        json.dump(dataset_info, f, indent=2, ensure_ascii=False)
    
    # 输出统计
    print("\n" + "=" * 60)
    print("✅ 特征提取完成!")
    print("=" * 60)
    print(f"\n📊 统计:")
    print(f"   成功：{success_count} 个文件")
    print(f"   失败：{fail_count} 个文件")
    print(f"\n📈 类别分布:")
    for name, idx in class_to_idx.items():
        count = sum(1 for l in labels if l == idx)
        print(f"   {name}: {count} 个样本")
    print(f"\n🔢 特征形状：{CONFIG['n_mels']} x 128")
    print(f"\n📂 输出目录：{output_path}")
    
    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(description='提取音频特征')
    parser.add_argument('--input_dir', type=str, default='../data/prepared',
                        help='输入目录')
    parser.add_argument('--output_dir', type=str, default='../data/features',
                        help='输出目录')
    args = parser.parse_args()
    
    extract_all_features(args.input_dir, args.output_dir)


if __name__ == '__main__':
    main()
