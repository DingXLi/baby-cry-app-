#!/usr/bin/env python3
"""
将训练好的 sklearn Pipeline 导出为 JSON 格式
供 React Native 纯 JS 推理使用（无需 ONNX Runtime 原生模块）
🦞 虾虾开发

导出内容：
  - StandardScaler 的 mean / std
  - GradientBoosting 每棵树的结构（特征索引、阈值、叶节点值）
  - 类别信息和先验概率

用法:
    python export_model_js.py --model_dir ../models --output ../mobile/assets/model.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

CLASSES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
CLASSES_CN = {'hungry': '饿了', 'sleepy': '困了', 'uncomfortable': '不舒服', 'normal': '正常'}


def tree_to_dict(tree_):
    """将 sklearn 决策树内部结构序列化为字典（递归压缩）"""
    n_nodes      = tree_.node_count
    children_l   = tree_.children_left.tolist()
    children_r   = tree_.children_right.tolist()
    features     = tree_.feature.tolist()
    thresholds   = tree_.threshold.tolist()
    # values shape: (n_nodes, n_outputs, max_n_classes)
    values       = tree_.value[:, 0, :].tolist()

    def recurse(node_id):
        if children_l[node_id] == -1:  # leaf
            return {'v': [round(x, 6) for x in values[node_id]]}
        return {
            'f': features[node_id],
            't': round(thresholds[node_id], 6),
            'l': recurse(children_l[node_id]),
            'r': recurse(children_r[node_id]),
        }

    return recurse(0)


def export(model_dir: str, output_path: str):
    model_path = Path(model_dir)

    # 重新训练（或加载）pipeline
    # 这里用 skl2onnx 的加载能力不可用，直接重训
    print("📦 重新运行训练以获取 pipeline 对象...")

    sys.path.insert(0, str(Path(__file__).parent))

    # 加载特征
    features_dir = model_path.parent / 'data' / 'features'
    if (features_dir / 'X.npy').exists():
        X = np.load(features_dir / 'X.npy')
        y = np.load(features_dir / 'y.npy')
        print(f"   加载真实特征：{X.shape}")
    else:
        from generate_synthetic_data import generate_mfcc_features
        X_list, y_list = [], []
        for i, cls in enumerate(CLASSES):
            feats = generate_mfcc_features(cls, 300, seed=42 + i)
            X_list.append(feats)
            y_list.extend([i] * 300)
        X = np.vstack(X_list)
        y = np.array(y_list)
        print(f"   使用合成特征：{X.shape}")

    # 训练 pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.pipeline import Pipeline

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', GradientBoostingClassifier(
            n_estimators=200, max_depth=4,
            learning_rate=0.1, subsample=0.8, random_state=42,
        )),
    ])
    pipeline.fit(X, y)

    scaler: StandardScaler = pipeline.named_steps['scaler']
    clf: GradientBoostingClassifier = pipeline.named_steps['clf']

    # ─── 导出 Scaler ──────────────────────────────────────────────────────────
    scaler_data = {
        'mean': [round(float(x), 6) for x in scaler.mean_],
        'std':  [round(float(x), 6) for x in scaler.scale_],
    }

    # ─── 导出 GBT 树 ──────────────────────────────────────────────────────────
    # clf.estimators_ shape: (n_estimators, n_classes)  — multi-class OvR
    trees = []
    for class_estimators in clf.estimators_:   # n_estimators rows
        row = []
        for estimator in class_estimators:     # n_classes cols
            row.append(tree_to_dict(estimator.tree_))
        trees.append(row)

    # ─── 导出 prior 和学习率 ──────────────────────────────────────────────────
    # GBT initial estimator (prior log-odds per class)
    init_pred = clf._raw_predict_init(X[:1])
    prior = [round(float(x), 6) for x in init_pred[0]]

    model_json = {
        'version': '1.0',
        'type': 'GradientBoosting',
        'n_classes': len(CLASSES),
        'classes': CLASSES,
        'classes_cn': CLASSES_CN,
        'input_dim': int(X.shape[1]),
        'n_estimators': clf.n_estimators_,
        'learning_rate': clf.learning_rate,
        'prior': prior,
        'scaler': scaler_data,
        'trees': trees,    # [n_estimators][n_classes] tree dicts
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(model_json, f, separators=(',', ':'))  # compact

    size_kb = out.stat().st_size / 1024
    print(f"\n✅ 模型 JSON 已导出：{out}  ({size_kb:.0f} KB)")
    print(f"   树数量：{len(trees)} × {len(trees[0])} (estimators × classes)")

    # ─── 快速验证 ─────────────────────────────────────────────────────────────
    y_pred = pipeline.predict(X[:5])
    print(f"   前 5 个样本预测：{[CLASSES[i] for i in y_pred]}")
    print(f"   真实标签：       {[CLASSES[i] for i in y[:5]]}")

    return model_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_dir', default='../models')
    parser.add_argument('--output',    default='../mobile/assets/model.json')
    args = parser.parse_args()
    export(args.model_dir, args.output)


if __name__ == '__main__':
    main()
