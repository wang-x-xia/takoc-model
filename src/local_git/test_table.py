import pytest
import tempfile
from pathlib import Path
from .db import TakocLocalDb
from .namespace import Namespace
from .table import Table


@pytest.fixture
def temp_namespace():
    """Create temporary namespace for testing"""
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=False)
        # Create a namespace
        namespaces = db.namespaces
        namespaces.create_namespace(name="test_ns", description="Test namespace")
        namespace = namespaces.get_namespace("test_ns")
        yield namespace, db


def test_create_table(temp_namespace):
    """Test creating table"""
    namespace, db = temp_namespace
    
    # Create table
    table = namespace.create_table(
        name="test_table",
        description="This is a test table"
    )
    
    assert table is not None
    assert isinstance(table, Table)
    assert hasattr(table, "_db")
    assert hasattr(table, "_files")
    
    # 验证表目录已创建
    table_dir = db.global_config.data_dir / "test_ns" / "test_table"
    assert table_dir.exists()


def test_list_tables(temp_namespace):
    """Test listing all tables"""
    namespace, _ = temp_namespace
    
    # 初始状态应该没有表
    initial_tables = namespace.list_tables()
    assert len(initial_tables) == 0
    
    # 创建两个表
    namespace.create_table(name="table1", description="Table 1")
    namespace.create_table(name="table2", description="Table 2")
    
    # 验证表列表
    all_tables = namespace.list_tables()
    assert len(all_tables) == 2
    
    # 检查表名称
    assert "table1" in all_tables
    assert "table2" in all_tables


def test_get_table(temp_namespace):
    """Test getting a single table"""
    namespace, _ = temp_namespace
    
    # 创建表
    namespace.create_table(name="test_table", description="Test table")
    
    # 获取表
    table = namespace.get_table("test_table")
    
    assert table is not None
    assert isinstance(table, Table)


def test_get_nonexistent_table(temp_namespace):
    """Test getting non-existent table"""
    namespace, _ = temp_namespace
    
    # 获取不存在的表应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespace.get_table("nonexistent_table")
    
    assert "not found" in str(excinfo.value)


def test_update_table(temp_namespace):
    """Test updating table information"""
    namespace, _ = temp_namespace
    
    # 创建表
    namespace.create_table(name="update_test", description="Original description")
    
    # 更新表 - 验证不会抛出异常
    namespace.update_table(name="update_test", description="Updated description")
    
    # 验证表仍然存在
    tables = namespace.list_tables()
    assert "update_test" in tables


def test_update_nonexistent_table(temp_namespace):
    """Test updating non-existent table"""
    namespace, _ = temp_namespace
    
    # 更新不存在的表应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespace.update_table(name="nonexistent_table", description="Description")
    
    assert "not found" in str(excinfo.value)


def test_delete_table(temp_namespace):
    """Test deleting table"""
    namespace, db = temp_namespace
    
    # 创建表
    namespace.create_table(name="delete_test", description="To be deleted")
    
    # 验证表存在
    all_tables = namespace.list_tables()
    assert len(all_tables) == 1
    
    # 验证表目录存在
    table_dir = db.global_config.data_dir / "test_ns" / "delete_test"
    assert table_dir.exists()
    
    # 删除表
    namespace.delete_table(name="delete_test")
    
    # 验证表已删除
    all_tables = namespace.list_tables()
    assert len(all_tables) == 0
    
    # 验证表目录已删除
    assert not table_dir.exists()


def test_delete_nonexistent_table(temp_namespace):
    """Test deleting non-existent table"""
    namespace, _ = temp_namespace
    
    # 删除不存在的表应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespace.delete_table(name="nonexistent_table")
    
    assert "not found" in str(excinfo.value)


def test_create_duplicate_table(temp_namespace):
    """Test creating duplicate table"""
    namespace, _ = temp_namespace
    
    # 创建表
    namespace.create_table(name="duplicate_table", description="First instance")
    
    # 再次创建同名表应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        namespace.create_table(name="duplicate_table", description="Second instance")
    
    assert "already exists" in str(excinfo.value)





def test_table_records(temp_namespace):
    """Test table record functionality"""
    namespace, _ = temp_namespace
    
    # 创建表
    table = namespace.create_table(name="record_test", description="Record test table")
    
    # Create records
    table.create_record("record1", {"id": 1, "name": "Test 1", "value": 10.5})
    table.create_record("record2", {"id": 2, "name": "Test 2", "value": 20.5})
    
    # List all records
    record_ids = table.list_records()
    assert len(record_ids) == 2
    assert "record1" in record_ids
    assert "record2" in record_ids
    
    # Get a single record
    retrieved_record = table.get_record("record1")
    assert retrieved_record["id"] == 1
    assert retrieved_record["name"] == "Test 1"
    assert retrieved_record["value"] == 10.5
    
    # Update record
    table.update_record("record1", {"id": 1, "name": "Updated Test 1", "value": 15.5})
    updated_record = table.get_record("record1")
    assert updated_record["name"] == "Updated Test 1"
    assert updated_record["value"] == 15.5
    
    # Delete record
    table.delete_record("record2")
    record_ids_after_delete = table.list_records()
    assert len(record_ids_after_delete) == 1
    assert "record1" in record_ids_after_delete
    assert "record2" not in record_ids_after_delete


def test_get_nonexistent_record(temp_namespace):
    """测试获取不存在的记录"""
    namespace, _ = temp_namespace
    
    # 创建表
    table = namespace.create_table(name="record_test", description="Record test table")
    
    # 获取不存在的记录应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        table.get_record("nonexistent_record")
    
    assert "not found" in str(excinfo.value)


def test_update_nonexistent_record(temp_namespace):
    """测试更新不存在的记录"""
    namespace, _ = temp_namespace
    
    # 创建表
    table = namespace.create_table(name="record_test", description="Record test table")
    
    # 更新不存在的记录应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        table.update_record("nonexistent_record", {"id": 1, "name": "Test"})
    
    assert "not found" in str(excinfo.value)


def test_delete_nonexistent_record(temp_namespace):
    """测试删除不存在的记录"""
    namespace, _ = temp_namespace
    
    # 创建表
    table = namespace.create_table(name="record_test", description="Record test table")
    
    # 删除不存在的记录应该抛出异常
    with pytest.raises(ValueError) as excinfo:
        table.delete_record("nonexistent_record")
    
    assert "not found" in str(excinfo.value)
