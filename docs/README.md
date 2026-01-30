# Flux 项目文档

本目录包含项目开发和维护过程中使用的内部文档，**不上传到 GitHub**。

## 📁 目录结构

### api-reference/
API 接口参考文档，包含 Flux XDR 平台的 API 定义和参数说明。

**文件列表**：
- `查询安全事件列表.txt` - 安全事件列表查询 API
- `根据事件uuId获取举证信息.txt` - 事件举证信息获取 API
- `根据事件uuId获取事件外网ip处置实体.txt` - IP 处置实体查询 API
- `批量修改安全事件处置接口.txt` - 批量更新事件状态 API
- `查询封禁设备列表.txt` - 封禁设备查询 API
- `查询封禁地址策略列表.txt` - 封禁策略查询 API
- `新增网侧封禁地址策略.txt` - 创建封禁策略 API
- `asset.txt` - 资产管理相关 API

**用途**：开发过程中参考 API 参数格式和返回值结构

### development-notes/
开发过程记录文档，包含问题修复、调试笔记等。

**文件列表**：
- `IP_BLOCK_CONNECTION_FIX.md` - IP 封禁连接错误修复记录

**用途**：记录问题排查过程和解决方案，供后续参考

---

## 📝 注意事项

1. **本目录不上传到 GitHub**，已在 `.gitignore` 中配置
2. 这些文档主要用于内部开发参考
3. API 文档来源于 Flux XDR 平台的 OpenAPI 规范
4. 开发笔记用于记录问题排查和解决方案

## 🔗 相关文档

- [项目主 README](../README.md) - 项目说明和快速开始指南
- [API 交互文档](http://localhost:8000/docs) - FastAPI 自动生成的 Swagger 文档
