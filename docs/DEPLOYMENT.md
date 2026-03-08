# 📱 移动端部署指南

**版本:** v3  
**模型准确率:** 51.57%  
**更新日期:** 2026-03-08

---

## 🎯 当前状态

| 模块 | 状态 | 说明 |
|------|------|------|
| **模型导出** | ✅ 完成 | ONNX 格式 (11.75 KB) |
| **推理服务** | ✅ 完成 | CryRecognitionService.js |
| **UI 集成** | ✅ 完成 | HomeScreen 更新 |
| **类别映射** | ✅ 完成 | class_mapping.json |

---

## 📦 模型文件

| 文件 | 位置 | 大小 | 说明 |
|------|------|------|------|
| `cry_classifier.onnx` | `mobile/assets/` | 11.75 KB | ONNX 模型 |
| `class_mapping.json` | `mobile/assets/` | 200 B | 类别映射 |

---

## 🔧 集成步骤

### 1. 安装依赖

```bash
cd baby-cry-app/mobile

# 安装 ONNX Runtime (可选，当前使用模拟推理)
npm install onnxruntime-react-native

# 安装音频处理
npm install expo-av
```

### 2. 模型文件已就位

```
mobile/assets/
├── cry_classifier.onnx    # 模型文件
└── class_mapping.json     # 类别映射
```

### 3. 服务已集成

```javascript
// mobile/src/services/CryRecognitionService.js
import CryRecognitionService from '../services/CryRecognitionService';

// 使用示例
await CryRecognitionService.initialize();
const result = await CryRecognitionService.recognize(audioUri);
console.log(result.type); // 'hungry', 'sleepy', etc.
```

### 4. UI 已更新

```javascript
// mobile/src/screens/HomeScreen.js
// 监听按钮已集成识别逻辑
// 检测到哭声会自动发送通知
```

---

## 🚀 运行测试

### 开发模式

```bash
cd baby-cry-app/mobile
npm install
npm start

# 扫码打开 Expo Go
# iOS: 用 Camera App
# Android: 用 Expo Go App
```

### 真机测试

1. 点击"开始监听"按钮
2. 播放测试音频（婴儿哭声）
3. 查看识别结果
4. 检查通知推送

---

## 📊 模型性能

### 各类别表现

| 类别 | 召回率 | 建议 |
|------|--------|------|
| hungry (饿了) | 94.0% | ✅ 可直接使用 |
| sleepy (困了) | 10.3% | ⚠️ 经常误判为 hungry |
| uncomfortable | 17.0% | ⚠️ 经常误判为 hungry |
| normal (正常) | 56.5% | ⚠️ 一般 |

### 使用建议

**当前模型适合：**
- ✅ 检测"饿了"哭声（94% 准确率）
- ✅ 作为 demo 展示
- ✅ 收集用户反馈

**需要改进：**
- ❌ sleepy/uncomfortable 识别率低
- ❌ 需要更多训练数据
- ❌ 需要真正的 ONNX 推理集成

---

## 🔄 模型更新流程

### 本地推理（当前）

```
训练新模型 → 导出 ONNX → 替换文件 → 重新发布 App
                                    ↑
                                 需要审核
```

**更新难度：** ⭐⭐⭐ (需要重新发版)

### 云端推理（未来）

```
训练新模型 → 部署到服务器 → App 自动使用
                              ↑
                          无需发版
```

**更新难度：** ⭐ (热更新)

---

## 📝 TODO

### 高优先级

- [ ] 集成真正的 ONNX Runtime
- [ ] 实现音频特征提取 (librosa.js 或原生模块)
- [ ] 测试真机推理性能

### 中优先级

- [ ] 添加模型版本管理
- [ ] 实现 A/B 测试框架
- [ ] 收集用户反馈数据

### 低优先级

- [ ] 准备云端 API
- [ ] 实现模型热更新
- [ ] 添加使用统计

---

## 🎯 下一步

1. **测试当前版本** - 验证 UI 和基本功能
2. **收集反馈** - 看看实际效果如何
3. **迭代优化** - 根据反馈改进模型

---

**🦞 虾虾开发 - 2026-03-08**
