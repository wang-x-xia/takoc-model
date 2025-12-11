# JSON Schema Type System (Simplified Version)

## Core Concepts

JSON Schema (latest version Draft 2020-12) is a **validation tool** rather than a strict type definition language. It is
used to check whether JSON data conforms to expected structures and constraints, rather than forcing how data must be
structured.

## Main Features

- **Validation-oriented**：Focus on data "validity" rather than "definition"
- **Flexible constraints**：Support various validation rules from loose to strict
- **Version evolution**：Continuous updates to support more complex validation scenarios

## Wildcard Example: Validation Rather Than Definition

The following example demonstrates the characteristics of JSON Schema as a validation tool, using the concept of "
wildcards" to accept valid data with various structures:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Flexible User Data Validation",
  "description": "Validate user data without strictly defining its structure",
  
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
      "additionalProperties": true  // Allow any additional contact information fields
    }
  },
  "required": ["id", "name"],
  
  "additionalProperties": true  // Wildcard: Allow any additional user attributes
}
```

### The Significance of This Example

1. **Does not strictly define structure**：Uses `additionalProperties: true` to allow objects to contain any fields not
   explicitly listed in the schema

2. **Flexible validation rules**：The `contact` object only requires at least one contact method (email/phone/address),
   but can contain more

3. **Validation rather than restriction**：Data can have various additional properties (such as `age`, `gender`,
   `preferences`, etc.) as long as it meets the basic validation conditions

## Validation Scenario Comparison

| Scenario                     | JSON Schema Behavior                      |
|------------------------------|-------------------------------------------|
| Strict structure definition  | ❌ Not a core goal                         |
| Data validity verification   | ✅ Core functionality                      |
| Accept flexible data formats | ✅ Support wildcards and conditional rules |
| Force data structure         | ❌ Usually avoid over-constraints          |

## Summary

JSON Schema is a powerful **data validation tool** whose design philosophy is to "validate whether data is valid" rather
than "force how data must be defined". Through wildcards and flexible validation rules, it can adapt to various data
structures while ensuring core data quality and consistency.
