# JSON Schema 类型系统（简化版）

## 核心概念

JSON Schema（最新版本 Draft 2020-12）是一种**验证工具**，而非严格的类型定义语言。它用于检查 JSON 数据是否符合预期的结构和约束，而不是强制定义数据必须如何构建。

## 主要特点

- **验证导向**：关注数据的「有效性」而非「定义性」
- **灵活约束**：支持从宽松到严格的各种验证规则
- **版本演进**：持续更新以支持更复杂的验证场景

## 通配符示例：验证而非定义

以下示例展示了 JSON Schema 作为验证工具的特性，使用「通配符」概念来接受多种结构的有效数据：

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "灵活的用户数据验证",
  "description": "验证用户数据，但不严格定义其结构",
  
  "type": "object",
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "contact": {
      "type": "object",
      "anyOf": [
        { "required": ["email"] },
        { "required": ["phone"] },
        { "required": ["address"] }
      ],
      "additionalProperties": true  // 允许任意额外的联系信息字段
    }
  },
  "required": ["id", "name"],
  
  "additionalProperties": true  // 通配符：允许任意额外的用户属性
}
```

### 这个示例的意义

1. **不严格定义结构**：使用 `additionalProperties: true` 允许对象包含 schema 中未明确列出的任意字段

2. **灵活的验证规则**：`contact` 对象只要求至少提供一种联系方式（email/phone/address），但可以包含更多

3. **验证而非限制**：数据可以有各种额外属性（如 `age`, `gender`, `preferences` 等），只要满足基本验证条件即可通过

## 验证场景对比

| 场景 | JSON Schema 行为 |
|------|-----------------|
| 严格定义结构 | ❌ 不是核心目标 |
| 验证数据有效性 | ✅ 核心功能 |
| 接受灵活数据格式 | ✅ 支持通配符和条件规则 |
| 强制数据结构 | ❌ 通常避免过度约束 |

## 总结

JSON Schema 是一个强大的**数据验证工具**，其设计理念是「验证数据是否有效」而非「强制数据必须如何定义」。通过通配符和灵活的验证规则，它能够适应各种数据结构，同时确保核心数据质量和一致性。
