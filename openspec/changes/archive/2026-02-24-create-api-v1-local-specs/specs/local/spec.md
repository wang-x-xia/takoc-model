## ADDED Requirements

### Requirement: Format Flexibility
The Local Git storage solution SHALL support JSON and YAML formats, with YAML as the default.

#### Scenario: YAML Format
- **WHEN** the system stores data
- **THEN** the system SHALL use YAML format by default

#### Scenario: JSON Format
- **WHEN** the system is configured to use JSON format
- **THEN** the system SHALL store data in JSON format

### Requirement: Static Linking
The Local Git storage solution SHALL use static linking, where all files are referenced directly by files, without relying on list files or list folders.

#### Scenario: Static Linking
- **WHEN** the system references files
- **THEN** the system SHALL reference files directly without using list files or folders

### Requirement: Default File Layout
The Local Git storage solution SHALL use the following default file layout:
- `takoc.yaml`: Global configuration file
- `takoc/`: Metadata directory
  - `namespaces.yaml`: Namespace list
  - `mynamespace_tables.yaml`: Tables for mynamespace
- `mynamespace/`: Namespace directory
  - `mytable/`: Table directory
    - `records.yaml`: Records list
    - `record1.yaml`: Record files
    - `record2.yaml`:

#### Scenario: Default File Layout
- **WHEN** the system initializes
- **THEN** the system SHALL create files according to the default file layout

### Requirement: Custom Storage Location
The Local Git storage solution SHALL allow users to store data in a specific directory through the global configuration file.

#### Scenario: Custom Storage Location
- **WHEN** the user configures a custom storage location in takoc.yaml
- **THEN** the system SHALL store data in the specified directory

### Requirement: Metadata Storage
The Local Git storage solution SHALL store metadata in the `takoc/` directory, including namespace and table metadata.

#### Scenario: Metadata Storage
- **WHEN** the system creates or updates namespaces or tables
- **THEN** the system SHALL store the metadata in the appropriate files in the `takoc/` directory

### Requirement: Record Storage
The Local Git storage solution SHALL store records in the appropriate table directories, with each record in its own file.

#### Scenario: Record Storage
- **WHEN** the system creates or updates records
- **THEN** the system SHALL store each record in its own file in the appropriate table directory
