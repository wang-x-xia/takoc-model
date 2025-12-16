from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


# Pydantic model definitions (corresponding to schemas in YAML)

class NamespaceBase(BaseModel):
    name: str
    description: Optional[str]


class NamespaceCreate(NamespaceBase):
    ...


class NamespaceUpdate(BaseModel):
    description: str = Field(..., description="Description of the namespace")


class Namespace(NamespaceBase):
    ...


class TableBase(BaseModel):
    name: str
    description: Optional[str]


class TableCreate(TableBase):
    ...


class TableUpdate(BaseModel):
    description: str = Field(..., description="Description of the table")


class Table(TableBase):
    namespace: str = Field(..., description="Name of the parent namespace")


class ErrorResponse(BaseModel):
    message: str = Field(description="Error message for human consumption")
    type: str = Field(description="Error type for programmatic handling")
    data: Any = Field(description="Additional error data", default=None)


# Main data access layer interface (for backward compatibility)
class IDatabase(ABC):
    """Main data access layer interface"""

    @property
    @abstractmethod
    def namespaces(self) -> "INamespaces":
        """Get namespace data access object"""
        pass

    @abstractmethod
    def load_namespace(self, namespace: str) -> Optional["INamespace"]:
        """Get table data access object for a specific namespace"""
        pass


# Data access layer interfaces
class INamespaces(ABC):
    """Namespace data access interface"""

    @abstractmethod
    def list_namespaces(self) -> list[Namespace]:
        """List all namespace metadata"""
        pass

    @abstractmethod
    def create_namespace(self, create: NamespaceCreate) -> None:
        """Add namespace metadata"""
        pass

    @abstractmethod
    def get_namespace(self, namespace) -> Namespace | None:
        """Add namespace metadata"""
        pass

    @abstractmethod
    def update_namespace(self, update: NamespaceUpdate) -> None:
        """Update namespace metadata"""
        pass

    @abstractmethod
    def delete_namespace(self, name: str) -> None:
        """Delete namespace metadata"""
        pass


class INamespace(ABC):
    """Table data access interface"""

    @property
    @abstractmethod
    def namespace(self) -> str:
        """Namespace property"""
        pass

    @abstractmethod
    def list_tables(self) -> list[Table]:
        """List all table metadata in a namespace"""
        pass

    @abstractmethod
    def get_table(self, name: str) -> Table | None:
        """Get a single table by name, return None if not found"""
        pass

    @abstractmethod
    def create_table(self, create: TableCreate) -> None:
        """Add table metadata"""
        pass

    @abstractmethod
    def update_table(self, update: TableUpdate) -> None:
        """Update table metadata"""
        pass

    @abstractmethod
    def delete_table(self, name: str) -> None:
        """Delete table metadata"""
        pass

    @abstractmethod
    def load_table(self, table: str) -> "ITable":
        """Get record data access object for a specific table"""
        pass


class ITable(ABC):
    """Record data access interface"""

    @property
    @abstractmethod
    def namespace(self) -> str:
        """Namespace property"""
        pass

    @property
    @abstractmethod
    def table(self) -> str:
        """Table property"""
        pass

    @abstractmethod
    def list_records(self) -> list[str]:
        """List all record IDs in a table"""
        pass

    @abstractmethod
    def get_record(self, record_id: str) -> Any:
        """Get single record data"""
        pass

    @abstractmethod
    def create_record(self, record_id: str, data: Any) -> None:
        """Add a record"""
        pass

    @abstractmethod
    def update_record(self, record_id: str, data: Any) -> None:
        """Update a record"""
        pass

    @abstractmethod
    def delete_record(self, record_id: str) -> None:
        """Delete a record"""
        pass
