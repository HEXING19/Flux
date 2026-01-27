# LLM 聊天集成资产添加功能 - 使用指南

## 概述

现在您可以直接在前端对话界面中通过自然语言添加资产！系统会自动识别您的意图，提取参数，并调用 Flux XDR API 创建资产。

## 如何使用

### 1. 启动服务

```bash
# 后端
cd backend
source venv/bin/activate
venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev
```

### 2. 登录系统

1. 打开浏览器访问前端地址（通常是 `http://localhost:5173`）
2. 使用联动码登录
3. 登录成功后，认证信息会自动保存到浏览器 localStorage

### 3. 配置 LLM

1. 进入"设置"页面
2. 配置大模型 API（推荐使用智谱AI、OpenAI 或 DeepSeek）
3. 保存配置

### 4. 开始对话

进入聊天界面，您可以用自然语言添加资产：

## 示例对话

### 示例 1: 简单资产添加

**您输入：**
```
Add a Linux web server with IP 192.168.127.100
```

**系统响应：**
```
我识别到您想添加一个资产。我已经提取了以下信息：

• IP 地址: 192.168.127.100
• 操作系统: Linux
• 资产分类: 服务器
• 重要级别: 普通
• 资产组: 0

✅ 资产添加成功！

资产信息：
• IP: 192.168.127.100
• 类型: Linux
• 分类: 服务器
• 资产组: 0
```

### 示例 2: 详细描述

**您输入：**
```
Add a production database server at 10.0.0.50, it's MySQL, name it DB-Primary, it's very important
```

**系统响应：**
```
我识别到您想添加一个资产。我已经提取了以下信息：

• IP 地址: 10.0.0.50
• 资产名称: DB-Primary
• 操作系统: Unknown
• 资产分类: 服务器
• 重要级别: 核心
• 资产组: 0

✅ 资产添加成功！
```

### 示例 3: 网络设备

**您输入：**
```
Add a router with IP 192.168.1.1
```

**系统响应：**
```
我识别到您想添加一个资产。我已经提取了以下信息：

• IP 地址: 192.168.1.1
• 资产分类: 网络设备
• 资产组: 0

✅ 资产添加成功！
```

## 支持的表达方式

系统可以理解各种表达方式：

- ✅ "Add a Linux web server with IP 192.168.1.100"
- ✅ "Create a production database at 10.0.0.50"
- ✅ "Register a Windows desktop with IP 172.16.0.100"
- ✅ "Add a router at 192.168.1.1"
- ✅ "I want to add a new server"
- ✅ "Create an asset with IP 10.0.0.1"

## 可识别的参数

系统可以自动识别以下信息：

### 必填参数
- **IP 地址** - 必须提供

### 可选参数
- **资产名称** - 如 "name it Web-01"
- **操作系统** - Linux, Windows, OS X, iOS, Android 等
- **资产分类** - Web服务器、数据库、路由器、交换机等
- **重要级别** - production, critical, important → core
- **MAC 地址** - 如 "fe:fc:fe:d7:04:91"
- **主机名** - 如 "web-01.example.com"
- **标签** - 如 "production", "web"
- **备注** - 任意描述

## 工作原理

### 1. 意图检测

系统首先使用 LLM 判断您是否想要添加资产：

```
用户消息 → LLM 分析 → 判断意图
                  ↓
         add_asset | general_chat
```

### 2. 参数提取

如果识别为添加资产，系统会提取结构化参数：

```
用户消息 → LLM 提取 → JSON 参数
                    {
                      "ip": "192.168.1.100",
                      "type": "Linux",
                      "classify1Id": 1,
                      ...
                    }
```

### 3. 参数验证与补充

使用 AssetService 验证和补充参数：

```
提取的参数 → AssetService → 验证 + 补充默认值
```

### 4. API 调用

调用 Flux XDR API 创建资产：

```
验证的参数 → HMAC-SHA256 签名 → Flux XDR API
                                    ↓
                              返回创建结果
```

### 5. 结果格式化

将结果格式化为易读的消息返回给您：

```
API 结果 → 格式化 → 用户友好的消息
```

## 技术细节

### 修改的文件

