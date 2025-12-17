import tempfile

import pytest

from .db import TakocLocalDb
from .metadata import Metadata, NamespaceMetadata, TableMetadata


@pytest.fixture
def temp_metadata():
    """Test fixture for Metadata class"""
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=False)
        yield db.metadata, db


@pytest.fixture
def temp_metadata_with_namespace(temp_metadata):
    """Test fixture with a pre-created namespace"""
    metadata, db = temp_metadata
    metadata.add_namespace(name="test_ns", description="Test namespace")
    yield metadata, db


@pytest.fixture
def temp_metadata_with_table(temp_metadata_with_namespace):
    """Test fixture with a pre-created namespace and table"""
    metadata, db = temp_metadata_with_namespace
    metadata.add_table(namespace="test_ns", name="test_table", description="Test table")
    yield metadata, db


def test_metadata_initialization(temp_metadata):
    """Test Metadata class initialization"""
    metadata, db = temp_metadata
    assert metadata is not None
    assert isinstance(metadata, Metadata)
    assert metadata.db == db
    assert metadata.metadata_dir == db.global_config.data_dir / "takoc"
    assert metadata.metadata_dir.exists()


def test_add_namespace(temp_metadata):
    """Test adding a namespace"""
    metadata, _ = temp_metadata
    metadata.add_namespace(name="test_ns", description="Test namespace")

    namespaces = metadata.get_namespaces()
    assert len(namespaces) == 1
    assert namespaces[0].name == "test_ns"
    assert namespaces[0].description == "Test namespace"
    assert namespaces[0].path == "test_ns"


def test_add_duplicate_namespace(temp_metadata):
    """Test adding a duplicate namespace"""
    metadata, _ = temp_metadata
    metadata.add_namespace(name="test_ns", description="Test namespace")

    with pytest.raises(ValueError) as excinfo:
        metadata.add_namespace(name="test_ns", description="Duplicate namespace")

    assert "already exists" in str(excinfo.value)


def test_get_namespaces(temp_metadata):
    """Test getting all namespaces"""
    metadata, _ = temp_metadata
    assert len(metadata.get_namespaces()) == 0

    metadata.add_namespace(name="ns1", description="Namespace 1")
    metadata.add_namespace(name="ns2", description="Namespace 2")

    namespaces = metadata.get_namespaces()
    assert len(namespaces) == 2
    assert all(isinstance(ns, NamespaceMetadata) for ns in namespaces)

    names = [ns.name for ns in namespaces]
    assert "ns1" in names
    assert "ns2" in names


def test_update_namespace(temp_metadata):
    """Test updating a namespace"""
    metadata, _ = temp_metadata
    metadata.add_namespace(name="test_ns", description="Original description")

    metadata.update_namespace(name="test_ns", description="Updated description")

    namespaces = metadata.get_namespaces()
    assert namespaces[0].description == "Updated description"


def test_update_nonexistent_namespace(temp_metadata):
    """Test updating a nonexistent namespace"""
    metadata, _ = temp_metadata

    with pytest.raises(ValueError) as excinfo:
        metadata.update_namespace(name="nonexistent", description="Description")

    assert "not found" in str(excinfo.value)


def test_delete_namespace_meta(temp_metadata):
    """Test deleting a namespace's metadata"""
    metadata, _ = temp_metadata
    metadata.add_namespace(name="test_ns", description="Test namespace")

    metadata.delete_namespace_meta(name="test_ns")

    namespaces = metadata.get_namespaces()
    assert len(namespaces) == 0


def test_delete_nonexistent_namespace_meta(temp_metadata):
    """Test deleting a nonexistent namespace's metadata"""
    metadata, _ = temp_metadata

    with pytest.raises(ValueError) as excinfo:
        metadata.delete_namespace_meta(name="nonexistent")

    assert "not found" in str(excinfo.value)


def test_add_table(temp_metadata_with_namespace):
    """Test adding a table"""
    metadata, _ = temp_metadata_with_namespace

    metadata.add_table(namespace="test_ns", name="test_table", description="Test table")

    tables = metadata.get_tables(namespace="test_ns")
    assert len(tables) == 1
    assert tables[0].name == "test_table"
    assert tables[0].description == "Test table"
    assert tables[0].path == "test_table"


