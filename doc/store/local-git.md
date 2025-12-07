# Local Git 存储方案

## 1. 核心设计理念

Local Git 存储方案基于以下核心原则：

- **直接存储在仓库**：默认将数据直接存储在 Git 仓库根目录，支持配置自定义存储位置
- **配置驱动**：通过全局配置和表级配置管理数据结构和行为
- **列表文件维护**：使用专门的 YAML 文件维护命名空间和表的列表，确保一致性
- **Git 集成**：提供数据完备性检查，确保 Git 中的数据有效
- **格式灵活**：支持 JSON 和 YAML 格式，默认使用 YAML

## 2. 目录结构

### 2.1 默认目录结构

数据默认直接存储在 Git 仓库根目录：

```
.git/
├── ... (Git内部文件)
└── hooks/ (Git钩子)
takoc.yaml                 # 全局配置文件
namespaces.yaml            # 命名空间列表
mynamespace/               # Namespace 目录
├── tables.yaml            # Table 列表
└── mytable/               # Table 目录
    ├── config.yaml        # Table 配置
    ├── schema.yaml        # Table 的 JSON Schema 定义
    ├── records.yaml       # Records 列表
    └── records/           # 数据记录存储目录
        ├── record1.yaml
        ├── record2.yaml
        └── ...
anothernamespace/          # 另一个 Namespace 目录
└── ...
```

### 2.2 自定义存储位置

用户可以通过全局配置文件将数据存储在特定目录下：

```
.git/
├── ... (Git内部文件)
└── hooks/ (Git钩子)
takoc.yaml
└── data/                  # 用户自定义的数据目录
    ├── namespaces.yaml
    ├── mynamespace/
    │   ├── tables.yaml
    │   └── mytable/
    │       ├── config.yaml
    │       ├── schema.yaml
    │       ├── records.yaml
    │       └── records/
    │           └── ...
    └── ...
```

### 2.3 核心目录说明

- **全局配置文件**：`takoc.yaml` - 存储系统级配置
- **命名空间列表**：`namespaces.yaml` - 维护所有命名空间
- **命名空间目录**：`{namespace}/` - 包含该命名空间下的所有表
- **表列表**：`{namespace}/tables.yaml` - 维护该命名空间下的所有表
- **表目录**：`{namespace}/{table}/` - 包含表的配置和数据
- **表配置**：`{namespace}/{table}/config.yaml` - 存储表级配置
- **表结构**：`{namespace}/{table}/schema.yaml` - Table 的 JSON Schema 定义
- **记录列表**：`{namespace}/{table}/records.yaml` - 维护该表下的所有记录
- **记录目录**：`{namespace}/{table}/records/` - 存储数据记录

## 3. 配置系统

### 3.1 全局配置文件 (`takoc.yaml`)

```yaml
# 全局配置
version: "1.0"

# 数据存储配置
storage:
  # 数据存储位置，默认根目录，可配置为相对或绝对路径
  data_dir: "."
  # 默认文件格式：yaml 或 json
  default_format: "yaml"

# Git 集成配置
git:
  # 数据完备性检查开关
  integrity_check: true
```

### 3.2 命名空间列表 (`namespaces.yaml`)

```yaml
# 命名空间列表
namespaces:
  - name: "mynamespace"
    description: "我的第一个命名空间"
    created_at: "2023-01-01T00:00:00Z"
    updated_at: "2023-01-01T00:00:00Z"
  
  - name: "anothernamespace"
    description: "另一个命名空间"
    created_at: "2023-01-02T00:00:00Z"
    updated_at: "2023-01-02T00:00:00Z"
```

### 3.3 表列表 (`{namespace}/tables.yaml`)

```yaml
# 表列表
namespace: "mynamespace"
tables:
  - name: "mytable"
    description: "我的第一个表"
    created_at: "2023-01-01T00:00:00Z"
    updated_at: "2023-01-01T00:00:00Z"
  
  - name: "anothertable"
    description: "另一个表"
    created_at: "2023-01-02T00:00:00Z"
    updated_at: "2023-01-02T00:00:00Z"
```

### 3.4 表配置 (`{namespace}/{table}/config.yaml`)

```yaml
# 表配置
name: "mytable"
namespace: "mynamespace"
description: "我的第一个表"
created_at: "2023-01-01T00:00:00Z"
updated_at: "2023-01-01T00:00:00Z"

# 表格式配置
format:
  schema: "yaml"     # schema 文件格式
  records: "yaml"    # 记录文件格式
```

