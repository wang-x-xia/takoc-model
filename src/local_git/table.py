from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .db import TakocLocalDb
from .file_io import Files, FILE_FORMAT
from ..api.v1 import ITable


class TableMeta(BaseModel):
    """Table metadata"""
    records_format: FILE_FORMAT = "yaml"
    json_schema: dict | None = None
    path: str | None = None

    @classmethod
    def load(cls, files: Files) -> 'TableMeta':
        """Load table metadata from file

        Args:
            files: Files instance

        Returns:
            Table metadata object
        """
        return cls(**files.read_file("takoc"))


class RecordPos(BaseModel):
    id: str
    file: str


class Records(BaseModel):
    records: list[RecordPos] = []


class Table(ITable):
    """Table APIs"""

    def __init__(self, db: TakocLocalDb, dir: Path):
        """Initialize table

        Args:
            db: TakocLocalDb instance
            dir: Table directory path
        """
        self._db = db
        self._dir = dir
        self._meta = TableMeta.load(Files(dir=dir, read_only=True))

        self._files = Files(
            dir=self._dir / self._meta.path if self._meta.path else self._dir,
            read_only=db.read_only,
            format=self._meta.records_format if self._meta.records_format else self._db.global_config.default_format)

        self._schema = self._meta.json_schema

        # Extract namespace and table name from path
        self._namespace = dir.parent.name
        self._table_name = dir.name

    @classmethod
    def initialize(cls, db: TakocLocalDb, dir: Path) -> 'Table':
        """Create a new table

        Args:
            db: TakocLocalDb instance
            dir: Table directory path

        Returns:
            Created table instance
        """
        # Create table directory
        dir.mkdir(parents=True, exist_ok=True)

        # Initialize table metadata
        files = Files(
            dir=dir, read_only=False, format=db.global_config.default_format)

        # Create table metadata file
        table_meta = TableMeta()
        files.write_file("takoc", table_meta.model_dump())

        # Create empty records list file
        empty_records = Records(records=[])
        files.write_file("records", empty_records.model_dump())

        # Create and return table instance
        return cls(db=db, dir=dir)

    @property
    def json_schema(self) -> dict | None:
        return self._schema

    @property
    def namespace(self) -> str:
        """Get namespace name

        Returns:
            Namespace name
        """
        return self._namespace

    @property
    def name(self) -> str:
        """Get table name

        Returns:
            Table name
        """
        return self._table_name

    def _get_records(self) -> Records:
        """Get all records

        Returns:
            Record list object
        """
        return Records(**self._files.read_file("records"))

    def _get_record(self, record_id: str, records: Records = None) -> RecordPos | None:
        """Get record position

        Args:
            record_id: Record ID

        Returns:
            Record position object
        """
        if records is None:
            records = self._get_records()
        for record in records.records:
            if record.id == record_id:
                return record
        return None

    def _update_records(self, records: Records) -> None:
        """Update record list

        Args:
            records: Record list object
        """
        self._files.write_file("records", records.model_dump())

    def list_records(self) -> list[str]:
        """Get all records in the table

        Returns:
            List of record IDs
        """
        return [record.id for record in self._get_records().records]

    def get_record(self, record_id: str) -> Any:
        """Get a specific record

        Args:
            record_id: Record ID

        Returns:
            Record data

        Raises:
            ValueError: Record not found
        """
        record = self._files.read_file(record_id)
        if record is None:
            raise ValueError(f"Record '{record_id}' not found in table")
        return record

    def create_record(self, record_id: str, data: Any) -> None:
        """Create a new record

        Args:
            record_id: Record ID
            data: Record data

        Returns:
            None
        """
        records = self._get_records()
        record = self._get_record(record_id, records=records)
        if record is not None:
            raise ValueError(f"Record '{record_id}' already exists")

        file_name = self._files.generate_file_name(record_id)
        records.records.append(RecordPos(id=record_id, file=file_name))
        self._update_records(records)

        self._files.write_file(file_name, data)

    def update_record(self, record_id: str, data: Any) -> None:
        """Update a record

        Args:
            record_id: Record ID
            data: New record data

        Returns:
            None

        Raises:
            ValueError: Record not found
        """
        record = self._get_record(record_id)
        if record is None:
            raise ValueError(f"Record '{record_id}' not found in table")

        self._files.write_file(record.file, data)

    def delete_record(self, record_id: str) -> None:
        """Delete a record

        Args:
            record_id: Record ID

        Returns:
            None

        Raises:
            ValueError: Record not found
        """
        records = self._get_records()
        record = self._get_record(record_id, records=records)
        if record is None:
            raise ValueError(f"Record '{record_id}' not found in table")

        records.records = [
            record for record in records.records if record.id != record_id]
        self._update_records(records)

        self._files.delete_file(record.file)