def test_add_duplicate_table(temp_metadata_with_namespace):
    """Test adding a duplicate table"""
    metadata, _ = temp_metadata_with_namespace
    metadata.add_table(namespace="test_ns", name="test_table", description="Test table")

    with pytest.raises(ValueError) as excinfo:
        metadata.add_table(namespace="test_ns", name="test_table", description="Duplicate table")

    assert "already exists" in str(excinfo.value)


def test_get_tables(temp_metadata_with_table):
    """Test getting all tables in a namespace"""
    metadata, _ = temp_metadata_with_table

    metadata.add_table(namespace="test_ns", name="table2", description="Second table")

    tables = metadata.get_tables(namespace="test_ns")
    assert len(tables) == 2
    assert all(isinstance(table, TableMetadata) for table in tables)

    names = [table.name for table in tables]
    assert "test_table" in names
    assert "table2" in names


def test_update_table(temp_metadata_with_table):
    """Test updating a table"""
    metadata, _ = temp_metadata_with_table

    metadata.update_table(namespace="test_ns", name="test_table", description="Updated table")

    tables = metadata.get_tables(namespace="test_ns")
    assert tables[0].description == "Updated table"


def test_update_nonexistent_table(temp_metadata_with_namespace):
    """Test updating a nonexistent table"""
    metadata, _ = temp_metadata_with_namespace

    with pytest.raises(ValueError) as excinfo:
        metadata.update_table(namespace="test_ns", name="nonexistent", description="Description")

    assert "not found" in str(excinfo.value)


def test_delete_table(temp_metadata_with_table):
    """Test deleting a table"""
    metadata, _ = temp_metadata_with_table

    metadata.delete_table(namespace="test_ns", name="test_table")

    tables = metadata.get_tables(namespace="test_ns")
    assert len(tables) == 0


def test_delete_nonexistent_table(temp_metadata_with_namespace):
    """Test deleting a nonexistent table"""
    metadata, _ = temp_metadata_with_namespace

    with pytest.raises(ValueError) as excinfo:
        metadata.delete_table(namespace="test_ns", name="nonexistent")

    assert "not found" in str(excinfo.value)


def test_takoc_local_db_read_only_property():
    """Test the read_only property of TakocLocalDb"""
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        # Test with read_only=False
        db = TakocLocalDb(db_root=tmp_dir, read_only=False)
        assert db.read_only is False
        assert db._files.read_only is False

        # Test with read_only=True
        db_read_only = TakocLocalDb(db_root=tmp_dir, read_only=True)
        assert db_read_only.read_only is True
        assert db_read_only._files.read_only is True


def test_metadata_uses_db_read_only(temp_metadata):
    """Test that Metadata uses the read_only property from db"""
    metadata, db = temp_metadata
    assert metadata._files.read_only == db.read_only

    # Test with read_only=True
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db_read_only = TakocLocalDb(db_root=tmp_dir, read_only=True)
        metadata_read_only = db_read_only.metadata
        assert metadata_read_only._files.read_only is True


def test_delete_namespace_meta_clears_tables(temp_metadata_with_table):
    """Test that deleting namespace metadata also deletes associated tables"""
    metadata, _ = temp_metadata_with_table

    # Verify table exists before deleting namespace metadata
    tables_before = metadata.get_tables(namespace="test_ns")
    assert len(tables_before) == 1

    # Delete namespace metadata
    metadata.delete_namespace_meta(name="test_ns")

    # Verify namespace is deleted
    namespaces_after = metadata.get_namespaces()
    assert len(namespaces_after) == 0

    # Verify tables file is also deleted by trying to get tables (should return empty list)
    tables_after = metadata.get_tables(namespace="test_ns")
    assert len(tables_after) == 0


