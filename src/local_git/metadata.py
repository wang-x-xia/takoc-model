from typing import Any

from pydantic import BaseModel

from .db import TakocLocalDb
from .file_io import Files
from ..api.v1 import INamespace, ITable, TableData, TableCreateRequest, TableUpdateRequest, NamespaceData, \
    NamespaceCreateRequest, NamespaceUpdateRequest


class NamespaceMetadata(BaseModel):
    """Namespace metadata class"""
    name: str
    description: str = ""
    path: str = ""


class NamespacesMetadata(BaseModel):
    """Namespace list class"""
    namespaces: list[NamespaceMetadata] = []


class TableMetadata(BaseModel):
    """Table metadata class"""
    name: str
    description: str = ""
    path: str = ""
    json_schema: dict | None = None


class TablesMetadata(BaseModel):
    """Table list class"""
    tables: list[TableMetadata] = []


class Metadata:
    """
    Use this class to manage the Takoc metadata.

    Including the Takoc namespaces, tables.

    This API access the fixed 'takoc' metadata folder within the data directory.
    """

    def __init__(self, db: TakocLocalDb):
        self.db = db
        # Use fixed metadata directory 'takoc' inside data directory
        self.metadata_dir = db.global_config.data_dir / "takoc"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Initialize file manager for metadata folder
        self._files = Files(
            dir=self.metadata_dir,
            read_only=db.read_only,
            format=db.global_config.default_format
        )

    def get_namespaces(self) -> list[NamespaceMetadata]:
        """
        Get metadata for all namespaces.

        Returns:
            List of NamespaceMetadata objects.
        """
        data = self._files.read_file("namespaces")
        namespaces_data = NamespacesMetadata(
            **data) if data else NamespacesMetadata()
        return namespaces_data.namespaces

    def get_namespace(self, name: str) -> NamespaceMetadata | None:
        """
        Get metadata for a specific namespace.

        Args:
            name: Namespace name

        Returns:
            NamespaceMetadata object if found, None otherwise.
        """
        namespaces = self.get_namespaces()
        for ns in namespaces:
            if ns.name == name:
                return ns
        return None

    def add_namespace(self, name: str, description: str = "") -> None:
        """
        Add a new namespace to metadata.

        Args:
            name: Namespace name
            description: Namespace description
        """
        # Load existing namespaces
        data = self._files.read_file("namespaces")
        namespaces_data = NamespacesMetadata(
            **data) if data else NamespacesMetadata()

        # Check if namespace already exists
        for ns in namespaces_data.namespaces:
            if ns.name == name:
                raise ValueError(f"Namespace '{name}' already exists")

        # Add new namespace
        new_namespace = NamespaceMetadata(
            name=name, description=description, path=name)
        namespaces_data.namespaces.append(new_namespace)

        # Save updated namespaces
        self._files.write_file("namespaces", namespaces_data.model_dump())

    def update_namespace(self, name: str, description: str) -> None:
        """
        Update an existing namespace in metadata.

        Args:
            name: Namespace name
            description: New namespace description
        """
        # Load existing namespaces
        data = self._files.read_file("namespaces")
        namespaces_data = NamespacesMetadata(
            **data) if data else NamespacesMetadata()

        # Find and update the namespace
        found = False
        for ns in namespaces_data.namespaces:
            if ns.name == name:
                ns.description = description
                found = True
                break

        if not found:
            raise ValueError(f"Namespace '{name}' not found")

        # Save updated namespaces
        self._files.write_file("namespaces", namespaces_data.model_dump())

    def delete_namespace_meta(self, name: str) -> None:
        """
        Delete namespace metadata.

        Args:
            name: Namespace name
        """
        # Load existing namespaces
        data = self._files.read_file("namespaces")
        namespaces_data = NamespacesMetadata(
            **data) if data else NamespacesMetadata()

        # Remove the namespace
        original_count = len(namespaces_data.namespaces)
        namespaces_data.namespaces = [
            ns for ns in namespaces_data.namespaces if ns.name != name]

        if len(namespaces_data.namespaces) == original_count:
            raise ValueError(f"Namespace '{name}' not found")

        # Save updated namespaces
        self._files.write_file("namespaces", namespaces_data.model_dump())

        # Also delete the tables file for this namespace if it exists
        tables_file = f"{name}_tables"
        if self._files.file_info(tables_file):
            self._files.delete_file(tables_file)

    def get_tables(self, namespace: str) -> list[TableMetadata]:
        """
        Get metadata for all tables in a specific namespace.

        Args:
            namespace: Name of the namespace.

        Returns:
            List of TableMetadata objects.
        """
        table_file = f"{namespace}_tables"
        data = self._files.read_file(table_file)
        tables_data = TablesMetadata(**data) if data else TablesMetadata()
        return tables_data.tables

    def get_table(self, namespace: str, name: str) -> TableMetadata | None:
        """
        Get metadata for a specific table in a namespace.

        Args:
            namespace: Namespace name
            name: Table name

        Returns:
            TableMetadata object if found, None otherwise.
        """
        tables = self.get_tables(namespace)
        for table in tables:
            if table.name == name:
                return table
        return None

    def add_table(self, namespace: str, name: str, description: str = "") -> None:
        """
        Add a new table to a namespace's metadata.

        Args:
            namespace: Namespace name
            name: Table name
            description: Table description
        """
        table_file = f"{namespace}_tables"

        # Load existing tables
        data = self._files.read_file(table_file)
        tables_data = TablesMetadata(**data) if data else TablesMetadata()

        # Check if table already exists
        for table in tables_data.tables:
            if table.name == name:
                raise ValueError(
                    f"Table '{name}' already exists in namespace '{namespace}'")

        # Add new table
        new_table = TableMetadata(
            name=name, description=description, path=name)
        tables_data.tables.append(new_table)

        # Save updated tables
        self._files.write_file(table_file, tables_data.model_dump())

    def update_table(self, namespace: str, name: str, description: str) -> None:
        """
        Update an existing table in a namespace's metadata.

        Args:
            namespace: Namespace name
            name: Table name
            description: New table description
        """
        table_file = f"{namespace}_tables"

        # Load existing tables
        data = self._files.read_file(table_file)
        tables_data = TablesMetadata(**data) if data else TablesMetadata()

        # Find and update the table
        found = False
        for table in tables_data.tables:
            if table.name == name:
                table.description = description
                found = True
                break

        if not found:
            raise ValueError(
                f"Table '{name}' not found in namespace '{namespace}'")

        # Save updated tables
        self._files.write_file(table_file, tables_data.model_dump())

    def delete_table(self, namespace: str, name: str) -> None:
        """
        Delete a table from a namespace's metadata.

        Args:
            namespace: Namespace name
            name: Table name
        """
        table_file = f"{namespace}_tables"

        # Load existing tables
        data = self._files.read_file(table_file)
        tables_data = TablesMetadata(**data) if data else TablesMetadata()

        # Remove the table
        original_count = len(tables_data.tables)
        tables_data.tables = [
            table for table in tables_data.tables if table.name != name]

        if len(tables_data.tables) == original_count:
            raise ValueError(
                f"Table '{name}' not found in namespace '{namespace}'")

        # Save updated tables
        self._files.write_file(table_file, tables_data.model_dump())

    def get_metadata_namespace(self) -> INamespace:
        """
        Get the special 'takoc' metadata namespace.

        Returns:
            INamespace implementation for the metadata namespace.
        """
        return MetadataNamespace(self)


