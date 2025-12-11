import tempfile

import pytest

from .db import TakocLocalDb
from .global_config import GlobalConfig


@pytest.fixture
def temp_db():
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        yield TakocLocalDb(db_root=tmp_dir, read_only=False)


def test_db_initialization(temp_db):
    """Test database initialization"""
    assert temp_db is not None
    assert temp_db.global_config is not None
    assert temp_db.namespaces is not None


def test_get_global_config(temp_db):
    """Test getting global configuration"""
    global_config = temp_db.global_config
    assert global_config is not None
    assert isinstance(global_config, GlobalConfig)
    assert global_config.version == "1.0"
    assert global_config.default_format == "yaml"


def test_get_namespaces(temp_db):
    """Test getting namespace manager"""
    from .namespaces import Namespaces
    namespaces = temp_db.namespaces
    assert namespaces is not None
    assert isinstance(namespaces, Namespaces)


def test_save_global_config(temp_db):
    """Test saving global configuration"""
    # Modify global configuration
    new_config = GlobalConfig(
        version="2.0",
        data_path="custom_data",
        default_format="json"
    )

    # Save configuration
    temp_db.save_global_config(new_config)

    # Reinitialize database to verify configuration has been saved
    from .db import TakocLocalDb
    reinitialized_db = TakocLocalDb(
        db_root=temp_db.global_config.config_dir, read_only=False)

    assert reinitialized_db.global_config.version == "2.0"
    assert reinitialized_db.global_config.data_path == "custom_data"
    assert reinitialized_db.global_config.default_format == "json"


def test_read_only_mode():
    """Test read-only mode"""
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=True)

        # Attempting to save configuration should fail
        new_config = GlobalConfig(version="2.0")
        with pytest.raises(PermissionError):
            db.save_global_config(new_config)


def test_data_dir_property(temp_db):
    """Test data_dir property"""
    # By default, data_dir should be config_dir
    assert temp_db.global_config.data_dir == temp_db.global_config.config_dir

    # After modifying data_path, data_dir should be config_dir/data_path
    new_config = GlobalConfig(data_path="test_data")
    new_db = temp_db.save_global_config(new_config)

    expected_data_dir = temp_db.global_config.config_dir / "test_data"
    assert new_db.global_config.data_dir == expected_data_dir