def test_get_metadata_namespace(temp_metadata):
    """Test that get_metadata_namespace returns a MetadataNamespace instance"""
    metadata, db = temp_metadata
    metadata_namespace = metadata.get_metadata_namespace()

    from .metadata import MetadataNamespace
    assert isinstance(metadata_namespace, MetadataNamespace)
    assert metadata_namespace.name == "takoc"


def test_metadata_namespace_list_tables(temp_metadata):
    """Test that MetadataNamespace lists the correct tables"""
    metadata, db = temp_metadata
    metadata_namespace = metadata.get_metadata_namespace()

    tables = metadata_namespace.list_tables()
    assert len(tables) == 2
    table_names = [table.name for table in tables]
    assert "namespace" in table_names
    assert "table" in table_names


def test_metadata_namespace_get_table(temp_metadata):
    """Test that MetadataNamespace can get individual tables"""
    metadata, db = temp_metadata
    metadata_namespace = metadata.get_metadata_namespace()

    namespace_table = metadata_namespace.get_table("namespace")
    assert namespace_table is not None
    assert namespace_table.name == "namespace"
    assert namespace_table.description == "Stores all namespace records"

    table_table = metadata_namespace.get_table("table")
    assert table_table is not None
    assert table_table.name == "table"
    assert table_table.description == "Stores all table records"

    nonexistent_table = metadata_namespace.get_table("nonexistent")
    assert nonexistent_table is None


def test_metadata_namespace_load_table(temp_metadata):
    """Test that MetadataNamespace can load table implementations"""
    metadata, db = temp_metadata
    metadata_namespace = metadata.get_metadata_namespace()

    from .metadata import NamespacesTable, TablesTable

    namespace_table = metadata_namespace.load_table("namespace")
    assert isinstance(namespace_table, NamespacesTable)

    table_table = metadata_namespace.load_table("table")
    assert isinstance(table_table, TablesTable)

    with pytest.raises(ValueError):
        metadata_namespace.load_table("nonexistent")


def test_metadata_namespace_cannot_modify_tables(temp_metadata):
    """Test that MetadataNamespace tables cannot be modified"""
    metadata, db = temp_metadata
    metadata_namespace = metadata.get_metadata_namespace()

    from ..api.v1 import TableCreateRequest, TableUpdateRequest
    from ..api.error import ReadOnlyError

    with pytest.raises(ReadOnlyError):
        metadata_namespace.create_table(TableCreateRequest(name="new_table", description="New table"))

    with pytest.raises(ReadOnlyError):
        metadata_namespace.update_table("namespace", TableUpdateRequest(description="Updated description"))

    with pytest.raises(ReadOnlyError):
        metadata_namespace.delete_table("namespace")


def test_namespaces_table_list_records(temp_metadata_with_namespace):
    """Test that NamespacesTable can list namespace records"""
    metadata, db = temp_metadata_with_namespace
    namespaces_table = metadata.get_metadata_namespace().load_table("namespace")

    records = namespaces_table.list_records()
    assert len(records) == 1
    assert "test_ns" in records


def test_namespaces_table_get_record(temp_metadata_with_namespace):
    """Test that NamespacesTable can get individual namespace records"""
    metadata, db = temp_metadata_with_namespace
    namespaces_table = metadata.get_metadata_namespace().load_table("namespace")

    record = namespaces_table.get_record("test_ns")
    assert record["name"] == "test_ns"
    assert record["description"] == "Test namespace"

    with pytest.raises(ValueError):
        namespaces_table.get_record("nonexistent")


def test_namespaces_table_create_record(temp_metadata):
    """Test that NamespacesTable can create namespace records"""
    metadata, db = temp_metadata
    namespaces_table = metadata.get_metadata_namespace().load_table("namespace")

    data = {"name": "new_ns", "description": "New namespace"}
    namespaces_table.create_record("new_ns", data)

    # Verify namespace was created
    namespaces = metadata.get_namespaces()
    assert len(namespaces) == 1
    assert namespaces[0].name == "new_ns"
    assert namespaces[0].description == "New namespace"

    # Verify record exists
    record = namespaces_table.get_record("new_ns")
    assert record["name"] == "new_ns"


