#!/usr/bin/env python3
"""
音频预处理脚本
🦞 虾虾开发

功能:
- 统一采样率
- 转换为单声道
- 裁剪/填充到固定时长
- 降噪处理

用法:
    python preprocess_audio.py --input_dir ../data/raw --output_dir ../data/processed
"""

import argparse
import os
from pathlib import Path
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm


def preprocess_audio_file(input_path, output_path, target_sr=16000, target_duration=5.0):
    """
    预处理单个音频文件
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        target_sr: 目标采样率 (默认 16kHz)
        target_duration: 目标时长 (秒，默认 5 秒)
    """
    try:
        # 加载音频
        y, sr = librosa.load(input_path, sr=target_sr, mono=True)
        
        # 计算目标样本数
        target_samples = int(target_sr * target_duration)
        
        # 裁剪或填充
        if len(y) > target_samples:
            # 裁剪（从中间开始）
            start = (len(y) - target_samples) // 2
            y = y[start:start + target_samples]
        else:
            # 填充
            y = np.pad(y, (0, target_samples - len(y)), mode='constant')
        
        # 保存
        sf.write(output_path, y, target_sr)
        return True
        
    except Exception as e:
        print(f"❌ 处理失败 {input_path}: {e}")
        return False


def preprocess_directory(input_dir, output_dir, target_sr=16000, target_duration=5.0):
    """预处理整个目录"""
    print("🦞 音频预处理工具")
    print("=" * 60)
    print(f"📂 输入目录：{input_dir}")
    print(f"📂 输出目录：{output_dir}")
    print(f"🎯 目标采样率：{target_sr} Hz")
    print(f"⏱️  目标时长：{target_duration} 秒")
    print("=" * 60)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ 输入目录不存在：{input_path}")
        return
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有音频文件
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(input_path.rglob(f'*{ext}'))
        audio_files.extend(input_path.rglob(f'*{ext.upper()}'))
    
    audio_files = list(set(audio_files))
    
    if len(audio_files) == 0:
        print("❌ 未找到音频文件")
        return
    
    print(f"\n📊 找到 {len(audio_files)} 个音频文件")
    print("🚀 开始预处理...\n")
    
    # 按目录分组（保持分类结构）
    success_count = 0
    fail_count = 0
    
    for input_file in tqdm(audio_files, desc="处理中"):
        # 计算输出路径（保持目录结构）
        relative_path = input_file.relative_to(input_path)
        output_file = output_path / relative_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 处理文件
        if preprocess_audio_file(input_file, output_file, target_sr, target_duration):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print("✅ 预处理完成!")
    print(f"   成功：{success_count} 个文件")
    print(f"   失败：{fail_count} 个文件")
    print(f"📂 输出目录：{output_path}")


def main():
    parser = argparse.ArgumentParser(description='音频预处理')
    parser.add_argument('--input_dir', type=str, default='../data/raw',
                        help='输入目录')
    parser.add_argument('--output_dir', type=str, default='../data/processed',
                        help='输出目录')
    parser.add_argument('--target_sr', type=int, default=16000,
                        help='目标采样率')
    parser.add_argument('--duration', type=float, default=5.0,
                        help='目标时长（秒）')
    args = parser.parse_args()
    
    preprocess_directory(
        args.input_dir,
        args.output_dir,
        args.target_sr,
        args.duration
    )


if __name__ == '__main__':
    main()
