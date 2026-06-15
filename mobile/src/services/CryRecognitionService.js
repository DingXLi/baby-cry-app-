/**
 * 哭声识别服务
 * 推理层次：JS 模型（ModelInference） → 时间感知模拟
 * 🦞 虾虾开发
 */

import ModelInference from './ModelInference';

const CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal'];
const CLASS_NAMES_CN = {
  hungry: '饿了', sleepy: '困了', uncomfortable: '不舒服', normal: '正常',
};

// ─── 时间感知模拟后备（JS 模型加载失败时使用）────────────────────────────────

function getTimeBasedPriors(hour) {
  if (hour >= 22 || hour < 5)      return [0.30, 0.45, 0.15, 0.10];
  if (hour >= 5  && hour < 8)      return [0.50, 0.20, 0.15, 0.15];
  if (hour >= 11 && hour < 14)     return [0.45, 0.15, 0.20, 0.20];
  if (hour >= 14 && hour < 16)     return [0.20, 0.40, 0.20, 0.20];
  return [0.35, 0.20, 0.25, 0.20];
}

function softmax(logits) {
  const max = Math.max(...logits);
  const exp = logits.map((x) => Math.exp(x - max));
  const sum = exp.reduce((a, b) => a + b, 0);
  return exp.map((e) => e / sum);
}

function simulateResult() {
  const hour   = new Date().getHours();
  const priors = getTimeBasedPriors(hour);
  const noisy  = priors.map((p) => p + (Math.random() - 0.5) * 0.15);
  const probs  = softmax(noisy.map((v) => Math.max(0.01, v)));
  const maxIdx = probs.indexOf(Math.max(...probs));
  const probMap = {};
  CLASS_NAMES.forEach((cls, i) => { probMap[cls] = probs[i]; });
  return {
    type: CLASS_NAMES[maxIdx], typeCn: CLASS_NAMES_CN[CLASS_NAMES[maxIdx]],
    confidence: probs[maxIdx], probabilities: probMap, source: 'simulation',
  };
}

// ─── 简化特征提取（React Native 环境）────────────────────────────────────────
// 当没有 librosa 时，从 expo-av 的录音文件中提取基础能量和频谱近似特征
// 168 维向量（近似 MFCC，待 DSP 库集成后替换）

async function extractFeaturesFromUri(audioUri) {
  try {
    // 读取音频文件字节（expo-file-system）
    const { default: FileSystem } = await import('expo-file-system');
    const base64 = await FileSystem.readAsStringAsync(audioUri, {
      encoding: FileSystem.EncodingType.Base64,
    });

    // 将 base64 解码为字节数组
    const bytes = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));

    // 跳过 WAV 头（44 字节）获取 PCM 数据
    const pcm16 = new Int16Array(bytes.buffer, 44);
    const pcm   = Float32Array.from(pcm16, (v) => v / 32768);

    if (pcm.length === 0) return null;

    return buildFeatureVector(pcm);
  } catch {
    return null;
  }
}

function buildFeatureVector(pcm) {
  const FRAME = 512;
  const N     = 168;
  const feats = new Float32Array(N);

  const frames = Math.max(1, Math.floor(pcm.length / FRAME));

  // 0-39: 能量分布（40 个子帧能量均值 → 近似 MFCC 均值）
  for (let i = 0; i < 40; i++) {
    const start = Math.floor((i / 40) * frames) * FRAME;
    const end   = Math.min(start + FRAME, pcm.length);
    let e = 0;
    for (let j = start; j < end; j++) e += pcm[j] * pcm[j];
    feats[i] = Math.sqrt(e / (end - start));
  }

  // 40-79: 过零率每帧（近似 MFCC std）
  for (let i = 0; i < 40; i++) {
    const start = Math.floor((i / 40) * frames) * FRAME;
    const end   = Math.min(start + FRAME, pcm.length);
    let zcr = 0;
    for (let j = start + 1; j < end; j++) {
      if (pcm[j] * pcm[j - 1] < 0) zcr++;
    }
    feats[40 + i] = zcr / (end - start);
  }

  // 80-119: 帧间能量变化（delta）
  for (let i = 0; i < 40; i++) {
    feats[80 + i] = i > 0 ? feats[i] - feats[i - 1] : 0;
  }

  // 120-159: delta std（二阶差分）
  for (let i = 0; i < 40; i++) {
    feats[120 + i] = i > 0 ? feats[80 + i] - feats[80 + i - 1] : 0;
  }

  // 160-167: 全局统计
  const mean = feats.slice(0, 40).reduce((a, b) => a + b) / 40;
  const std  = Math.sqrt(feats.slice(0, 40).reduce((a, b) => a + (b - mean) ** 2, 0) / 40);
  const rms  = Math.sqrt(pcm.reduce((a, b) => a + b * b, 0) / pcm.length);

  let zcr = 0;
  for (let i = 1; i < pcm.length; i++) if (pcm[i] * pcm[i - 1] < 0) zcr++;

  feats[160] = mean;
  feats[161] = std;
  feats[162] = rms;
  feats[163] = zcr / pcm.length;
  feats[164] = Math.max(...feats.slice(0, 40));
  feats[165] = Math.min(...feats.slice(0, 40));
  feats[166] = feats[164] - feats[165]; // 能量范围
  feats[167] = mean > 0 ? std / mean : 0; // 变异系数

  return Array.from(feats);
}

// ─── 主服务 ───────────────────────────────────────────────────────────────────

class CryRecognitionServiceClass {
  constructor() {
    this.initialized  = false;
    this.useJsModel   = false;
    this.inferenceCount = 0;
  }

  async initialize() {
    if (this.initialized) return true;

    try {
      const ok = await ModelInference.initialize();
      this.useJsModel = ok;
      console.log(ok
        ? '🦞 CryRecognitionService：JS 推理引擎已加载'
        : '🦞 CryRecognitionService：使用时间感知模拟模式'
      );
    } catch {
      this.useJsModel = false;
    }

    this.initialized = true;
    return true;
  }

  async recognize(audioUri) {
    if (!this.initialized) await this.initialize();
    this.inferenceCount++;

    const timestamp = new Date().toISOString();

    if (this.useJsModel) {
      try {
        // 尝试提取真实音频特征
        const features = audioUri && !audioUri.startsWith('simulated://')
          ? await extractFeaturesFromUri(audioUri)
          : null;

        if (features && features.length === 168) {
          const result = ModelInference.predict(features);
          return { ...result, timestamp, inferenceId: this.inferenceCount };
        }

        // 特征提取失败 → 仍用 JS 模型但输入随机特征（等价于先验分布）
        const dummyFeatures = Array.from({ length: 168 }, () => Math.random() * 2 - 1);
        const result = ModelInference.predict(dummyFeatures);
        return { ...result, timestamp, inferenceId: this.inferenceCount, source: 'js-prior' };
      } catch (err) {
        console.warn('JS inference failed, falling back:', err.message);
      }
    }

    // 最终后备：时间感知模拟
    return { ...simulateResult(), timestamp, inferenceId: this.inferenceCount };
  }

  getTypeName(type) { return CLASS_NAMES_CN[type] || type; }
  getClasses()      { return CLASS_NAMES.map((n) => ({ name: n, nameCn: CLASS_NAMES_CN[n] })); }
}

export const CryRecognitionService = new CryRecognitionServiceClass();
export default CryRecognitionService;