def test_namespaces_table_update_record(temp_metadata_with_namespace):
    """Test that NamespacesTable can update namespace records"""
    metadata, db = temp_metadata_with_namespace
    namespaces_table = metadata.get_metadata_namespace().load_table("namespace")

    data = {"description": "Updated namespace"}
    namespaces_table.update_record("test_ns", data)

    # Verify namespace was updated
    namespace = metadata.get_namespace("test_ns")
    assert namespace.description == "Updated namespace"

    # Verify record was updated
    record = namespaces_table.get_record("test_ns")
    assert record["description"] == "Updated namespace"


def test_namespaces_table_delete_record(temp_metadata_with_namespace):
    """Test that NamespacesTable can delete namespace records"""
    metadata, db = temp_metadata_with_namespace
    namespaces_table = metadata.get_metadata_namespace().load_table("namespace")

    namespaces_table.delete_record("test_ns")

    # Verify namespace was deleted
    namespaces = metadata.get_namespaces()
    assert len(namespaces) == 0


def test_tables_table_list_records(temp_metadata_with_table):
    """Test that TablesTable can list table records with namespace.table format"""
    metadata, db = temp_metadata_with_table
    tables_table = metadata.get_metadata_namespace().load_table("table")

    records = tables_table.list_records()
    assert len(records) == 1
    assert "test_ns.test_table" in records


def test_tables_table_get_record(temp_metadata_with_table):
    """Test that TablesTable can get individual table records"""
    metadata, db = temp_metadata_with_table
    tables_table = metadata.get_metadata_namespace().load_table("table")

    record = tables_table.get_record("test_ns.test_table")
    assert record["name"] == "test_table"
    assert record["description"] == "Test table"
    assert record["namespace"] == "test_ns"

    with pytest.raises(ValueError):
        tables_table.get_record("nonexistent_table")

    with pytest.raises(ValueError):
        tables_table.get_record("nonexistent.namespace")


def test_tables_table_create_record(temp_metadata_with_namespace):
    """Test that TablesTable can create table records"""
    metadata, db = temp_metadata_with_namespace
    tables_table = metadata.get_metadata_namespace().load_table("table")

    data = {"name": "new_table", "description": "New table"}
    tables_table.create_record("test_ns.new_table", data)

    # Verify table was created
    tables = metadata.get_tables("test_ns")
    assert len(tables) == 1
    assert tables[0].name == "new_table"
    assert tables[0].description == "New table"

    # Verify record exists
    record = tables_table.get_record("test_ns.new_table")
    assert record["name"] == "new_table"


def test_tables_table_update_record(temp_metadata_with_table):
    """Test that TablesTable can update table records"""
    metadata, db = temp_metadata_with_table
    tables_table = metadata.get_metadata_namespace().load_table("table")

    data = {"description": "Updated table"}
    tables_table.update_record("test_ns.test_table", data)

    # Verify table was updated
    table = metadata.get_table("test_ns", "test_table")
    assert table.description == "Updated table"

    # Verify record was updated
    record = tables_table.get_record("test_ns.test_table")
    assert record["description"] == "Updated table"


def test_tables_table_delete_record(temp_metadata_with_table):
    """Test that TablesTable can delete table records"""
    metadata, db = temp_metadata_with_table
    tables_table = metadata.get_metadata_namespace().load_table("table")

    tables_table.delete_record("test_ns.test_table")

    # Verify table was deleted
    tables = metadata.get_tables("test_ns")
    assert len(tables) == 0


def test_tables_table_record_id_format(temp_metadata):
    """Test that TablesTable enforces namespace.table record ID format"""
    metadata, db = temp_metadata
    tables_table = metadata.get_metadata_namespace().load_table("table")

    with pytest.raises(ValueError):
        tables_table.get_record("invalid_id")

    with pytest.raises(ValueError):
        tables_table.create_record("invalid_id", {"name": "table", "description": "Table"})

    with pytest.raises(ValueError):
        tables_table.update_record("invalid_id", {"description": "Updated"})

    with pytest.raises(ValueError):
        tables_table.delete_record("invalid_id")
