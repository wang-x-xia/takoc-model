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
