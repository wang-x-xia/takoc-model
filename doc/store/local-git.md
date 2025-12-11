# Local Git Storage Solution

## Core Design Principles

The Local Git storage solution is based on the following core principles:

- **Format Flexibility**: Supports JSON and YAML formats, with YAML as the default
- **Static Linking**: All files are referenced directly by files, without relying on list files or list folders

## File Layout

### Default File Layout

Data is directly stored in the repository root by default:

```
takoc.yaml                 # Global configuration file
takoc/                     # Metadata directory
├── namespaces.yaml        # Namespace list
└── mynamespace_tables.yaml # Tables for mynamespace
mynamespace/               # Namespace directory
└── mytable/               # Table directory
    ├── records.yaml       # Records list
    ├── record1.yaml       # Record files
    ├── record2.yaml
    └── ...
anothernamespace/          # Another Namespace directory
└── ...
```

### Custom Storage Location

Users can store data in a specific directory through the global configuration file:

```
takoc.yaml
└── data/                  # User-defined data directory
    ├── takoc/             # Metadata directory
    │   ├── namespaces.yaml
    │   └── mynamespace_tables.yaml
    ├── mynamespace/
    │   └── mytable/
    │       ├── records.yaml
    │       ├── record1.yaml
    │       └── ...
    └── ...
```