## 4. 文件格式

### 4.1 Schema 文件 (`schema.yaml`)

使用 YAML 格式的 JSON Schema Draft 2020-12，定义 Table 的数据结构和验证规则：

```yaml
$schema: https://json-schema.org/draft/2020-12/schema
title: Table Schema
description: Table description
type: object
properties:
  field1:
    type: string
    description: Field 1 description
  field2:
    type: integer
    minimum: 0
    description: Field 2 description
required:
  - field1
additionalProperties: true
```

### 4.2 Record 列表 (`records.yaml`)

维护表中的所有记录 ID：

```yaml
# 记录列表
namespace: "mynamespace"
table: "mytable"
records:
  - id: "record1"
    created_at: "2023-01-01T00:00:00Z"
    updated_at: "2023-01-01T00:00:00Z"
  
  - id: "record2"
    created_at: "2023-01-02T00:00:00Z"
    updated_at: "2023-01-02T12:00:00Z"
```

### 4.3 Record 文件 (`{record_id}.yaml`)

包含记录的原始数据和元数据：

```yaml
id: record1
data:
  field1: value1
  field2: 42
  additionalField: extra value
metadata:
  created_at: "2023-01-01T00:00:00Z"
  updated_at: "2023-01-02T12:00:00Z"
```

## 5. 与 API 的映射关系

### 5.1 命名空间管理 API

| API 端点 | 操作 | 文件系统操作 |
|---------|------|--------------|
| `POST /api/v1/namespace` | 创建命名空间 | 1. 创建目录：`{data_dir}/{namespace}/`<br>2. 更新 `{data_dir}/namespaces.yaml` 添加新命名空间 |
| `GET /api/v1/namespace` | 获取命名空间列表 | 读取 `{data_dir}/namespaces.yaml` |
| `GET /api/v1/namespace/{namespace}` | 获取单个命名空间 | 从 `{data_dir}/namespaces.yaml` 中查找 |
| `PUT /api/v1/namespace/{namespace}` | 更新命名空间 | 更新 `{data_dir}/namespaces.yaml` 中的命名空间信息 |
| `DELETE /api/v1/namespace/{namespace}` | 删除命名空间 | 1. 从 `{data_dir}/namespaces.yaml` 中移除<br>2. 删除目录：`{data_dir}/{namespace}/` |

### 5.2 表管理 API

| API 端点 | 操作 | 文件系统操作 |
|---------|------|--------------|
| `POST /api/v1/table/{namespace}/{table}` | 创建表 | 1. 创建目录：`{data_dir}/{namespace}/{table}/`<br>2. 创建配置文件：`{data_dir}/{namespace}/{table}/config.yaml`<br>3. 创建 Schema 文件：`{data_dir}/{namespace}/{table}/schema.yaml`<br>4. 创建 Records 列表文件：`{data_dir}/{namespace}/{table}/records.yaml`<br>5. 创建 Records 目录：`{data_dir}/{namespace}/{table}/records/`<br>6. 更新 `{data_dir}/{namespace}/tables.yaml` 添加新表 |
| `GET /api/v1/table/{namespace}` | 获取表列表 | 读取 `{data_dir}/{namespace}/tables.yaml` |
| `GET /api/v1/table/{namespace}/{table}` | 获取单个表 | 1. 从 `{data_dir}/{namespace}/tables.yaml` 中查找<br>2. 读取 `{data_dir}/{namespace}/{table}/config.yaml` 和 `schema.yaml` |
| `PUT /api/v1/table/{namespace}/{table}` | 更新表 | 1. 更新 `{data_dir}/{namespace}/tables.yaml` 中的表信息<br>2. 更新 `{data_dir}/{namespace}/{table}/config.yaml` 和 `schema.yaml` |
| `DELETE /api/v1/table/{namespace}/{table}` | 删除表 | 1. 从 `{data_dir}/{namespace}/tables.yaml` 中移除<br>2. 删除目录：`{data_dir}/{namespace}/{table}/` |

### 5.3 数据操作 API

