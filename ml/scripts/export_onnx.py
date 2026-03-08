#!/usr/bin/env python3
"""
导出 ONNX 模型 - 用于移动端部署
🦞 虾虾开发

用法:
    python export_onnx.py
"""

import torch
import torch.nn as nn
import onnx
import onnxruntime as ort
import numpy as np
from pathlib import Path

NUM_CLASSES = 4
CLASS_NAMES = ['hungry', 'sleepy', 'uncomfortable', 'normal']
INPUT_DIM = 168


class SimpleTransfer(nn.Module):
    """与训练脚本 v3 一致的模型结构"""
    def __init__(self, input_dim=168):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, NUM_CLASSES),
        )
    
    def forward(self, x):
        return self.net(x)


def export_model():
    print("\n" + "=" * 60)
    print("🦞 导出 ONNX 模型")
    print("=" * 60)
    
    # 加载 PyTorch 模型
    model_path = Path('/home/liding/.openclaw/workspace/baby-cry-app/ml/models/best_model_v3.pth')
    model = SimpleTransfer(INPUT_DIM)
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
    model.eval()
    
    print(f"✅ 模型加载：{model_path}")
    
    # 创建示例输入
    dummy_input = torch.randn(1, INPUT_DIM)
    
    # 导出 ONNX
    output_path = Path('/home/liding/.openclaw/workspace/baby-cry-app/mobile/assets/cry_classifier.onnx')
    output_path.parent.mkdir(exist_ok=True)
    
    torch.onnx.export(
        model,
        dummy_input,
        str(output_path),
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print(f"✅ ONNX 导出：{output_path}")
    
    # 验证模型
    print("\n🔍 验证模型...")
    
    # 检查 ONNX 模型
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print("✅ ONNX 模型验证通过")
    
    # 测试推理
    ort_session = ort.InferenceSession(str(output_path))
    ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.numpy()}
    ort_outs = ort_session.run(None, ort_inputs)
    
    # 对比 PyTorch 和 ONNX 输出
    with torch.no_grad():
        pt_out = model(dummy_input)
    
    pt_out = pt_out.numpy()
    onnx_out = ort_outs[0]
    
    diff = np.abs(pt_out - onnx_out).max()
    print(f"✅ PyTorch vs ONNX 最大差异：{diff:.6f}")
    
    # 模型信息
    print("\n📊 模型信息:")
    print(f"   输入形状：{dummy_input.shape}")
    print(f"   输出形状：{pt_out.shape}")
    print(f"   输出类别：{CLASS_NAMES}")
    print(f"   文件大小：{output_path.stat().st_size / 1024:.2f} KB")
    
    # 保存类别映射
    mapping_path = Path('/home/liding/.openclaw/workspace/baby-cry-app/mobile/assets/class_mapping.json')
    import json
    mapping = {
        'classes': CLASS_NAMES,
        'input_dim': INPUT_DIM,
        'model_version': 'v3',
        'accuracy': 0.5157
    }
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\n💾 类别映射：{mapping_path}")
    print("\n🎉 导出完成!")
    
    return output_path


if __name__ == '__main__':
    export_model()
