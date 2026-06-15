#!/usr/bin/env python3
"""
合成数据生成器 - 生成类别可区分的 MFCC 特征用于测试管线
🦞 虾虾开发

不同哭声类型的频谱特征来自婴儿哭声研究文献：
- hungry：低频周期性强，能量集中在 300-800 Hz
- sleepy：衰减平缓，高频成分少
- uncomfortable：高频尖锐成分多，不规则性强
- normal：能量均衡，规则周期

用法:
    python generate_synthetic_data.py --output_dir ../data/features --samples_per_class 200
"""

import argparse
import numpy as np
from pathlib import Path

CLASSES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
N_MFCC = 40
N_FRAMES = 128
FEATURE_DIM = N_MFCC * 3  # MFCC + delta + delta2 = 120 features per frame → mean+std = 240; 这里用 168


def generate_mfcc_features(cry_type: str, n_samples: int, seed: int = 42) -> np.ndarray:
    """
    生成类型特异性 MFCC 特征向量 (168 维)
    每个样本 = [MFCC_mean(40) | MFCC_std(40) | delta_mean(40) | delta_std(40) | spectral_features(8)]
    """
    rng = np.random.default_rng(seed)
    samples = []

    for _ in range(n_samples):
        noise = rng.standard_normal(168) * 0.15

        if cry_type == 'hungry':
            # 周期性强，低频集中
            base = np.zeros(168)
            base[:10] = rng.uniform(8, 14, 10)    # 低频 MFCC 高
            base[10:20] = rng.uniform(2, 6, 10)
            base[20:40] = rng.uniform(-3, 2, 20)  # 高频衰减
            base[40:80] = base[:40] * 0.6 + rng.standard_normal(40) * 0.3  # std
            base[80:120] = rng.uniform(1, 4, 40)  # delta 平稳（周期性）
            base[120:160] = rng.uniform(-1, 1, 40) * 0.5
            base[160:168] = [0.7, 0.3, 0.8, 0.2, 0.6, 120, 0.9, 0.4]  # spectral

        elif cry_type == 'sleepy':
            # 衰减平缓，能量低
            base = np.zeros(168)
            base[:10] = rng.uniform(2, 6, 10)     # 整体能量低
            base[10:40] = rng.uniform(-2, 3, 30)
            base[40:80] = base[:40] * 0.4 + rng.standard_normal(40) * 0.2
            base[80:120] = rng.uniform(-1, 1, 40) * 0.3  # delta 极小（衰减）
            base[120:160] = rng.uniform(-0.5, 0.5, 40) * 0.2
            base[160:168] = [0.3, 0.7, 0.2, 0.5, 0.2, 80, 0.4, 0.6]

        elif cry_type == 'uncomfortable':
            # 高频多，不规则，尖锐
            base = np.zeros(168)
            base[:5] = rng.uniform(4, 8, 5)
            base[5:25] = rng.uniform(3, 9, 20)    # 高频 MFCC 高
            base[25:40] = rng.uniform(2, 7, 15)
            base[40:80] = base[:40] * 0.8 + rng.standard_normal(40) * 0.5  # std 大（不规则）
            base[80:120] = rng.uniform(-5, 5, 40)  # delta 剧烈变化
            base[120:160] = rng.uniform(-3, 3, 40)
            base[160:168] = [0.9, 0.1, 0.7, 0.8, 0.9, 200, 0.6, 0.2]

        else:  # normal
            # 均衡，规则
            base = np.zeros(168)
            base[:10] = rng.uniform(5, 9, 10)
            base[10:20] = rng.uniform(2, 5, 10)
            base[20:40] = rng.uniform(0, 3, 20)
            base[40:80] = base[:40] * 0.5 + rng.standard_normal(40) * 0.25
            base[80:120] = rng.uniform(-2, 2, 40)
            base[120:160] = rng.uniform(-1, 1, 40) * 0.4
            base[160:168] = [0.5, 0.5, 0.5, 0.4, 0.5, 150, 0.7, 0.5]

        samples.append(base + noise)

    return np.array(samples, dtype=np.float32)


def generate_dataset(output_dir: str, samples_per_class: int = 200, seed: int = 42):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"🦞 合成数据生成器")
    print(f"   输出目录：{out}")
    print(f"   每类样本数：{samples_per_class}")

    all_X, all_y = [], []

    for label_idx, cls in enumerate(CLASSES):
        cls_dir = out / cls
        cls_dir.mkdir(exist_ok=True)

        features = generate_mfcc_features(cls, samples_per_class, seed=seed + label_idx)

        for i, feat in enumerate(features):
            np.save(cls_dir / f'{cls}_{i:04d}.npy', feat)

        all_X.append(features)
        all_y.extend([label_idx] * samples_per_class)
        print(f"   ✅ {cls}: {samples_per_class} 个样本")

    X = np.vstack(all_X)
    y = np.array(all_y)

    # 保存合并数据集
    np.save(out / 'X.npy', X)
    np.save(out / 'y.npy', y)

    print(f"\n✅ 总计 {len(X)} 个样本，形状 {X.shape}")
    print(f"   已保存到 {out}")
    return X, y


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', default='../data/features')
    parser.add_argument('--samples_per_class', type=int, default=200)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    generate_dataset(args.output_dir, args.samples_per_class, args.seed)
