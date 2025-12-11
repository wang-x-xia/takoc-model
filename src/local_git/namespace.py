import shutil
from pathlib import Path

from .db import TakocLocalDb
from .file_io import Files


class Namespace:
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

    def create_table(self, name: str, description: str = "") -> 'Table':
        """Create new table

        Args:
            name: Table name
            description: Table description

        Returns:
            Created table instance

        Raises:
            ValueError: Table already exists
        """
        from .table import Table

        # Use metadata to add table
        self._db.metadata.add_table(self._name, name, description)

        # Create table directory
        table_dir = self._files.dir / name

        # Use Table class method to create table
        return Table.initialize(self._db, table_dir)

    def list_tables(self) -> list[str]:
        """Get list of all tables in namespace

        Returns:
            List of table names
        """
        tables = self._db.metadata.get_tables(self._name)
        return [table.name for table in tables]

    def get_table(self, name: str):
        """Get single table instance

        Args:
            name: Table name

        Returns:
            Table instance

        Raises:
            ValueError: Table not found
        """
        from .table import Table
        tables = self._db.metadata.get_tables(self._name)
        for table in tables:
            if table.name == name:
                table_dir = self._files.dir / table.path
                return Table(self._db, dir=table_dir)
        raise ValueError(f"Table '{name}' not found in namespace")

    def update_table(self, name: str, description: str) -> None:
        """Update table information

        Args:
            name: Table name
            description: New description

        Raises:
            ValueError: Table not found
        """
        # Use metadata to update table
        self._db.metadata.update_table(self._name, name, description)

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
