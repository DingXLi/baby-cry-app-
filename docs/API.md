# 📡 API 文档

## 基础信息

**Base URL:** `http://localhost:3000/api/v1` (开发环境)

**认证方式:** JWT Token

---

## 认证模块 (Auth)

### POST `/auth/register`
用户注册

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "User Name"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "User Name"
    },
    "token": "jwt_token_here"
  }
}
```

---

### POST `/auth/login`
用户登录

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "user": { ... },
    "token": "jwt_token_here"
  }
}
```

---

### GET `/auth/me`
获取当前用户信息

**Headers:** `Authorization: Bearer <token>`

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "createdAt": "2026-02-27T00:00:00Z"
  }
}
```

---

## 哭声记录模块 (Cry Records)

### GET `/cry-records`
获取用户的哭声记录列表

**Headers:** `Authorization: Bearer <token>`

**查询参数:**
- `page` (number): 页码，默认 1
- `limit` (number): 每页数量，默认 20
- `startDate` (string): 开始日期 (ISO 8601)
- `endDate` (string): 结束日期 (ISO 8601)
- `type` (string): 哭声类型过滤 (hungry|sleepy|uncomfortable|normal)

**响应:**
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "id": "uuid",
        "userId": "uuid",
        "cryType": "hungry",
        "confidence": 0.92,
        "audioUrl": "/audio/xxx.wav",
        "duration": 5.2,
        "timestamp": "2026-02-27T08:30:00Z",
        "createdAt": "2026-02-27T08:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

---

### POST `/cry-records`
上传新的哭声记录

**Headers:** `Authorization: Bearer <token>`

**请求体:** `multipart/form-data`
- `audio`: 音频文件 (WAV/MP3)
- `cryType`: 哭声类型（可选，用于手动标注）
- `notes`: 备注（可选）

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "cryType": "hungry",
    "confidence": 0.92,
    "audioUrl": "/audio/xxx.wav",
    "createdAt": "2026-02-27T08:30:00Z"
  }
}
```

---

### GET `/cry-records/:id`
获取单条哭声记录详情

**Headers:** `Authorization: Bearer <token>`

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "userId": "uuid",
    "cryType": "hungry",
    "confidence": 0.92,
    "audioUrl": "/audio/xxx.wav",
    "duration": 5.2,
    "notes": null,
    "timestamp": "2026-02-27T08:30:00Z",
    "createdAt": "2026-02-27T08:30:00Z"
  }
}
```

---

### DELETE `/cry-records/:id`
删除哭声记录

**Headers:** `Authorization: Bearer <token>`

**响应:**
```json
{
  "success": true,
  "message": "Record deleted successfully"
}
```

---

## 统计分析模块 (Analytics)

### GET `/analytics/summary`
获取统计摘要

**Headers:** `Authorization: Bearer <token>`

**查询参数:**
- `period`: `day` | `week` | `month` | `year`

**响应:**
```json
{
  "success": true,
  "data": {
    "totalCries": 150,
    "averagePerDay": 5.2,
    "typeDistribution": {
      "hungry": 45,
      "sleepy": 30,
      "uncomfortable": 20,
      "normal": 5
    },
    "peakHours": [2, 3, 14, 22],
    "period": "week"
  }
}
```

---

### GET `/analytics/trends`
获取趋势数据

**Headers:** `Authorization: Bearer <token>`

**查询参数:**
- `type`: 哭声类型
- `days`: 天数，默认 30

**响应:**
```json
{
  "success": true,
  "data": {
    "labels": ["2026-01-01", "2026-01-02", ...],
    "datasets": {
      "hungry": [5, 3, 7, ...],
      "sleepy": [2, 4, 1, ...],
      "uncomfortable": [1, 2, 3, ...],
      "normal": [0, 1, 0, ...]
    }
  }
}
```

---

## 模型模块 (Model)

### GET `/model/info`
获取当前模型信息

**响应:**
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "accuracy": 0.89,
    "lastUpdated": "2026-02-27T00:00:00Z",
    "classes": ["hungry", "sleepy", "uncomfortable", "normal"]
  }
}
```

---

### POST `/model/predict`
使用服务端模型进行预测（可选）

**Headers:** `Authorization: Bearer <token>`

**请求体:** `multipart/form-data`
- `audio`: 音频文件

**响应:**
```json
{
  "success": true,
  "data": {
    "cryType": "hungry",
    "confidence": 0.92,
    "probabilities": {
      "hungry": 0.92,
      "sleepy": 0.05,
      "uncomfortable": 0.02,
      "normal": 0.01
    }
  }
}
```

---

## 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [...]
  }
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| `VALIDATION_ERROR` | 400 | 请求验证失败 |
| `UNAUTHORIZED` | 401 | 未认证 |
| `FORBIDDEN` | 403 | 无权限 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `SERVER_ERROR` | 500 | 服务器错误 |

---

## 速率限制

- 普通请求：100 次/分钟
- 上传音频：10 次/分钟
- 预测请求：30 次/分钟

---

📝 **注意:** Phase 1 以本地推理为主，后端主要用于数据同步和备份。
