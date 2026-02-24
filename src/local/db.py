from pathlib import Path

from .file_io import Files
from .global_config import GlobalConfig
from ..api.v1 import IDatabase, INamespace


class TakocLocalDb(IDatabase):
    """Local Git Database"""

    def __init__(self, db_root: str = ".", read_only: bool = False):
        """Initialize configuration manager

        Args:
            db_root: Git repository path, default current directory
        """
        from .namespaces import Namespaces
        from .metadata import Metadata
        self._files = Files(dir=Path(db_root), read_only=read_only)
        self._global_config = GlobalConfig.load(self._files)
        self._namespaces = Namespaces(self)
        self._metadata = Metadata(self)

    @property
    def global_config(self) -> GlobalConfig:
        """Get global configuration instance"""
        return self._global_config

    @property
    def namespaces(self):
        """Get namespaces manager"""
        return self._namespaces

    @property
    def metadata(self):
        """Get metadata manager"""
        return self._metadata

    @property
    def read_only(self) -> bool:
        """Get read-only status"""
        return self._files.read_only

    def save_global_config(self, global_config: GlobalConfig) -> "TakocLocalDb":
        """Save global configuration file"""
        global_config.save(self._files)
        return TakocLocalDb(db_root=self._files.dir, read_only=self.read_only)

    def load_namespace(self, namespace: str) -> INamespace | None:
        """Get table data access object for a specific namespace"""
        # Check if this is the special 'takoc' metadata namespace
        if namespace == "takoc":
            return self._metadata.get_metadata_namespace()

        from .namespace import Namespace

        # Check if namespace exists
        if not self._metadata.get_namespace(namespace):
            return None

        # Create and return namespace instance
        namespace_dir = self._files.dir / namespace
        return Namespace(db=self, name=namespace, dir=namespace_dir)
