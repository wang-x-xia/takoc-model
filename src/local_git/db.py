from pathlib import Path

from .file_io import Files
from .global_config import GlobalConfig


class TakocLocalDb:
    """Local Git Database"""

    def __init__(self, db_root: str = ".", read_only: bool = False):
        """Initialize configuration manager

        Args:
            db_root: Git repository path, default current directory
        """
        from .namespaces import Namespaces
        self._files = Files(
            dir=Path(db_root), read_only=read_only)
        self._global_config = GlobalConfig.load(self._files)
        self._namespaces = Namespaces(self, read_only=read_only)

    @property
    def global_config(self) -> GlobalConfig:
        """Get global configuration instance"""
        return self._global_config

    @property
    def namespaces(self):
        """Get namespaces manager"""
        return self._namespaces

    def save_global_config(self, global_config: GlobalConfig) -> "TakocLocalDb":
        """Save global configuration file"""
        global_config.save(self._files)
        return TakocLocalDb(db_root=self._files.dir, read_only=self._files.read_only)
