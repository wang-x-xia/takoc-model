import pytest
import tempfile
from pathlib import Path
from .db import TakocLocalDb
from .global_config import GlobalConfig


@pytest.fixture
def temp_db():
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        yield TakocLocalDb(db_root=tmp_dir, read_only=False)


def test_db_initialization(temp_db):
    """测试数据库初始化"""
    assert temp_db is not None
    assert temp_db.global_config is not None
    assert temp_db.namespaces is not None


def test_get_global_config(temp_db):
    """测试获取全局配置"""
    global_config = temp_db.global_config
    assert global_config is not None
    assert isinstance(global_config, GlobalConfig)
    assert global_config.version == "1.0"
    assert global_config.default_format == "yaml"


def test_get_namespaces(temp_db):
    """测试获取命名空间管理器"""
    from .namespaces import Namespaces
    namespaces = temp_db.namespaces
    assert namespaces is not None
    assert isinstance(namespaces, Namespaces)


def test_save_global_config(temp_db):
    """测试保存全局配置"""
    # 修改全局配置
    new_config = GlobalConfig(
        version="2.0",
        data_path="custom_data",
        default_format="json"
    )

    # 保存配置
    temp_db.save_global_config(new_config)

    # 重新初始化数据库以验证配置已保存
    from .db import TakocLocalDb
    reinitialized_db = TakocLocalDb(
        db_root=temp_db.global_config.config_dir, read_only=False)

    assert reinitialized_db.global_config.version == "2.0"
    assert reinitialized_db.global_config.data_path == "custom_data"
    assert reinitialized_db.global_config.default_format == "json"


def test_read_only_mode():
    """测试只读模式"""
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=True)

        # 尝试保存配置应该失败
        new_config = GlobalConfig(version="2.0")
        with pytest.raises(PermissionError):
            db.save_global_config(new_config)


def test_data_dir_property(temp_db):
    """测试data_dir属性"""
    # 默认情况下，data_dir应该是config_dir
    assert temp_db.global_config.data_dir == temp_db.global_config.config_dir

    # 修改data_path后，data_dir应该是config_dir/data_path
    new_config = GlobalConfig(data_path="test_data")
    new_db = temp_db.save_global_config(new_config)

    expected_data_dir = temp_db.global_config.config_dir / "test_data"
    assert new_db.global_config.data_dir == expected_data_dir
