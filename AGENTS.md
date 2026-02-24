# Takoc

Takoc is a simple JSON database specification with several local implementations.

The Takoc specification is designed to be simple and flexible:

1. If mainly defined by HTTP APIs, and also provide SDKs for other languages.
2. Provide several toolkits to access the HTTP APIs, including CLI, GUI.

## Project Rules

- Only use English in the code and comments.

- This is a Python project.
  - This project uses `uv`, don't call `pip` directly.
  - Use relative import in the python code.
  - Directly use dict or list for typing. Avoid Dict and List in typing module.
  - Interface should use `I` as prefix.
  - Use `pydantic` for data models.
  - Data models should use suffix Base/Data/Request/Response.

## Project Concepts

Basically, the Takoc uses **Table** to manage **Record**s.

- **Table**: A table is a collection of records with specific data type.
- **Record**: A record is a data entity. In Takoc, the record operation is atomic—always applied to the entire record; partial byte-level or field-level updates are not supported (field-level changes may be possible but are discouraged).
- **ID**: A unique identifier for each record in a table. Recommended to have a meaninful ID.

Above **Table**, we have more control resources, such as:

- **Namespace**: A namespace is a logical container for tables.
- **Database**: A database is a collection of namespaces. Each HTTP endpoint corresponds to a database.

## Project layout

**/src/api** defines the Takoc spec.

**/src/local** defines the Takoc impl of Local Yaml files.
