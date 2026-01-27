# 资产添加 Claude Skill 使用指南

## 概述

这个 Claude Skill 允许用户通过自然对话方式向 Flux 安全平台添加资产。用户可以用自然语言描述资产（例如："Add a Linux web server with IP 192.168.1.100"），Skill 会智能提取参数、验证并调用 API 创建资产。

## 快速开始

### 1. 启动后端服务

```bash
cd backend
source venv/bin/activate
venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

### 3. 登录系统

- 打开浏览器访问前端地址（通常是 `http://localhost:5173`）
- 使用联动码登录
- 登录成功后，认证信息会自动保存到浏览器 localStorage

### 4. 使用 Claude Skill

在对话中输入自然语言描述，例如：

```
Add a Linux web server with IP 192.168.1.100
```

Claude 会引导你完成资产添加流程。

## 支持的功能

### 自然语言理解

Skill 可以理解各种表达方式：

- ✅ "Add a Linux web server with IP 192.168.1.100"
- ✅ "Create a production database at 10.0.0.50"
- ✅ "Register a Windows desktop with IP 172.16.0.100"
- ✅ "Add a router at 192.168.1.1"

### 智能参数提取

Skill 会自动提取以下信息：

#### 必填参数
- **IP 地址**: 自动识别 IPv4 地址
- **资产组ID (branchId)**: 默认值为 0

#### 可选参数
- **MAC 地址**: 识别格式如 `fe:fc:fe:d7:04:91`
- **资产名称**: 从描述中提取，如 "name it Web-01"
- **主机名**: 识别域名格式
- **操作系统类型**: 智能推断（Linux, Windows, OS X, iOS, Android 等）
- **资产分类**: 自动识别（Web服务器、数据库、路由器等）
- **重要级别**: 识别 "production" 等关键词
- **标签**: 提取逗号分隔的标签列表

### 资产分类映射

Skill 支持以下资产分类：

#### 服务器 (Server)
- Web服务器 (Nginx, Apache)
- 数据库 (MySQL, PostgreSQL, Oracle)
- DNS服务器
- 邮件服务器
- 文件服务器
- 域控制器
- 应用服务器

#### 终端 (Terminal)
- 桌面电脑
- 笔记本电脑
- 工作站

#### 网络设备 (Network Device)
- 路由器
- 交换机
- 无线接入点
- 负载均衡器
- 代理服务器

#### 安全设备 (Security Product)
- 防火墙
- IDS/IPS
- WAF
- SIEM
- EDR/XDR

#### IoT 设备
- 摄像头
- 传感器
- 智能设备

#### 移动设备
- iPhone
- Android 手机
- 平板电脑

## 对话示例

### 示例 1: 简单资产添加

```
用户: Add a Linux web server with IP 192.168.1.100

Claude: I'll help you add that asset. I've extracted:
- IP Address: 192.168.1.100
- OS Type: Linux
- Category: Web Server
- Asset Group: 0 (default)

Would you like to add an asset name, tags, or specify importance?
Or shall I proceed with just the required fields?
```

### 示例 2: 详细资产描述

```
用户: Add a production database server at 10.0.0.50, it's MySQL, name it DB-Primary

Claude: I've extracted:
- IP Address: 10.0.0.50
- Asset Name: DB-Primary
- Category: Database Server
- Importance: Core (production)
- Asset Group: 0 (default)

I need the operating system (Linux/Windows/etc.).
Please provide it so I can add the asset.
```

### 示例 3: 多轮对话

```
用户: I want to add a new server

Claude: Great! I'll help you add a server. I'll need some information:
1. What's the IP address of the server?
2. What type of server is it? (web server, database, file server, etc.)

用户: IP is 172.16.0.100, it's a web server

Claude: Perfect! I have the basic information. A few more details:
- What's the operating system? (Linux, Windows, etc.)
- Would you like to give it a name?
- Is it a production server or normal?

用户: It's Linux, name it Web-01, it's for production

Claude: Excellent! Here's the complete asset information:
- IP Address: 172.16.0.100
- Asset Name: Web-01
- OS Type: Linux
- Category: Web Server
- Importance: Core
- Asset Group: 0

Ready to add this asset. Shall I proceed?

用户: Yes, add it

Claude: Asset added successfully! Server "Web-01" has been registered in the system.
```

