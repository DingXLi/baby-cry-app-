#!/usr/bin/env python3
"""
数据集准备脚本 - 整理目录结构并映射标签
🦞 虾虾开发

用法:
    python prepare_dataset.py --raw_dir ../data/raw --output_dir ../data/prepared
"""

import argparse
import shutil
from pathlib import Path
import os


# 标签映射配置
LABEL_MAPPING = {
    'hungry': ['hungry'],
    'sleepy': ['tired'],
    'uncomfortable': ['belly pain', 'discomfort', 'cold_hot'],
    'normal': ['burping', 'lonely', 'laugh'],
}

# 要跳过的目录
SKIP_DIRS = ['noise', 'silence', 'scared']


def prepare_dataset(raw_dir, output_dir):
    """准备数据集"""
    print("🦞 数据集准备工具")
    print("=" * 60)
    print(f"📂 原始数据目录：{raw_dir}")
    print(f"📂 输出目录：{output_dir}")
    print("=" * 60)
    
    raw_path = Path(raw_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建 4 类分类目录
    for label in LABEL_MAPPING.keys():
        (output_path / label).mkdir(exist_ok=True)
    
    # 统计
    stats = {label: 0 for label in LABEL_MAPPING.keys()}
    total_files = 0
    skipped_files = 0
    
    # 处理两个数据集
    dataset_dirs = [
        raw_path / 'Baby Cry Dataset',
        raw_path / 'Baby Crying Sounds',
    ]
    
    for dataset_dir in dataset_dirs:
        if not dataset_dir.exists():
            print(f"⚠️  跳过不存在的目录：{dataset_dir}")
            continue
        
        print(f"\n📁 处理数据集：{dataset_dir.name}")
        
        # 遍历所有类别目录
        for class_dir in dataset_dir.iterdir():
            if not class_dir.is_dir():
                continue
            
            class_name = class_dir.name
            
            # 检查是否要跳过
            if class_name in SKIP_DIRS:
                skipped = len(list(class_dir.glob('*.wav')))
                skipped_files += skipped
                print(f"   ⏭️  跳过：{class_name} ({skipped} 个文件)")
                continue
            
            # 找到目标标签
            target_label = None
            for label, sources in LABEL_MAPPING.items():
                if class_name in sources:
                    target_label = label
                    break
            
            if target_label is None:
                print(f"   ⚠️  未知类别：{class_name}")
                continue
            
            # 复制文件
            wav_files = list(class_dir.glob('*.wav'))
            for i, wav_file in enumerate(wav_files):
                # 重命名文件（避免冲突）
                new_name = f"{class_name}_{dataset_dir.name.replace(' ', '_')}_{i:04d}.wav"
                dest_file = output_path / target_label / new_name
                
                shutil.copy2(wav_file, dest_file)
                stats[target_label] += 1
                total_files += 1
            
            print(f"   ✅ {class_name} → {target_label} ({len(wav_files)} 个文件)")
    
    # 输出统计
    print("\n" + "=" * 60)
    print("✅ 数据集准备完成!")
    print("=" * 60)
    print(f"\n📊 分类统计:")
    for label, count in stats.items():
        print(f"   {label}: {count} 个文件")
    
    print(f"\n📈 总计:")
    print(f"   已复制：{total_files} 个文件")
    print(f"   已跳过：{skipped_files} 个文件 ({', '.join(SKIP_DIRS)})")
    print(f"\n📂 输出目录：{output_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='准备数据集')
    parser.add_argument('--raw_dir', type=str, default='../data/raw',
                        help='原始数据目录')
    parser.add_argument('--output_dir', type=str, default='../data/prepared',
                        help='输出目录')
    args = parser.parse_args()
    
    prepare_dataset(args.raw_dir, args.output_dir)


if __name__ == '__main__':
    main()
