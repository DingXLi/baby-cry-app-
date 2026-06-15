#!/usr/bin/env python3
"""
生成合成婴儿哭声 WAV 文件 - 用于测试管线
🦞 虾虾开发

每类哭声有不同的频谱特征（参考文献）：
- hungry:        低频周期性，基频 ~350 Hz，强谐波
- sleepy:        低频，衰减慢，能量低
- uncomfortable: 高频尖锐，不规则，基频 ~550 Hz
- normal:        中频，均衡，规律

用法:
    python generate_synthetic_audio.py --output_dir ../data/raw --samples_per_class 50
"""

import argparse
from pathlib import Path
import numpy as np
import soundfile as sf

SAMPLE_RATE = 16000
DURATION    = 5.0
CLASSES     = ['hungry', 'sleepy', 'uncomfortable', 'normal']


def make_cry_signal(cry_type: str, sr: int, duration: float, rng) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    if cry_type == 'hungry':
        f0 = 350 + rng.uniform(-30, 30)
        signal = (
            0.6 * np.sin(2 * np.pi * f0 * t) +
            0.3 * np.sin(2 * np.pi * 2 * f0 * t) +
            0.1 * np.sin(2 * np.pi * 3 * f0 * t)
        )
        # 添加周期振幅调制（模拟哭泣节奏）
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 2 * t)
        signal *= modulation
        noise = rng.normal(0, 0.02, len(t))

    elif cry_type == 'sleepy':
        f0 = 250 + rng.uniform(-20, 20)
        signal = 0.3 * np.sin(2 * np.pi * f0 * t)
        # 缓慢衰减
        envelope = np.exp(-t * 0.3)
        signal *= envelope
        noise = rng.normal(0, 0.01, len(t))

    elif cry_type == 'uncomfortable':
        f0 = 550 + rng.uniform(-50, 50)
        signal = (
            0.5 * np.sin(2 * np.pi * f0 * t) +
            0.3 * np.sin(2 * np.pi * 1.5 * f0 * t) +  # 非谐波分量
            0.2 * np.sin(2 * np.pi * 2.3 * f0 * t)
        )
        # 不规则振幅
        modulation = 1 + 0.4 * rng.uniform(-1, 1, len(t))
        signal *= modulation
        noise = rng.normal(0, 0.05, len(t))

    else:  # normal
        f0 = 400 + rng.uniform(-40, 40)
        signal = (
            0.5 * np.sin(2 * np.pi * f0 * t) +
            0.2 * np.sin(2 * np.pi * 2 * f0 * t)
        )
        modulation = 0.7 + 0.3 * np.sin(2 * np.pi * 1.5 * t)
        signal *= modulation
        noise = rng.normal(0, 0.03, len(t))

    raw = signal + noise
    # 归一化到 [-1, 1]
    peak = np.abs(raw).max()
    return (raw / (peak + 1e-8) * 0.9).astype(np.float32)


def generate(output_dir: str, samples_per_class: int = 50, seed: int = 42):
    rng = np.random.default_rng(seed)
    out = Path(output_dir)

    print(f"🦞 生成合成音频：{samples_per_class} 个/类 → {out}")
    for cls in CLASSES:
        cls_dir = out / cls
        cls_dir.mkdir(parents=True, exist_ok=True)
        for i in range(samples_per_class):
            signal = make_cry_signal(cls, SAMPLE_RATE, DURATION, rng)
            path   = cls_dir / f'{cls}_{i:04d}.wav'
            sf.write(str(path), signal, SAMPLE_RATE)
        print(f"   ✅ {cls}: {samples_per_class} 个 WAV 文件")

    total = len(CLASSES) * samples_per_class
    print(f"\n✅ 总计 {total} 个音频文件")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir',       default='../data/raw')
    parser.add_argument('--samples_per_class', type=int, default=50)
    parser.add_argument('--seed',              type=int, default=42)
    args = parser.parse_args()
    generate(args.output_dir, args.samples_per_class, args.seed)
