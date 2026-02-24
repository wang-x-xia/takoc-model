# API module

## V1

- Base URL: `/api/v1`
- Authentication: Not yet implemented
- Request/Response Format: JSON

Main API List:

- Namespace Management
  - **GET /namespace** Get All Namespaces
  - **GET/POST/PUT/DELETE /namespace/{namespace}** Create/Get/Update/Delete Namespace
- Table Management
  - **GET /table/{namespace}** Get All Tables
  - **POST/GET/PUT/DELETE /table/{namespace}/{table}** Create/Get/Update/Delete Table
- Record Operations
  - **POST/GET/PUT/DELETE /record/{namespace}/{table}/{record_id}** Create/Get/Update/Delete Record
  - **GET /record/{namespace}/{table}** List All Records of Table

## Built-in Namespace

The system provides a special Namespace named `takoc` by default for managing system metadata. This Namespace contains
the following three Tables:

- **config**: Stores system configuration information
- **namespace**: Stores metadata for all created Namespaces
- **table**: Stores metadata for all created Tables

## Directory Layout

`v1.yaml` is the complete V1 API documentation, provided in OpenAPI 3.0 YAML format.

`v1.py` is the Python interface for V1 API.
Each concept should have a corresponding `pydantic` model in `v1.py`.
Each method should correspond to an API endpoint.

`v1_app.py` is the FastAPI application for V1 API.