import shutil
from pathlib import Path

from .db import TakocLocalDb
from .file_io import Files
from ..api.v1 import INamespace, ITable, TableData, TableCreateRequest, TableUpdateRequest


class Namespace(INamespace):
    """Namespace APIs"""

    def __init__(self, db: TakocLocalDb, name: str, dir: Path):
        """Initialize namespace

        Args:
            db: TakocLocalDb instance
            name: Namespace name
            dir: Namespace directory path
        """
        self._db = db
        self._name = name
        self._files = Files(
            dir=dir, read_only=db.read_only, format=db.global_config.default_format)

    @classmethod
    def initialize(cls, db: TakocLocalDb, name: str, dir: Path) -> 'Namespace':
        """Create new namespace

        Args:
            db: TakocLocalDb instance
            name: Namespace name
            dir: Namespace directory path

        Returns:
            Created namespace instance
        """
        # Create namespace directory
        dir.mkdir(parents=True, exist_ok=True)

        # Initialize namespace file manager
        namespace = cls(db=db, name=name, dir=dir)

        # No need to create initial tables file - metadata will handle it

        return namespace

    @property
    def name(self) -> str:
        """Get namespace name

        Returns:
            Namespace name
        """
        return self._name

    def create_table(self, create: TableCreateRequest) -> None:
        """Create new table

        Args:
            create: Table creation data

        Returns:
            None

        Raises:
            ValueError: Table already exists
        """
        from .table import Table

        # Use metadata to add table
        self._db.metadata.add_table(self._name, create.name, create.description)

        # Create table directory
        table_dir = self._files.dir / create.name

        # Use Table class method to create table
        Table.initialize(self._db, table_dir)

    def list_tables(self) -> list[TableData]:
        """Get list of all tables in namespace

        Returns:
            List of tables
        """
        tables_metadata = self._db.metadata.get_tables(self._name)
        return [TableData(name=table.name, description=table.description, namespace=self._name) for table in
                tables_metadata]

    def get_table(self, name: str) -> TableData | None:
        """Get single table instance

        Args:
            name: Table name

        Returns:
            Table information or None if not found
        """
        table = self._db.metadata.get_table(self._name, name)
        if table:
            return TableData(name=table.name, description=table.description, namespace=self._name)
        return None

    def update_table(self, name: str, update: TableUpdateRequest) -> None:
        """Update table information

        Args:
            name: Table name
            update: Table update data

        Raises:
            ValueError: Table not found
        """
        # Use metadata to update table
        self._db.metadata.update_table(self._name, name, update.description)

    def delete_table(self, name: str) -> None:
        """Delete table

        Args:
            name: Table name

        Raises:
            ValueError: Table not found
        """
        # Use metadata to delete table
        self._db.metadata.delete_table(self._name, name)

        # Delete table directory
        table_dir = self._files.dir / name
        if table_dir.exists():
            shutil.rmtree(table_dir)

    def load_table(self, table: str) -> ITable:
        """Get record data access object for a specific table

        Args:
            table: Table name

        Returns:
            ITable implementation for the table

        Raises:
            ValueError: Table not found
        """
        from .table import Table
        table_metadata = self._db.metadata.get_table(self._name, table)
        if table_metadata:
            table_dir = self._files.dir / table_metadata.path
            return Table(self._db, table_dir)
        raise ValueError(f"Table '{table}' not found in namespace '{self._name}'")