## API 文档

### 后端 API 端点

#### 1. 创建资产
- **URL**: `POST /api/v1/assets/create`
- **Headers**:
  - `X-Auth-Code`: Flux 平台联动码
  - `X-Base-Url`: Flux API 基础 URL
- **Body**:
```json
{
  "ip": "192.168.1.100",
  "branchId": 0,
  "mac": "fe:fc:fe:d7:04:91",
  "assetName": "Web Server 1",
  "hostName": "web-01.example.com",
  "type": "Linux",
  "magnitude": "core",
  "tags": ["production", "web"],
  "classify1Id": 1,
  "classifyId": 100012,
  "comment": "Main web server"
}
```

#### 2. 参数推断
- **URL**: `POST /api/v1/assets/infer`
- **Body**:
```json
{
  "text": "Add a Linux web server with IP 192.168.1.100",
  "provided_params": {}
}
```

#### 3. 获取分类映射
- **URL**: `GET /api/v1/assets/categories`
- **返回**: OS 类型映射和资产分类映射

## 错误处理

Skill 会处理以下错误情况：

### 验证错误
- ❌ 无效的 IP 地址格式
- ❌ 无效的 MAC 地址格式
- ❌ 字段长度超过限制
- ❌ 标签数量超过限制

### API 错误
- ❌ 认证失败
- ❌ 网络超时
- ❌ 重复 IP
- ❌ 无效的资产组 ID

### 用户反馈
对于每种错误，Skill 都会：
1. 提供清晰的错误消息
2. 展示正确的格式示例
3. 建议下一步操作

## 最佳实践

1. **提供完整的描述**: 尽可能在第一次描述中提供所有信息
2. **使用标准的术语**: 使用 "Linux", "Windows", "web server" 等标准术语
3. **明确资产名称**: 如果有特定名称，使用 "name it XXX" 的表达方式
4. **指定重要级别**: 使用 "production", "critical" 等关键词
5. **逐步完善**: 如果不确定某些参数，可以先提供基本信息，然后逐步补充

## 技术细节

### 架构

```
用户自然语言输入
    ↓
Claude Skill (.claude/skills/add-asset.md)
    ↓
LLM 参数提取（结构化输出）
    ↓
验证与类型检查
    ↓
API 调用（通过 asset_service.py）
    ↓
Flux XDR API (/api/xdr/v1/assets)
    ↓
成功/错误反馈
```

### 文件结构

- `.claude/skills/add-asset.md` - Claude Skill 定义
- `backend/app/services/asset_service.py` - 资产服务层
- `backend/app/api/v1/endpoints/assets.py` - REST API 端点
- `frontend/src/components/tool/LoginForm.tsx` - 登录表单（保存认证信息）
- `backend/app/main.py` - 主路由器（注册资产路由）

### 认证机制

- 使用 HMAC-SHA256 签名认证
- 复用现有的 Signature SDK（`aksk_py3.py`）
- 支持联动码（auth_code）或 AK/SK
- 认证信息存储在浏览器 localStorage

## 故障排除

### 问题: 无法添加资产

**解决方案**:
1. 确认已登录系统（检查 localStorage 中的 `flux_auth_code`）
2. 检查后端服务是否正常运行
3. 查看浏览器控制台是否有错误信息
4. 验证提供的 IP 地址格式是否正确

### 问题: 参数推断不准确

**解决方案**:
1. 使用更明确的表达方式
2. 提供更多上下文信息
3. 使用标准术语（如 "Linux", "web server"）
4. 分步提供信息，让 Skill 确认后再继续

### 问题: API 调用失败

**解决方案**:
1. 检查网络连接
2. 验证 Flux API 地址是否正确
3. 确认联动码是否有效
4. 查看后端日志获取详细错误信息

## 后续增强

计划中的功能增强：

- [ ] 批量资产导入（CSV/Excel）
- [ ] 资产更新和删除
- [ ] 资产搜索和过滤
- [ ] 资产关系和拓扑图
- [ ] 资产监控和分析
- [ ] 资产模板管理

## 支持

如有问题或建议，请联系开发团队或提交 Issue。
