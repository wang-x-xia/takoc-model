from pathlib import Path
from .file_io import Files, FILE_FORMAT
from pydantic import BaseModel


class GlobalConfig(BaseModel):
    version: str = "1.0"
    # Absolute path to the config directory
    config_dir: Path = Path(".")
    # Relative path to the config directory
    data_path: str = ""
    default_format: FILE_FORMAT = "yaml"

    @classmethod
    def load(cls, files: Files) -> "GlobalConfig":
        """Load configuration from file

        Args:
            files: File manager instance

        Returns:
            GlobalConfig instance
        """
        config_dir = files.dir.absolute()
        data = files.read_file("takoc")
        if data:
            return cls(config_dir=config_dir, **data)
        else:
            return cls(config_dir=config_dir)

    @property
    def data_dir(self) -> Path:
        """Get absolute data directory path"""
        return self.config_dir / self.data_path

    def save(self, files: Files) -> None:
        """Save configuration to file

        Args:
            files: File manager instance
        """
        files.write_file("takoc", self.model_dump(exclude={"config_dir"}))