1. **backend/app/services/llm_service.py**
   - 添加 `chat_with_asset_support` 方法
   - 添加 `_detect_intent` 方法（意图检测）
   - 添加 `_extract_asset_params` 方法（参数提取）
   - 添加 `_format_confirmation_message` 方法（格式化确认信息）

2. **backend/app/api/v1/endpoints/llm.py**
   - 更新 `ChatRequest` 模型（添加 auth_code 和 flux_base_url）
   - 修改 `/chat` 端点（调用新的方法）

3. **frontend/src/components/chat/ChatInterface.tsx**
   - 从 localStorage 读取 flux_auth_code 和 flux_base_url
   - 在调用 API 时传递认证信息

### API 调用链路

```
前端 → POST /api/v1/llm/chat
  ↓
LLMService.chat_with_asset_support()
  ├─ _detect_intent() ← LLM API
  ├─ _extract_asset_params() ← LLM API
  └─ AssetService.create_asset()
      └─ POST /api/xdr/v1/assets ← Flux XDR API
```

### 认证流程

1. **登录时**：LoginForm 保存 `flux_auth_code` 和 `flux_base_url` 到 localStorage
2. **聊天时**：ChatInterface 从 localStorage 读取并传递给后端
3. **API调用时**：AssetService 使用 auth_code 进行 HMAC-SHA256 签名

## 故障排除

### 问题：系统提示 "⚠️ 资产已存在"

**原因**：该 IP 地址的资产已经在系统中存在

**示例**：
```
您：Add a Linux web server with IP 192.168.127.100

系统：我识别到您想添加一个资产...
⚠️ 资产已存在

IP 地址 192.168.127.100 的资产已经在系统中存在。

如果您想更新该资产，请使用其他命令。
```

**解决方案**：
- 使用不同的 IP 地址
- 或者检查现有资产是否需要更新
- 如果确实需要重复添加，联系系统管理员

### 问题：系统没有识别到添加资产的意图

**原因**：意图检测的置信度低于 0.7

**解决方案**：
- 使用更明确的表达方式
- 包含关键词："add", "create", "register", "asset", "server"
- 示例：❌ "I have a server" → ✅ "Add a server with IP 192.168.1.100"

### 问题：参数提取不准确

**原因**：LLM 没有正确理解您的描述

**解决方案**：
- 使用标准的术语（Linux, Windows, web server, database）
- 提供更多上下文信息
- 明确指定 IP 地址
- 示例：❌ "a machine" → ✅ "a Linux web server with IP 192.168.1.100"

### 问题：提示 "缺少 Flux 认证信息"

**原因**：localStorage 中没有保存认证信息

**解决方案**：
1. 退出当前登录
2. 重新使用联动码登录
3. 确认登录成功后再尝试添加资产

### 问题：提示 "认证失败"

**原因**：联动码无效或已过期

**解决方案**：
1. 确认已登录系统
2. 检查联动码是否有效
3. 尝试重新登录获取新的联动码

### 问题：提示 "IP 地址格式无效"

**原因**：IP 地址格式不正确

**解决方案**：
- 使用正确的 IPv4 格式：xxx.xxx.xxx.xxx
- 示例：✅ 192.168.1.100, 10.0.0.1
- 错误：❌ 192.168.1.256, 192.168.1, 192.168.1.1.1

## 优势

✅ **自然交互** - 无需学习复杂操作，自然对话即可
✅ **智能识别** - LLM 准确理解您的意图
✅ **自动验证** - 系统自动验证和补充参数
✅ **实时反馈** - 即时显示提取的信息和创建结果
✅ **无缝集成** - 与现有聊天界面完美集成

## 后续增强

计划中的功能：

- [ ] 支持多轮对话（逐步收集参数）
- [ ] 支持资产查询
- [ ] 支持资产更新
- [ ] 支持资产删除
- [ ] 添加会话状态管理（Redis）
- [ ] 支持批量添加资产

## 总结

现在您可以通过简单自然的方式添加资产：
1. 登录系统
2. 进入聊天界面
3. 用自然语言描述要添加的资产
4. 系统自动处理并返回结果

就是这么简单！🎉
