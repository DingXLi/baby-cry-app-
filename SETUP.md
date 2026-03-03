# 🔧 项目设置指南

## GitHub 仓库信息

- **仓库名:** `baby-cry-app`
- **可见性:** 公开 (Public)
- **SSH 公钥:** 已提供 ✅

---

## 第一步：在 GitHub 创建仓库

### 1. 添加 SSH Key 到 GitHub

1. 打开 https://github.com/settings/keys
2. 点击 **New SSH key**
3. 标题：`Laptop` 或任意名称
4. Key 类型：选择 **Authentication Key**
5. 粘贴你的公钥：
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKFy7qwhOA0t6zg/MwJJnGBgVqrkloX925XRvWIvwm6R lidin@LAPTOP-1KAS76HU
   ```
6. 点击 **Add SSH key**

### 2. 创建仓库

1. 打开 https://github.com/new
2. 仓库名：`baby-cry-app`
3. 可见性：**Public**
4. ❌ 不要勾选 "Initialize this repository with a README"
5. 点击 **Create repository**

### 3. 测试 SSH 连接

```bash
ssh -T git@github.com
```

看到 `Hi <username>! You've successfully authenticated` 就成功了！

---

## 第二步：初始化本地仓库

创建完仓库后，告诉我 **你的 GitHub 用户名**，我会帮你：

1. 初始化 Git 仓库
2. 添加远程仓库
3. 推送所有文件

---

## 第三步：数据集调研

Kaggle 上的婴儿哭声数据集：

- https://www.kaggle.com/datasets?query=baby+cry
- 推荐先看看这些，选定一个作为初始数据集

---

## 技术栈确认

| 模块 | 技术 |
|------|------|
| 移动端 | React Native (Expo) |
| ML 训练 | Python + TensorFlow |
| ML 推理 | TensorFlow Lite |
| 后端 | Node.js + Express + PostgreSQL |
| 部署 | Docker + Railway/Render |

---

🦞 弄好 GitHub 仓库后告诉我你的用户名！
