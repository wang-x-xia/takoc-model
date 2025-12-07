# Store API v1

## 概述

Store API v1 是一个基于RESTful风格的数据库API，提供Namespace管理、Table管理和数据CRUD操作。

## 基础信息

- API版本: v1
- 基础URL: `/api/v1`
- 认证方式: 暂未实现
- 请求/响应格式: JSON

## 主要API列表

### Namespace管理
- `POST /api/v1/namespace` - 创建Namespace
- `GET /api/v1/namespace` - 获取Namespace列表
- `GET /api/v1/namespace/{namespace}` - 获取单个Namespace
- `PUT /api/v1/namespace/{namespace}` - 更新Namespace
- `DELETE /api/v1/namespace/{namespace}` - 删除Namespace

### Table管理
- `POST /api/v1/table/{namespace}/{table}` - 创建Table（需包含JSON Schema）
- `GET /api/v1/table/{namespace}` - 获取Table列表
- `GET /api/v1/table/{namespace}/{table}` - 获取单个Table
- `PUT /api/v1/table/{namespace}/{table}` - 更新Table
- `DELETE /api/v1/table/{namespace}/{table}` - 删除Table

### 数据操作
- `POST /api/v1/data/{namespace}/{table}` - 创建数据
- `GET /api/v1/data/{namespace}/{table}` - 列出数据
- `PUT /api/v1/data/{namespace}/{table}/{record_id}` - 更新数据
- `DELETE /api/v1/data/{namespace}/{table}/{record_id}` - 删除数据

## 默认Namespace

系统默认提供一个名为 `takoc` 的特殊Namespace，用于管理系统元数据。该Namespace包含以下三个Table：

- **config**：存储系统配置信息
- **namespace**：存储系统中所有创建的Namespace元数据
- **table**：存储系统中所有创建的Table元数据

## 详细文档

完整的API文档以OpenAPI 3.0 YAML格式提供，请查看：
`src/api/v1.yaml`

## 错误处理

所有API都返回标准的HTTP状态码和JSON格式的错误响应，包含错误代码、消息和详细信息。

## 版本控制

- API版本通过URL路径中的 `v1` 标识
- 当API进行不兼容的更改时，将发布新版本（如 `v2`）
- 旧版本将在合理的时间内保持可用