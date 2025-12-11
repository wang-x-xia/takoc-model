# Store API v1

## Overview

Store API v1 is a RESTful-style database API that provides Namespace management, Table management, and data CRUD
operations.

## Basic Information

- API Version: v1
- Base URL: `/api/v1`
- Authentication: Not yet implemented
- Request/Response Format: JSON

## Main API List

- Namespace Management
  - Create Namespace
  - Get All Namespaces
  - Get Single Namespace
  - Update Namespace
  - Delete Namespace
- Table Management
  - Create Table
  - Get All Tables
  - Get Single Table
  - Update Table
  - Delete Table
- Record Operations
  - Create Record
  - List All Records
  - Update Record
  - Delete Record

## Built-in Namespace

The system provides a special Namespace named `takoc` by default for managing system metadata. This Namespace contains
the following three Tables:

- **config**: Stores system configuration information
- **namespace**: Stores metadata for all created Namespaces
- **table**: Stores metadata for all created Tables

## Detailed Documentation

The complete API documentation is provided in OpenAPI 3.0 YAML format, please check:
`src/api/v1.yaml`