| API 端点 | 操作 | 文件系统操作 |
|---------|------|--------------|
| `POST /api/v1/data/{namespace}/{table}` | 创建数据 | 1. 创建记录文件：`{data_dir}/{namespace}/{table}/records/{record_id}.yaml`<br>2. 更新 `{data_dir}/{namespace}/{table}/records.yaml` 添加新记录 |
| `GET /api/v1/data/{namespace}/{table}` | 列出数据 | 读取 `{data_dir}/{namespace}/{table}/records.yaml` |
| `GET /api/v1/data/{namespace}/{table}/{record_id}` | 获取单个数据 | 读取文件：`{data_dir}/{namespace}/{table}/records/{record_id}.yaml` |
| `PUT /api/v1/data/{namespace}/{table}/{record_id}` | 更新数据 | 1. 更新文件：`{data_dir}/{namespace}/{table}/records/{record_id}.yaml`<br>2. 更新 `{data_dir}/{namespace}/{table}/records.yaml` 中的元数据 |
| `DELETE /api/v1/data/{namespace}/{table}/{record_id}` | 删除数据 | 1. 从 `{data_dir}/{namespace}/{table}/records.yaml` 中移除<br>2. 删除文件：`{data_dir}/{namespace}/{table}/records/{record_id}.yaml` |

## 6. Git 集成

### 6.1 数据完备性检查

提供数据完备性检查功能，确保 Git 仓库中的数据有效：

- **命名空间检查**：验证 `namespaces.yaml` 中的命名空间与实际目录结构一致
- **表检查**：验证 `{namespace}/tables.yaml` 中的表与实际目录结构一致
- **记录检查**：验证 `{namespace}/{table}/records.yaml` 中的记录与实际记录文件一致
- **Schema 验证**：验证所有记录都符合其表的 Schema 定义

```bash
# 运行数据完备性检查
$ takoc check

# 输出示例
✓ 所有命名空间都存在对应目录
✓ 所有表都存在对应目录
✗ 表 mynamespace/mytable 缺少记录文件 record3.yaml
✓ 所有记录都符合 Schema 定义
```

## 7. 格式支持

### 7.1 默认格式

所有文件默认使用 YAML 格式，具有良好的可读性和简洁性。

### 7.2 JSON 格式支持

用户可以在配置中指定使用 JSON 格式：

```yaml
# 全局配置中设置默认格式
storage:
  default_format: "json"

# 或在表配置中单独设置
format:
  schema: "json"
  records: "json"
```

使用 JSON 格式的文件示例：

```json
// record1.json
{
  "id": "record1",
  "data": {
    "field1": "value1",
    "field2": 42
  },
  "metadata": {
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T12:00:00Z"
  }
}
```

## 8. 示例：创建和查询数据

### 8.1 创建命名空间

```bash
# API 请求
POST /api/v1/namespace
Content-Type: application/json

{"name": "mynamespace", "description": "我的第一个命名空间"}

# 文件系统结果
1. 更新 namespaces.yaml 添加新命名空间
2. 创建目录：mynamespace/
3. 创建文件：mynamespace/tables.yaml
```

### 8.2 创建表

```bash
# API 请求
POST /api/v1/table/mynamespace/mytable
Content-Type: application/json

{
  "name": "mytable",
  "description": "我的第一个表",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "age": {"type": "integer"}
    },
    "required": ["name"]
  }
}

# 文件系统结果
1. 创建目录：mynamespace/mytable/
2. 创建文件：mynamespace/mytable/config.yaml
3. 创建文件：mynamespace/mytable/schema.yaml
4. 创建文件：mynamespace/mytable/records.yaml
5. 创建目录：mynamespace/mytable/records/
6. 更新文件：mynamespace/tables.yaml
```

### 8.3 创建记录

```bash
# API 请求
POST /api/v1/data/mynamespace/mytable
Content-Type: application/json

{"name": "John Doe", "age": 30}

# 文件系统结果
1. 创建文件：mynamespace/mytable/records/record123.yaml
2. 更新文件：mynamespace/mytable/records.yaml
```

### 8.4 查询记录

```bash
# API 请求
GET /api/v1/data/mynamespace/mytable/record123

# 文件系统操作
读取文件：mynamespace/mytable/records/record123.yaml
```

## 9. 未来扩展

- 支持 JSON Schema 版本管理
- 支持数据导出和导入
- 实现数据备份和恢复机制
- 支持跨命名空间的数据引用

## 10. 总结

Local Git 存储方案提供了一种简单、直观且与 Git 原生集成的数据存储方式。通过使用专门的列表文件维护数据结构，确保了数据的一致性和完整性。默认使用 YAML 格式提供良好的可读性，同时支持 JSON 格式以满足不同需求。这种方案特别适合中小规模数据的管理，具有易于理解、便于维护和良好的版本控制能力等优点。