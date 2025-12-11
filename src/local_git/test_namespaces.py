import tempfile

import pytest

from .db import TakocLocalDb


@pytest.fixture
def temp_namespaces():
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=False)
        yield db.namespaces, db


def test_create_namespace(temp_namespaces):
    """测试创建命名空间"""
    namespaces, db = temp_namespaces

    # 创建命名空间
    namespace = namespaces.create_namespace(
        name="test_namespace",
        description="This is a test namespace"
    )

    assert namespace is not None
    assert hasattr(namespace, "_db")
    assert hasattr(namespace, "_files")

    # 验证命名空间目录已创建
    namespace_dir = db.global_config.data_dir / "test_namespace"
    assert namespace_dir.exists()


def test_list_namespaces(temp_namespaces):
    """测试列出所有命名空间"""
    namespaces, db = temp_namespaces

    # 初始状态应该没有命名空间
    initial_namespaces = namespaces.list_namespaces()
    assert len(initial_namespaces) == 0

    # 创建两个命名空间
    namespaces.create_namespace(name="ns1", description="Namespace 1")
    namespaces.create_namespace(name="ns2", description="Namespace 2")

    # 验证命名空间列表
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 2

    # 检查命名空间信息
    ns_names = [ns.name for ns in all_namespaces]
    assert "ns1" in ns_names
    assert "ns2" in ns_names

    ns_descriptions = [ns.description for ns in all_namespaces]
    assert "Namespace 1" in ns_descriptions
    assert "Namespace 2" in ns_descriptions


def test_get_namespace(temp_namespaces):
    """测试获取单个命名空间"""
    namespaces, db = temp_namespaces

    # 创建命名空间
    namespaces.create_namespace(name="test_ns", description="Test namespace")

    # 获取命名空间
    namespace = namespaces.get_namespace("test_ns")

    assert namespace is not None
    assert hasattr(namespace, "_db")
    assert hasattr(namespace, "_files")


def test_get_nonexistent_namespace(temp_namespaces):
    """测试获取不存在的命名空间"""
    namespaces, _ = temp_namespaces

    # 获取不存在的命名空间应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespaces.get_namespace("nonexistent")

    assert "not found" in str(excinfo.value)


def test_update_namespace(temp_namespaces):
    """测试更新命名空间"""
    namespaces, _ = temp_namespaces

    # 创建命名空间
    namespaces.create_namespace(name="update_test", description="Original description")

    # 更新命名空间
    namespaces.update_namespace(name="update_test", description="Updated description")

    # 验证更新
    all_namespaces = namespaces.list_namespaces()
    updated_ns = next(ns for ns in all_namespaces if ns.name == "update_test")
    assert updated_ns.description == "Updated description"


def test_update_nonexistent_namespace(temp_namespaces):
    """测试更新不存在的命名空间"""
    namespaces, _ = temp_namespaces

    # 更新不存在的命名空间应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespaces.update_namespace(name="nonexistent", description="Description")

    assert "not found" in str(excinfo.value)


def test_delete_namespace(temp_namespaces):
    """测试删除命名空间"""
    namespaces, db = temp_namespaces

    # 创建命名空间
    namespaces.create_namespace(name="delete_test", description="To be deleted")

    # 验证命名空间存在
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 1

    # 验证命名空间目录存在
    namespace_dir = db.global_config.data_dir / "delete_test"
    assert namespace_dir.exists()

    # 删除命名空间
    namespaces.delete_namespace(name="delete_test")

    # 验证命名空间已删除
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 0

    # 验证命名空间目录已删除
    assert not namespace_dir.exists()


def test_delete_nonexistent_namespace(temp_namespaces):
    """测试删除不存在的命名空间"""
    namespaces, _ = temp_namespaces

    # 删除不存在的命名空间应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespaces.delete_namespace(name="nonexistent")

    assert "not found" in str(excinfo.value)


def test_create_duplicate_namespace(temp_namespaces):
    """测试创建重复的命名空间"""
    namespaces, _ = temp_namespaces

    # 创建命名空间
    namespaces.create_namespace(name="duplicate", description="First instance")

    # 再次创建同名命名空间应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespaces.create_namespace(name="duplicate", description="Second instance")

    assert "already exists" in str(excinfo.value)
