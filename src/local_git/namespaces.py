import shutil
from pathlib import Path

from .db import TakocLocalDb
from .file_io import Files
from .metadata import NamespaceMetadata
from .namespace import Namespace


class Namespaces:
    """Namespace manager, handles CRUD operations for namespaces"""

    def __init__(self, db: TakocLocalDb):
        """Initialize namespace manager

        Args:
            db: Configuration manager instance
        """
        self._db = db
        self._files = Files(
            dir=Path(db.global_config.data_dir), read_only=db.read_only, format=db.global_config.default_format)

    def create_namespace(self, name: str, description: str = "") -> Namespace:
        """Create new namespace

        Args:
            name: Namespace name
            description: Namespace description

        Returns:
            Created namespace information
        """
        # Use metadata to add namespace
        self._db.metadata.add_namespace(name, description)

        # Use Namespace class method to create namespace
        return Namespace.initialize(db=self._db, name=name, dir=self._files.dir / name)

    def list_namespaces(self) -> list[NamespaceMetadata]:
        """Get list of all namespaces

        Returns:
            List of namespaces
        """
        return self._db.metadata.get_namespaces()

    def get_namespace(self, name: str) -> Namespace:
        """Get single namespace information

        Args:
            name: Namespace name

        Returns:
            Namespace information

        Raises:
            ValueError: Namespace not found
        """
        namespaces = self._db.metadata.get_namespaces()
        for ns in namespaces:
            if ns.name == name:
                return Namespace(db=self._db, name=name, dir=self._files.dir / ns.path)
        raise ValueError(f"Namespace '{name}' not found")

    def update_namespace(self, name: str, description: str) -> None:
        """Update namespace information

        Args:
            name: Namespace name
            description: New description

        Returns:
            Updated namespace information

        Raises:
            ValueError: Namespace not found
        """
        # Use metadata to update namespace
        self._db.metadata.update_namespace(name, description)

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
