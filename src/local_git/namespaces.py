from pathlib import Path
import shutil
from typing import Any, Dict, List

from pydantic import BaseModel
from .db import TakocLocalDb
from .file_io import Files
from .namespace import Namespace


class NamespaceMetadata(BaseModel):
    """Namespace metadata class"""
    name: str
    description: str = ""
    path: str = ""


class NamespacesMetadata(BaseModel):
    """Namespace list class"""
    namespaces: list[NamespaceMetadata] = []


class Namespaces:
    """Namespace manager, handles CRUD operations for namespaces"""

    def __init__(self, db: TakocLocalDb, read_only: bool = False):
        """Initialize namespace manager

        Args:
            db: Configuration manager instance
        """
        self._db = db
        self._files = Files(
            dir=Path(db.global_config.data_dir), read_only=read_only, format=db.global_config.default_format)
        self.namespaces_file = "namespaces"  # Without extension

    def _load_namespaces(self) -> NamespacesMetadata:
        """Load namespaces list"""
        data = self._files.read_file(self.namespaces_file)
        return NamespacesMetadata(**data) if data else NamespacesMetadata()

    def _save_namespaces(self, namespaces_data: NamespacesMetadata) -> None:
        """Save namespaces list"""
        self._files.write_file(
            self.namespaces_file, namespaces_data.model_dump())

    def create_namespace(self, name: str, description: str = "") -> Namespace:
        """Create new namespace

        Args:
            name: Namespace name
            description: Namespace description

        Returns:
            Created namespace information
        """
        namespace_info = NamespaceMetadata(
            name=name,
            description=description,
            path=name,
        )

        # Load existing namespaces
        namespaces_data = self._load_namespaces()

        # Check if namespace already exists
        for ns in namespaces_data.namespaces:
            if ns.name == name:
                raise ValueError(f"Namespace '{name}' already exists")

        # Add new namespace
        namespaces_data.namespaces.append(namespace_info)
        self._save_namespaces(namespaces_data)

        # Use Namespace class method to create namespace
        return Namespace.initialize(db=self._db, dir=self._files.dir / name)

    def list_namespaces(self) -> List[Dict[str, Any]]:
        """Get list of all namespaces

        Returns:
            List of namespaces
        """
        namespaces_data = self._load_namespaces()
        return namespaces_data.namespaces

    def get_namespace(self, name: str) -> Namespace:
        """Get single namespace information

        Args:
            name: Namespace name

        Returns:
            Namespace information

        Raises:
            ValueError: Namespace not found
        """
        namespaces_data = self._load_namespaces()
        for ns in namespaces_data.namespaces:
            if ns.name == name:
                return Namespace(db=self._db, dir=self._files.dir / ns.path, read_only=False)
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
        namespaces_data = self._load_namespaces()

        for ns in namespaces_data.namespaces:
            if ns.name == name:
                ns.description = description
                self._save_namespaces(namespaces_data)
                return
        raise ValueError(f"Namespace '{name}' not found")

    def delete_namespace(self, name: str) -> None:
        """Delete namespace

        Args:
            name: Namespace name

        Raises:
            ValueError: Namespace not found
        """
        namespaces_data = self._load_namespaces()

        # Check if namespace exists
        after_delete_namespaces = [
            ns for ns in namespaces_data.namespaces if ns.name != name]

        if len(after_delete_namespaces) == len(namespaces_data.namespaces):
            raise ValueError(f"Namespace '{name}' not found")

        namespaces_data.namespaces = after_delete_namespaces

        # Save updated namespaces list
        self._save_namespaces(namespaces_data)

        # Delete namespace directory
        namespace_dir = self._files.dir / name
        if namespace_dir.exists():
            shutil.rmtree(namespace_dir)
