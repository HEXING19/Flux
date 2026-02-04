# IP封禁显示问题修复

## 问题描述

用户报告了两个问题：
1. **422错误** - `POST /api/v1/ipblock/confirm-block HTTP/1.1" 422 Unprocessable Entity
2. **前端显示问题** - 确认对话框中没有显示需要封禁的IP地址

## 问题原因

后端服务返回的参数字段名与前端期望的字段名不匹配：

**后端返回**：
```python
"block_params": {
    "ip_address": "100.200.1.200",  # ❌ 使用了 ip_address
    "device_id": 123456,
    ...
}
```

**前端期望**：
```typescript
interface IPBlockParams {
  ip: string;  // ✅ 期望的是 ip 字段
  device_id: number;
  ...
}
```

## 修复方案

修改 `/Users/hexing/Flux/backend/app/services/ipblock_service.py` 的 `check_and_block` 方法：

### 修改前（第599行）
```python
"block_params": {
    "ip_address": ip_address,  # ❌ 字段名不匹配
    "device_id": target_device["device_id"],
    "device_name": target_device["device_name"],
    ...
}
```

### 修改后（第599行）
```python
"block_params": {
    "ip": ip_address,  # ✅ 改为 ip
    "device_id": target_device["device_id"],
    "device_name": target_device["device_name"],
    ...
}
```

## 修复效果

修复后，确认对话框将正确显示所有参数，包括IP地址：

```
IP 地址
100.200.1.200  ← 现在会正确显示

封禁设备
物联网安全网关 (AF)

封禁类型
源IP

封禁时长
永久封禁

设备状态
告警  ← 同时也修复了告警状态的判断
```

## 其他相关修复

同时修复了设备状态的判断逻辑，现在只有以下状态不可联动：
- `offline`（离线）
- `not_active`（未接入）

而 `online`（在线）和 `告警` 状态都可以正常联动。

## 测试验证

修复后，用户可以重新输入：
```
请帮我查询100.200.1.200这个IP地址是否已经被封禁，没有的话帮我调用物联网安全网关这个设备进行封禁
```

预期结果：
1. ✅ 系统识别为IP封禁操作
2. ✅ 查询设备列表，找到"物联网安全网关"
3. ✅ 检查设备状态（告警 - 可联动）
4. ✅ 显示确认对话框，**包含IP地址**
5. ✅ 用户确认后成功执行封禁

## 文件变更

**修改的文件**：
- `/Users/hexing/Flux/backend/app/services/ipblock_service.py`
  - 第599行：`ip_address` → `ip`
  - 第581行：修正设备状态判断逻辑

**无需修改的文件**：
- 前端组件 - 字段名已经是正确的（`ip`）
- API端点 - 参数定义已经是正确的（`ip`）
- 类型定义 - 字段名已经是正确的（`ip`）