class NamespacesTable(ITable):
    """ITable implementation for namespace records"""

    def __init__(self, metadata: Metadata):
        self._metadata = metadata

    @property
    def namespace(self) -> str:
        return "takoc"

    @property
    def name(self) -> str:
        return "namespace"

    def list_records(self) -> list[str]:
        namespaces = self._metadata.get_namespaces()
        return [ns.name for ns in namespaces]

    def get_record(self, record_id: str) -> Any:
        namespace = self._metadata.get_namespace(record_id)
        if namespace:
            return NamespaceData(name=namespace.name, description=namespace.description).model_dump()
        raise ValueError(f"Namespace '{record_id}' not found")

    def create_record(self, record_id: str, data: Any) -> None:
        create_req = NamespaceCreateRequest(**data)
        if create_req.name != record_id:
            raise ValueError(f"Record ID '{record_id}' must match namespace name '{create_req.name}'")
        self._metadata.add_namespace(create_req.name, create_req.description)

    def update_record(self, record_id: str, data: Any) -> None:
        update_req = NamespaceUpdateRequest(**data)
        self._metadata.update_namespace(record_id, update_req.description)

    def delete_record(self, record_id: str) -> None:
        self._metadata.delete_namespace_meta(record_id)


class TablesTable(ITable):
    """ITable implementation for table records"""

    def __init__(self, metadata: Metadata):
        self._metadata = metadata

    @property
    def namespace(self) -> str:
        return "takoc"

    @property
    def name(self) -> str:
        return "table"

    def list_records(self) -> list[str]:
        all_tables = []
        namespaces = self._metadata.get_namespaces()
        for ns in namespaces:
            tables = self._metadata.get_tables(ns.name)
            for table in tables:
                all_tables.append(f"{ns.name}.{table.name}")
        return all_tables

    def get_record(self, record_id: str) -> Any:
        if "." not in record_id:
            raise ValueError(f"Invalid table record ID format: '{record_id}'. Use 'namespace.table' format.")
        namespace, table_name = record_id.split(".", 1)
        table = self._metadata.get_table(namespace, table_name)
        if table:
            return TableData(name=table.name, description=table.description, namespace=namespace).model_dump()
        raise ValueError(f"Table '{record_id}' not found")

    def create_record(self, record_id: str, data: Any) -> None:
        if "." not in record_id:
            raise ValueError(f"Invalid table record ID format: '{record_id}'. Use 'namespace.table' format.")
        namespace, table_name = record_id.split(".", 1)
        create_req = TableCreateRequest(**data)
        if create_req.name != table_name:
            raise ValueError(f"Record ID table name '{table_name}' must match table name '{create_req.name}'")
        self._metadata.add_table(namespace, create_req.name, create_req.description)

    def update_record(self, record_id: str, data: Any) -> None:
        if "." not in record_id:
            raise ValueError(f"Invalid table record ID format: '{record_id}'. Use 'namespace.table' format.")
        namespace, table_name = record_id.split(".", 1)
        update_req = TableUpdateRequest(**data)
        self._metadata.update_table(namespace, table_name, update_req.description)

    def delete_record(self, record_id: str) -> None:
        if "." not in record_id:
            raise ValueError(f"Invalid table record ID format: '{record_id}'. Use 'namespace.table' format.")
        namespace, table_name = record_id.split(".", 1)
        self._metadata.delete_table(namespace, table_name)


