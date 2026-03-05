#!/usr/bin/env python3
"""
数据集探索脚本
🦞 虾虾开发

用法:
    python explore_data.py --data_dir ../data/raw
"""

import argparse
import os
from pathlib import Path
from collections import defaultdict
import json


def explore_directory(data_dir):
    """探索数据目录结构"""
    print("🦞 数据集探索工具")
    print("=" * 60)
    print(f"📂 数据目录：{data_dir}")
    print("=" * 60)
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"❌ 目录不存在：{data_path}")
        print("\n💡 提示:")
        print("   1. 从 Kaggle 下载数据集")
        print("   2. 解压到 ml/data/raw/ 目录")
        print("   3. 重新运行此脚本")
        return None
    
    # 查找所有音频文件
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(data_path.rglob(f'*{ext}'))
        audio_files.extend(data_path.rglob(f'*{ext.upper()}'))
    
    audio_files = list(set(audio_files))  # 去重
    
    print(f"\n📊 数据集统计")
    print("-" * 60)
    print(f"🎵 音频文件总数：{len(audio_files)}")
    
    if len(audio_files) == 0:
        print("\n❌ 未找到音频文件")
        print("\n💡 提示:")
        print("   检查文件扩展名是否为：wav, mp3, flac, ogg, m4a, aac")
        return None
    
    # 按目录统计
    dir_stats = defaultdict(list)
    for file in audio_files:
        dir_stats[file.parent.name].append(file)
    
    print(f"\n📁 目录分布:")
    for dir_name, files in sorted(dir_stats.items()):
        print(f"   {dir_name}: {len(files)} 个文件")
    
    # 文件扩展名统计
    ext_stats = defaultdict(int)
    for file in audio_files:
        ext_stats[file.suffix.lower()] += 1
    
    print(f"\n📄 文件格式分布:")
    for ext, count in sorted(ext_stats.items(), key=lambda x: -x[1]):
        print(f"   {ext}: {count} 个文件")
    
    # 文件大小统计
    sizes = [file.stat().st_size for file in audio_files]
    total_size = sum(sizes)
    avg_size = total_size / len(sizes) if sizes else 0
    
    print(f"\n💾 文件大小:")
    print(f"   总大小：{total_size / 1024 / 1024:.2f} MB")
    print(f"   平均大小：{avg_size / 1024:.2f} KB")
    print(f"   最小：{min(sizes) / 1024:.2f} KB")
    print(f"   最大：{max(sizes) / 1024:.2f} KB")
    
    # 尝试推断分类标签
    print(f"\n🏷️  推测分类标签:")
    label_keywords = {
        'hungry': ['hungry', 'hunger', 'feeding', 'feed'],
        'sleepy': ['sleepy', 'tired', 'sleep', 'bed'],
        'uncomfortable': ['pain', 'discomfort', 'sick', 'hurt'],
        'normal': ['normal', 'neutral', 'baseline', 'happy'],
    }
    
    for label, keywords in label_keywords.items():
        matching_dirs = [
            dir_name for dir_name in dir_stats.keys()
            if any(kw in dir_name.lower() for kw in keywords)
        ]
        if matching_dirs:
            print(f"   {label}: {', '.join(matching_dirs)}")
    
    # 保存统计信息
    stats = {
        'total_files': len(audio_files),
        'total_size_mb': total_size / 1024 / 1024,
        'directories': {k: len(v) for k, v in dir_stats.items()},
        'formats': dict(ext_stats),
    }
    
    output_path = data_path.parent / 'metadata' / 'dataset_stats.json'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 统计信息已保存：{output_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='探索数据集')
    parser.add_argument('--data_dir', type=str, default='../data/raw',
                        help='数据目录路径')
    args = parser.parse_args()
    
    explore_directory(args.data_dir)


if __name__ == '__main__':
    main()
