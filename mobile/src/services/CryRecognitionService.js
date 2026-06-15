/**
 * 哭声识别服务
 * 当前使用时间感知的模拟推理（等待真实 ONNX 模型集成）
 */

const CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal'];
const CLASS_NAMES_CN = {
  hungry: '饿了',
  sleepy: '困了',
  uncomfortable: '不舒服',
  normal: '正常',
};

// 根据当前小时返回先验概率权重
function getTimeBasedPriors(hour) {
  if (hour >= 22 || hour < 5) {
    // 深夜：困了更多，正常少
    return [0.30, 0.45, 0.15, 0.10];
  } else if (hour >= 5 && hour < 8) {
    // 清晨：饿了高
    return [0.50, 0.20, 0.15, 0.15];
  } else if (hour >= 11 && hour < 14) {
    // 午饭时段：饿了高
    return [0.45, 0.15, 0.20, 0.20];
  } else if (hour >= 14 && hour < 16) {
    // 午睡时段：困了高
    return [0.20, 0.40, 0.20, 0.20];
  } else {
    // 其他时段
    return [0.35, 0.20, 0.25, 0.20];
  }
}

// Dirichlet-like softmax with noise to simulate inference variance
function sampleProbabilities(priors) {
  const noisy = priors.map((p) => p + (Math.random() - 0.5) * 0.15);
  const clamped = noisy.map((v) => Math.max(0.01, v));
  const sum = clamped.reduce((a, b) => a + b, 0);
  return clamped.map((v) => v / sum);
}

class CryRecognitionServiceClass {
  constructor() {
    this.initialized = false;
    this.inferenceCount = 0;
  }

  async initialize() {
    if (this.initialized) return true;
    // Future: load ONNX model from assets
    console.log('🦞 哭声识别服务已初始化（模拟模式）');
    this.initialized = true;
    return true;
  }

  /**
   * 从音频 URI 提取特征
   * Future: 实现 Mel 频谱提取 (librosa-js / expo-av + FFT)
   */
  async extractFeatures(audioUri) {
    // Placeholder — returns a synthetic feature vector
    const features = new Float32Array(168);
    for (let i = 0; i < features.length; i++) {
      features[i] = Math.random() * 2 - 1;
    }
    return features;
  }

  /**
   * 推理：根据时间感知先验 + 噪声模拟输出概率
   */
  async predict(features) {
    if (!this.initialized) await this.initialize();

    const hour = new Date().getHours();
    const priors = getTimeBasedPriors(hour);
    const probabilities = sampleProbabilities(priors);

    const maxIdx = probabilities.indexOf(Math.max(...probabilities));
    const confidence = probabilities[maxIdx];

    this.inferenceCount++;

    return {
      type: CLASS_NAMES[maxIdx],
      typeCn: CLASS_NAMES_CN[CLASS_NAMES[maxIdx]],
      confidence,
      probabilities: CLASS_NAMES.reduce((acc, name, i) => {
        acc[name] = probabilities[i];
        return acc;
      }, {}),
      timestamp: new Date().toISOString(),
      inferenceId: this.inferenceCount,
    };
  }

  /**
   * 完整流程：音频 → 特征 → 结果
   */
  async recognize(audioUri) {
    const features = await this.extractFeatures(audioUri);
    if (!features) return null;
    return this.predict(features);
  }

  getTypeName(type) {
    return CLASS_NAMES_CN[type] || type;
  }

  getClasses() {
    return CLASS_NAMES.map((name) => ({ name, nameCn: CLASS_NAMES_CN[name] }));
  }
}

export const CryRecognitionService = new CryRecognitionServiceClass();
export default CryRecognitionService;
