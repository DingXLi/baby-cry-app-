#!/usr/bin/env python3
"""
从音频文件提取 MFCC 特征 - 生产级实现
🦞 虾虾开发

输出：168 维特征向量
  [MFCC均值(40) | MFCC标准差(40) | Δ均值(40) | Δ标准差(40) | 频谱统计(8)]

用法:
    python extract_features.py --input_dir ../data/raw --output_dir ../data/features
    python extract_features.py --file path/to/audio.wav --output features.npy
"""

import argparse
from pathlib import Path

import numpy as np
import librosa

SAMPLE_RATE = 16000
DURATION    = 5.0
N_MFCC      = 40
HOP_LENGTH  = 512
N_FFT       = 2048
N_MELS      = 128
FEATURE_DIM = 168

CLASSES = ['hungry', 'sleepy', 'uncomfortable', 'normal']


def extract_features(audio_path: str, sr: int = SAMPLE_RATE,
                     duration: float = DURATION) -> np.ndarray:
    """提取 168 维特征向量"""
    y, _ = librosa.load(audio_path, sr=sr, mono=True, duration=duration)

    target_len = int(sr * duration)
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]

    # MFCC (40 维均值 + 40 维标准差)
    mfcc      = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC,
                                      n_fft=N_FFT, hop_length=HOP_LENGTH,
                                      n_mels=N_MELS)
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_std  = mfcc.std(axis=1)

    # Delta MFCC (40 维均值 + 40 维标准差)
    delta      = librosa.feature.delta(mfcc)
    delta_mean = delta.mean(axis=1)
    delta_std  = delta.std(axis=1)

    # 频谱统计 (8 维)
    spec      = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH))
    centroid  = librosa.feature.spectral_centroid(S=spec, sr=sr).mean()
    bandwidth = librosa.feature.spectral_bandwidth(S=spec, sr=sr).mean()
    rolloff   = librosa.feature.spectral_rolloff(S=spec, sr=sr).mean()
    zcr       = librosa.feature.zero_crossing_rate(y, hop_length=HOP_LENGTH).mean()
    rms       = librosa.feature.rms(y=y, hop_length=HOP_LENGTH).mean()
    chroma    = librosa.feature.chroma_stft(S=spec, sr=sr).mean()
    y_harm, _ = librosa.effects.hpss(y)
    harm_ratio = np.sqrt((y_harm ** 2).mean()) / (np.sqrt((y ** 2).mean()) + 1e-8)
    flatness   = librosa.feature.spectral_flatness(S=spec).mean()

    spectral = np.array(
        [centroid / sr, bandwidth / sr, rolloff / sr, zcr,
         rms, chroma, float(harm_ratio), flatness],
        dtype=np.float32,
    )

    features = np.concatenate(
        [mfcc_mean, mfcc_std, delta_mean, delta_std, spectral]
    ).astype(np.float32)

    assert features.shape == (FEATURE_DIM,), f"维度错误: {features.shape}"
    return features


def extract_from_dir(input_dir: str, output_dir: str, verbose: bool = True):
    """批量从 raw/class_name/*.wav 提取特征到 features/class_name/*.npy"""
    try:
        from tqdm import tqdm
        USE_TQDM = True
    except ImportError:
        USE_TQDM = False

    input_path  = Path(input_dir)
    output_path = Path(output_dir)
    all_X, all_y = [], []

    for label_idx, cls in enumerate(CLASSES):
        cls_in  = input_path / cls
        cls_out = output_path / cls
        cls_out.mkdir(parents=True, exist_ok=True)

        exts = ('*.wav', '*.mp3', '*.m4a', '*.ogg', '*.flac')
        audio_files = sorted(f for ext in exts for f in cls_in.glob(ext))

        if not audio_files:
            if verbose:
                print(f"⚠️  {cls}: 无音频文件")
            continue

        iter_ = tqdm(audio_files, desc=f"  {cls}") if USE_TQDM else audio_files
        ok = 0
        for af in iter_:
            try:
                feat = extract_features(str(af))
                np.save(cls_out / (af.stem + '.npy'), feat)
                all_X.append(feat)
                all_y.append(label_idx)
                ok += 1
            except Exception as e:
                if verbose:
                    print(f"    ⚠️  {af.name}: {e}")

        if verbose:
            print(f"   ✅ {cls}: {ok}/{len(audio_files)}")

    if all_X:
        X, y = np.array(all_X, np.float32), np.array(all_y, np.int64)
        np.save(output_path / 'X.npy', X)
        np.save(output_path / 'y.npy', y)
        if verbose:
            print(f"\n✅ 总计 {len(X)} 个样本，形状 {X.shape}")
        return X, y
    return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir',  default='../data/raw')
    parser.add_argument('--output_dir', default='../data/features')
    parser.add_argument('--file',   help='处理单个音频文件')
    parser.add_argument('--output', help='单文件输出 .npy 路径')
    args = parser.parse_args()

    if args.file:
        feat = extract_features(args.file)
        if args.output:
            np.save(args.output, feat)
            print(f"✅ {args.output}  shape={feat.shape}")
        else:
            print(f"特征形状：{feat.shape}  前10维：{feat[:10]}")
    else:
        extract_from_dir(args.input_dir, args.output_dir)


if __name__ == '__main__':
    main()
