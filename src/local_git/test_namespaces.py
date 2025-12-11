import tempfile

import pytest

from .db import TakocLocalDb


@pytest.fixture
def temp_namespaces():
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        db = TakocLocalDb(db_root=tmp_dir, read_only=False)
        yield db.namespaces, db


def test_create_namespace(temp_namespaces):
    """Test creating namespace"""
    namespaces, db = temp_namespaces

    # Create namespace
    namespace = namespaces.create_namespace(
        name="test_namespace",
        description="This is a test namespace"
    )

    assert namespace is not None
    assert hasattr(namespace, "_db")
    assert hasattr(namespace, "_files")

    # Verify namespace directory has been created
    namespace_dir = db.global_config.data_dir / "test_namespace"
    assert namespace_dir.exists()


def test_list_namespaces(temp_namespaces):
    """Test listing all namespaces"""
    namespaces, db = temp_namespaces

    # Initially there should be no namespaces
    initial_namespaces = namespaces.list_namespaces()
    assert len(initial_namespaces) == 0

    # Create two namespaces
    namespaces.create_namespace(name="ns1", description="Namespace 1")
    namespaces.create_namespace(name="ns2", description="Namespace 2")

    # Verify namespace list
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 2

    # Check namespace information
    ns_names = [ns.name for ns in all_namespaces]
    assert "ns1" in ns_names
    assert "ns2" in ns_names

    ns_descriptions = [ns.description for ns in all_namespaces]
    assert "Namespace 1" in ns_descriptions
    assert "Namespace 2" in ns_descriptions


def test_get_namespace(temp_namespaces):
    """Test getting a single namespace"""
    namespaces, db = temp_namespaces

    # Create namespace
    namespaces.create_namespace(name="test_ns", description="Test namespace")

    # Get namespace
    namespace = namespaces.get_namespace("test_ns")

    assert namespace is not None
    assert hasattr(namespace, "_db")
    assert hasattr(namespace, "_files")


def test_get_nonexistent_namespace(temp_namespaces):
    """Test getting non-existent namespace"""
    namespaces, _ = temp_namespaces

    # Getting non-existent namespace should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.get_namespace("nonexistent")

    assert "not found" in str(excinfo.value)


def test_update_namespace(temp_namespaces):
    """Test updating namespace"""
    namespaces, _ = temp_namespaces

    # Create namespace
    namespaces.create_namespace(name="update_test", description="Original description")

    # Update namespace
    namespaces.update_namespace(name="update_test", description="Updated description")

    # Verify update
    all_namespaces = namespaces.list_namespaces()
    updated_ns = next(ns for ns in all_namespaces if ns.name == "update_test")
    assert updated_ns.description == "Updated description"


def test_update_nonexistent_namespace(temp_namespaces):
    """Test updating non-existent namespace"""
    namespaces, _ = temp_namespaces

    # Updating non-existent namespace should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.update_namespace(name="nonexistent", description="Description")

    assert "not found" in str(excinfo.value)


def test_delete_namespace(temp_namespaces):
    """Test deleting namespace"""
    namespaces, db = temp_namespaces

    # Create namespace
    namespaces.create_namespace(name="delete_test", description="To be deleted")

    # Verify namespace exists
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 1

    # Verify namespace directory exists
    namespace_dir = db.global_config.data_dir / "delete_test"
    assert namespace_dir.exists()

    # Delete namespace
    namespaces.delete_namespace(name="delete_test")

    # Verify namespace has been deleted
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 0

    # Verify namespace directory has been deleted
    assert not namespace_dir.exists()


def test_delete_nonexistent_namespace(temp_namespaces):
    """Test deleting non-existent namespace"""
    namespaces, _ = temp_namespaces

    # Deleting non-existent namespace should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.delete_namespace(name="nonexistent")

    assert "not found" in str(excinfo.value)


def test_create_duplicate_namespace(temp_namespaces):
    """Test creating duplicate namespace"""
    namespaces, _ = temp_namespaces

    # Create namespace
    namespaces.create_namespace(name="duplicate", description="First instance")

    # Creating same namespace again should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.create_namespace(name="duplicate", description="Second instance")

    assert "already exists" in str(excinfo.value)
