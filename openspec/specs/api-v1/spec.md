# api-v1 Specification

## Purpose

Define the Takoc specification.
V1 is for compatibility if future versions break backward compatibility.

## Requirements

### Requirement: API v1 Base Configuration

The API v1 SHALL have the following base configuration:

- Base URL: `/api/v1`
- Authentication: Not yet implemented
- Request/Response Format: JSON

#### Scenario: API v1 Base URL

- **WHEN** a client sends a request to `/api/v1`
- **THEN** the system SHALL route the request to the API v1 implementation

### Requirement: Namespace Management API

The API v1 SHALL provide the following endpoints for namespace management:

- **GET /namespace** Get All Namespaces
- **GET/POST/PUT/DELETE /namespace/{namespace}** Create/Get/Update/Delete Namespace

#### Scenario: Get All Namespaces

- **WHEN** a client sends a GET request to `/api/v1/namespace`
- **THEN** the system SHALL return a list of all namespaces

#### Scenario: Create Namespace

- **WHEN** a client sends a POST request to `/api/v1/namespace/{namespace}`
- **THEN** the system SHALL create a new namespace with the specified name

### Requirement: Table Management API

The API v1 SHALL provide the following endpoints for table management:

- **GET /table/{namespace}** Get All Tables
- **POST/GET/PUT/DELETE /table/{namespace}/{table}** Create/Get/Update/Delete Table

#### Scenario: Get All Tables

- **WHEN** a client sends a GET request to `/api/v1/table/{namespace}`
- **THEN** the system SHALL return a list of all tables in the specified namespace

#### Scenario: Create Table

- **WHEN** a client sends a POST request to `/api/v1/table/{namespace}/{table}`
- **THEN** the system SHALL create a new table with the specified name in the specified namespace

### Requirement: Record Operations API

The API v1 SHALL provide the following endpoints for record operations:

- **POST/GET/PUT/DELETE /record/{namespace}/{table}/{record_id}** Create/Get/Update/Delete Record
- **GET /record/{namespace}/{table}** List All Records of Table

#### Scenario: Get Record

- **WHEN** a client sends a GET request to `/api/v1/record/{namespace}/{table}/{record_id}`
- **THEN** the system SHALL return the record with the specified ID from the specified table and namespace

#### Scenario: List All Records

- **WHEN** a client sends a GET request to `/api/v1/record/{namespace}/{table}`
- **THEN** the system SHALL return a list of all records in the specified table and namespace

### Requirement: Built-in Namespace

The system SHALL provide a special Namespace named `takoc` by default for managing system metadata. This Namespace SHALL contain the following three Tables:

- **config**: Stores system configuration information
- **namespace**: Stores metadata for all created Namespaces
- **table**: Stores metadata for all created Tables

#### Scenario: Access Built-in Namespace

- **WHEN** a client sends a request to access the `takoc` namespace
- **THEN** the system SHALL allow access to the built-in namespace and its tables

### Requirement: API v1 Implementation Structure

The API v1 implementation SHALL follow the following structure:

- `v1.yaml`: Complete V1 API documentation in OpenAPI 3.0 YAML format
- `v1.py`: Python interface for V1 API with corresponding pydantic models
- `v1_app.py`: FastAPI application for V1 API

#### Scenario: API v1 File Structure

- **WHEN** the system is initialized
- **THEN** the API v1 implementation files SHALL be present in the correct structure