class MetadataNamespace(INamespace):
    """INamespace implementation for metadata namespace"""

    def __init__(self, metadata: Metadata):
        self._metadata = metadata
        self._name = "takoc"

    @property
    def name(self) -> str:
        return self._name

    def list_tables(self) -> list[TableData]:
        return [
            TableData(name="namespace", description="Stores all namespace records", namespace=self._name),
            TableData(name="table", description="Stores all table records", namespace=self._name)
        ]

    def get_table(self, name: str) -> TableData | None:
        if name in ["namespace", "table"]:
            if name == "namespace":
                return TableData(name="namespace", description="Stores all namespace records", namespace=self._name)
            else:
                return TableData(name="table", description="Stores all table records", namespace=self._name)
        return None

    def create_table(self, create: TableCreateRequest) -> None:
        raise ValueError("Cannot create tables in the 'takoc' metadata namespace")

    def update_table(self, name: str, update: TableUpdateRequest) -> None:
        raise ValueError("Cannot update tables in the 'takoc' metadata namespace")

    def delete_table(self, name: str) -> None:
        raise ValueError("Cannot delete tables in the 'takoc' metadata namespace")

    def load_table(self, table: str) -> ITable:
        if table == "namespace":
            return NamespacesTable(self._metadata)
        elif table == "table":
            return TablesTable(self._metadata)
        raise ValueError(f"Table '{table}' not found in namespace '{self._name}'")
