import shutil
from pathlib import Path

from ..api.v1 import INamespaces, NamespaceData, NamespaceCreateRequest, NamespaceUpdateRequest
from .db import TakocLocalDb
from .file_io import Files
from .namespace import Namespace


class Namespaces(INamespaces):
    """Namespace manager, handles CRUD operations for namespaces"""

    def __init__(self, db: TakocLocalDb):
        """Initialize namespace manager

        Args:
            db: Configuration manager instance
        """
        self._db = db
        self._files = Files(
            dir=Path(db.global_config.data_dir), read_only=db.read_only, format=db.global_config.default_format)

    def create_namespace(self, create: NamespaceCreateRequest) -> None:
        """Create new namespace

        Args:
            create: Namespace creation data

        Returns:
            None
        """
        # Use metadata to add namespace
        self._db.metadata.add_namespace(create.name, create.description)

        # Use Namespace class method to create namespace
        Namespace.initialize(db=self._db, name=create.name, dir=self._files.dir / create.name)

    def list_namespaces(self) -> list[NamespaceData]:
        """Get list of all namespaces

        Returns:
            List of namespaces
        """
        namespace_metadata_list = self._db.metadata.get_namespaces()
        return [NamespaceData(name=ns.name, description=ns.description) for ns in namespace_metadata_list]

    def get_namespace(self, namespace: str) -> NamespaceData | None:
        """Get single namespace information

        Args:
            namespace: Namespace name

        Returns:
            Namespace information or None if not found
        """
        ns = self._db.metadata.get_namespace(namespace)
        if ns:
            return NamespaceData(name=ns.name, description=ns.description)
        return None

    def update_namespace(self, namespace: str, update: NamespaceUpdateRequest) -> None:
        """Update namespace information

        Args:
            namespace: Namespace name
            update: Namespace update data

        Returns:
            None

        Raises:
            ValueError: Namespace not found
        """
        # Use metadata to update namespace
        self._db.metadata.update_namespace(namespace, update.description)

    def delete_namespace(self, name: str) -> None:
        """Delete namespace

        Args:
            name: Namespace name

        Raises:
            ValueError: Namespace not found
        """
        # Use metadata to delete namespace metadata
        self._db.metadata.delete_namespace_meta(name)

        # Delete namespace directory
        namespace_dir = self._files.dir / name
        if namespace_dir.exists():
            shutil.rmtree(namespace_dir)
