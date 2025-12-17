import tempfile

import pytest

from .db import TakocLocalDb


@pytest.fixture
def temp_namespace():
    """Create temporary namespace for testing"""
    from ..api.v1 import NamespaceCreateRequest
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=False)
        # Create a namespace
        namespaces = db.namespaces
        namespaces.create_namespace(NamespaceCreateRequest(name="test_ns", description="Test namespace"))
        namespace = db.load_namespace("test_ns")
        yield namespace, db


def test_create_table(temp_namespace):
    """Test creating table"""
    from ..api.v1 import TableCreateRequest
    namespace, db = temp_namespace

    # Create table
    namespace.create_table(
        TableCreateRequest(name="test_table", description="This is a test table")
    )

    # Verify table exists
    assert namespace.get_table("test_table") is not None

    # Verify table directory has been created
    table_dir = db.global_config.data_dir / "test_ns" / "test_table"
    assert table_dir.exists()


def test_list_tables(temp_namespace):
    """Test listing all tables"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Initially there should be no tables
    initial_tables = namespace.list_tables()
    assert len(initial_tables) == 0

    # Create two tables
    namespace.create_table(TableCreateRequest(name="table1", description="Table 1"))
    namespace.create_table(TableCreateRequest(name="table2", description="Table 2"))

    # Verify table list
    all_tables = namespace.list_tables()
    assert len(all_tables) == 2

    # Check table names
    table_names = [t.name for t in all_tables]
    assert "table1" in table_names
    assert "table2" in table_names


def test_get_table(temp_namespace):
    """Test getting a single table"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="test_table", description="Test table"))

    # Get table
    table = namespace.get_table("test_table")

    assert table is not None
    assert table.name == "test_table"
    assert table.description == "Test table"


def test_get_nonexistent_table(temp_namespace):
    """Test getting non-existent table"""
    namespace, _ = temp_namespace

    # Getting non-existent table should return None
    table = namespace.get_table("nonexistent_table")
    assert table is None


def test_update_table(temp_namespace):
    """Test updating table information"""
    from ..api.v1 import TableCreateRequest, TableUpdateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="update_test", description="Original description"))

    # Update table - verify no exception is thrown
    namespace.update_table(name="update_test", update=TableUpdateRequest(description="Updated description"))

    # Verify table was updated
    table = namespace.get_table("update_test")
    assert table is not None
    assert table.description == "Updated description"


def test_update_nonexistent_table(temp_namespace):
    """Test updating non-existent table"""
    from ..api.v1 import TableUpdateRequest
    namespace, _ = temp_namespace

    # Updating non-existent table should raise exception
    try:
        namespace.update_table(name="nonexistent_table", update=TableUpdateRequest(description="Description"))
        assert False, "Expected ValueError but none was raised"
    except ValueError as e:
        assert "not found" in str(e)


def test_delete_table(temp_namespace):
    """Test deleting table"""
    from ..api.v1 import TableCreateRequest
    namespace, db = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="delete_test", description="To be deleted"))

    # Verify table exists
    all_tables = namespace.list_tables()
    assert len(all_tables) == 1

    # Verify table directory exists
    table_dir = db.global_config.data_dir / "test_ns" / "delete_test"
    assert table_dir.exists()

    # Delete table
    namespace.delete_table(name="delete_test")

    # Verify table has been deleted
    all_tables = namespace.list_tables()
    assert len(all_tables) == 0

    # Verify table directory has been deleted
    assert not table_dir.exists()


def test_delete_nonexistent_table(temp_namespace):
    """Test deleting non-existent table"""
    namespace, _ = temp_namespace

    # Deleting non-existent table should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespace.delete_table(name="nonexistent_table")

    assert "not found" in str(excinfo.value)


def test_create_duplicate_table(temp_namespace):
    """Test creating duplicate table"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="duplicate_table", description="First instance"))

    # Creating same table again should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespace.create_table(TableCreateRequest(name="duplicate_table", description="Second instance"))

    assert "already exists" in str(excinfo.value)


def test_table_records(temp_namespace):
    """Test table record functionality"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="record_test", description="Record test table"))
    table = namespace.load_table("record_test")

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
    """Test getting non-existent record"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="record_test", description="Record test table"))
    table = namespace.load_table("record_test")

    # Getting non-existent record should raise exception
    with pytest.raises(ValueError) as excinfo:
        table.get_record("nonexistent_record")

    assert "not found" in str(excinfo.value)


def test_update_nonexistent_record(temp_namespace):
    """Test updating non-existent record"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="record_test", description="Record test table"))
    table = namespace.load_table("record_test")

    # Updating non-existent record should raise exception
    with pytest.raises(ValueError) as excinfo:
        table.update_record("nonexistent_record", {"id": 1, "name": "Nonexistent", "value": 0.0})

    assert "not found" in str(excinfo.value)


def test_delete_nonexistent_record(temp_namespace):
    """Test deleting non-existent record"""
    from ..api.v1 import TableCreateRequest
    namespace, _ = temp_namespace

    # Create table
    namespace.create_table(TableCreateRequest(name="record_test", description="Record test table"))
    table = namespace.load_table("record_test")

    # Deleting non-existent record should raise exception
    with pytest.raises(ValueError) as excinfo:
        table.delete_record("nonexistent_record")

    assert "not found" in str(excinfo.value)
