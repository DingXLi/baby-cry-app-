/**
 * 纯 JS GradientBoosting 推理引擎
 * 无需 ONNX Runtime 原生模块，完全兼容 Expo managed workflow
 * 🦞 虾虾开发
 *
 * 推理流程：
 *   1. StandardScaler 归一化特征
 *   2. 遍历每棵决策树，累积每个类别的原始得分
 *   3. Softmax 得到概率分布
 */

const MODEL_ASSET = require('../../assets/model.json');

// ─── 决策树遍历 ───────────────────────────────────────────────────────────────

function traverseTree(node, features) {
  if (node.v !== undefined) {
    return node.v[0]; // 叶节点：返回回归值
  }
  return features[node.f] <= node.t
    ? traverseTree(node.l, features)
    : traverseTree(node.r, features);
}

// ─── Softmax ──────────────────────────────────────────────────────────────────

function softmax(logits) {
  const max = Math.max(...logits);
  const exp = logits.map((x) => Math.exp(x - max));
  const sum = exp.reduce((a, b) => a + b, 0);
  return exp.map((e) => e / sum);
}

// ─── 主推理类 ─────────────────────────────────────────────────────────────────

class ModelInferenceClass {
  constructor() {
    this._model = null;
    this._ready = false;
  }

  async initialize() {
    if (this._ready) return true;
    try {
      this._model = MODEL_ASSET;
      this._ready = true;
      console.log(
        `🦞 JS 推理引擎加载完成：${this._model.n_estimators} 棵树 × ${this._model.n_classes} 类`
      );
      return true;
    } catch (e) {
      console.error('ModelInference init failed:', e);
      return false;
    }
  }

  /**
   * 对 168 维特征向量进行推理
   * @param {number[]} rawFeatures - 长度 168 的特征数组
   * @returns {{ type: string, typeCn: string, confidence: number, probabilities: Object }}
   */
  predict(rawFeatures) {
    if (!this._ready) throw new Error('模型未初始化');

    const { scaler, prior, trees, learning_rate, classes, classes_cn } = this._model;

    // 1. 标准化
    const scaled = rawFeatures.map(
      (v, i) => (v - scaler.mean[i]) / (scaler.std[i] + 1e-8)
    );

    // 2. 累积原始得分（GBT 回归树加和）
    const raw = [...prior];
    for (let e = 0; e < trees.length; e++) {
      for (let c = 0; c < trees[e].length; c++) {
        raw[c] += learning_rate * traverseTree(trees[e][c], scaled);
      }
    }

    // 3. Softmax → 概率
    const probs = softmax(raw);
    const maxIdx = probs.indexOf(Math.max(...probs));

    const probMap = {};
    classes.forEach((cls, i) => { probMap[cls] = probs[i]; });

    return {
      type:         classes[maxIdx],
      typeCn:       classes_cn[classes[maxIdx]],
      confidence:   probs[maxIdx],
      probabilities: probMap,
      source:       'js-inference',
    };
  }

  get isReady() {
    return this._ready;
  }

  get classes() {
    return this._model?.classes ?? [];
  }
}

export const ModelInference = new ModelInferenceClass();
export default ModelInference;
