import json
import os
from pathlib import Path
from typing import Any, Literal

import yaml

FILE_FORMAT = Literal["yaml", "json"]


class Files:
    """
    Unify the IO of files.
    This class will handle the extension of files.
    """

    def __init__(self, dir: Path, read_only: bool, format: FILE_FORMAT = "yaml"):
        """Initialize file manager

        Args:
            dir: Base directory, all file operations are based on this directory
        """
        self.__dir = dir
        self.__read_only = read_only
        self.__format = format

    @property
    def dir(self) -> Path:
        """Get base directory"""
        return self.__dir

    @property
    def read_only(self) -> bool:
        """Get read-only mode"""
        return self.__read_only

    @property
    def format(self) -> FILE_FORMAT:
        """Get default file format"""
        return self.__format

    def file_info(self, file_name: str) -> tuple[Path, FILE_FORMAT] | None:
        """Get file format

        Args:
            file_name: File name

        Returns:
            File format (yaml/json)

        Raises:
            ValueError: If file format is not supported
        """
        # Use default format first
        if self.format == "yaml":
            if info := self._yaml_file_info(file_name):
                return info
        elif self.format == "json":
            if info := self._json_file_info(file_name):
                return info

        # Fallback to other formats if default is not supported
        if info := self._yaml_file_info(file_name):
            return info
        if info := self._json_file_info(file_name):
            return info

        return None

    def _yaml_file_info(self, file_name: str) -> tuple[Path, FILE_FORMAT] | None:
        """Get YAML file information"""
        file = self.dir / (file_name + ".yaml")
        if file.exists():
            return file, "yaml"
        file = self.dir / (file_name + ".yml")
        if file.exists():
            return file, "yaml"
        return None

    def _json_file_info(self, file_name: str) -> tuple[Path, FILE_FORMAT] | None:
        """Get JSON file information"""
        file = self.dir / (file_name + ".json")
        if file.exists():
            return file, "json"
        return None

    def read_file(self, file_name: str) -> Any:
        """
        read the file content.

        Args:
            file_name: file name without extension

        Returns:
            file content
        """
        file_info = self.file_info(file_name)
        if file_info is None:
            return None

        file, format = file_info

        with open(file, "r", encoding="utf-8") as f:
            if format == "yaml":
                return yaml.safe_load(f)
            elif format == "json":
                return json.load(f)

        raise ValueError(f"Unsupported file format for {file_name}")

    def write_file(self, file_name: str, data: Any) -> None:
        """write the file content.

        Args:
            file_name: file name without extension
            data: file content
        """
        if self.read_only:
            raise PermissionError("Read-only mode, cannot write files")

        file = self.dir / (file_name + self.default_ext)
        os.makedirs(file.parent, exist_ok=True)

        # Determine file format
        with open(file, "w", encoding="utf-8") as f:
            if self.format == "yaml":
                yaml.dump(data, f, default_flow_style=False,
                          sort_keys=False, allow_unicode=True)
            elif self.format == "json":
                json.dump(data, f, indent=2, ensure_ascii=False)

    def delete_file(self, file_name: str) -> None:
        """delete the file.

        Args:
            file_name: file name without extension
        """
        file, _ = self.file_info(file_name)
        if os.path.exists(file):
            os.remove(file)

    @property
    def default_ext(self) -> str:
        """
        get the default extension of the file format.

        Returns:
            default extension
        """
        if self.format.lower() == "yaml":
            return ".yaml"
        elif self.format.lower() == "json":
            return ".json"
        raise ValueError(f"Unsupported file format: {self.format}")
