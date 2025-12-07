from pathlib import Path
import shutil
from typing import Any, Dict, List

from pydantic import BaseModel

from .db import TakocLocalDb
from .file_io import Files


class TableMetadata(BaseModel):
    """Table metadata class"""
    name: str
    description: str = ""
    path: str = ""


class TablesMetadata(BaseModel):
    """Table list class"""
    tables: list[TableMetadata] = []


class Namespace:
    """Namespace APIs"""

    def __init__(self, db: TakocLocalDb, dir: Path, read_only: bool = False):
        """Initialize namespace

        Args:
            db: TakocLocalDb instance
        """
        self._db = db
        self._files = Files(
            dir=dir, read_only=read_only, format=db.global_config.default_format)
        self.tables_file = "tables"  # Without extension

    def _load_tables(self) -> TablesMetadata:
        """Load tables list"""
        data = self._files.read_file(self.tables_file)
        return TablesMetadata(**data) if data else TablesMetadata()

    def _save_tables(self, tables_data: TablesMetadata) -> None:
        """Save tables list"""
        self._files.write_file(
            self.tables_file, tables_data.model_dump())

    @classmethod
    def initialize(cls, db: TakocLocalDb,  dir: Path) -> 'Namespace':
        """Create new namespace

        Args:
            db: TakocLocalDb instance
            dir: Namespace directory path

        Returns:
            Created namespace instance
        """
        # Create namespace directory
        dir.mkdir(parents=True, exist_ok=True)

        # Initialize namespace file manager
        namespace = cls(db=db, dir=dir, read_only=False)

        # Create initial tables list file
        tables_data = TablesMetadata()
        namespace._save_tables(tables_data)

        return namespace

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
        table_info = TableMetadata(
            name=name,
            description=description,
            path=name,
        )

        # Load existing tables list
        tables_data = self._load_tables()

        # Check if table already exists
        for table in tables_data.tables:
            if table.name == name:
                raise ValueError(f"Table '{name}' already exists in namespace")

        # Add new table
        tables_data.tables.append(table_info)
        self._save_tables(tables_data)

        # Create table directory
        table_dir = self._files.dir / name

        # Use Table class method to create table
        return Table.initialize(self._db, table_dir)

    def list_tables(self) -> List[str]:
        """Get list of all tables in namespace

        Returns:
            List of table names
        """
        tables_data = self._load_tables()
        return [table.name for table in tables_data.tables]

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
        tables_data = self._load_tables()
        for table in tables_data.tables:
            if table.name == name:
                table_dir = self._files.dir / table.path
                return Table(self._db, dir=table_dir, read_only=False)
        raise ValueError(f"Table '{name}' not found in namespace")

    def update_table(self, name: str, description: str) -> None:
        """Update table information

        Args:
            name: Table name
            description: New description

        Raises:
            ValueError: Table not found
        """
        tables_data = self._load_tables()

        for table in tables_data.tables:
            if table.name == name:
                table.description = description
                self._save_tables(tables_data)

                # Table description already updated in tables.yaml, no need to update config file

                return
        raise ValueError(f"Table '{name}' not found in namespace")

    def delete_table(self, name: str) -> None:
        """Delete table

        Args:
            name: Table name

        Raises:
            ValueError: Table not found
        """
        tables_data = self._load_tables()

        # Check if table exists
        after_delete_tables = [
            table for table in tables_data.tables if table.name != name]

        if len(after_delete_tables) == len(tables_data.tables):
            raise ValueError(f"Table '{name}' not found in namespace")

        tables_data.tables = after_delete_tables
        self._save_tables(tables_data)

        # Delete table directory
        table_dir = self._files.dir / name
        if table_dir.exists():
            shutil.rmtree(table_dir)
