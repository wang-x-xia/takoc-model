import tempfile

import pytest

from .db import TakocLocalDb
from ..api.v1 import NamespaceCreateRequest, NamespaceUpdateRequest


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
    namespaces.create_namespace(
        NamespaceCreateRequest(name="test_namespace", description="This is a test namespace")
    )

    # Verify namespace was created
    created_namespace = namespaces.get_namespace("test_namespace")
    assert created_namespace is not None
    assert created_namespace.name == "test_namespace"
    assert created_namespace.description == "This is a test namespace"

    # Verify namespace directory has been created
    namespace_dir = db.global_config.data_dir / "test_namespace"
    assert namespace_dir.exists()


def test_list_namespaces(temp_namespaces):
    """Test listing all namespaces"""
    namespaces, db = temp_namespaces

    # Initially there should be only the 'takoc' system namespace
    initial_namespaces = namespaces.list_namespaces()
    assert len(initial_namespaces) == 1
    assert initial_namespaces[0].name == "takoc"

    # Create two namespaces
    namespaces.create_namespace(NamespaceCreateRequest(name="ns1", description="Namespace 1"))
    namespaces.create_namespace(NamespaceCreateRequest(name="ns2", description="Namespace 2"))

    # Verify namespace list - should include 2 user namespaces + 1 system namespace
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 3

    # Check namespace information
    ns_names = [ns.name for ns in all_namespaces]
    assert "ns1" in ns_names
    assert "ns2" in ns_names
    assert "takoc" in ns_names

    ns_descriptions = [ns.description for ns in all_namespaces]
    assert "Namespace 1" in ns_descriptions
    assert "Namespace 2" in ns_descriptions
    assert "System metadata namespace" in ns_descriptions


def test_get_namespace(temp_namespaces):
    """Test getting a single namespace"""
    namespaces, db = temp_namespaces

    # Create namespace
    namespaces.create_namespace(NamespaceCreateRequest(name="test_ns", description="Test namespace"))

    # Get namespace
    namespace = namespaces.get_namespace("test_ns")

    assert namespace is not None
    assert namespace.name == "test_ns"
    assert namespace.description == "Test namespace"


def test_get_nonexistent_namespace(temp_namespaces):
    """Test getting non-existent namespace"""
    namespaces, _ = temp_namespaces

    # Getting non-existent namespace should return None
    namespace = namespaces.get_namespace("nonexistent")
    assert namespace is None


def test_update_namespace(temp_namespaces):
    """Test updating namespace"""
    namespaces, _ = temp_namespaces

    # Create namespace
    namespaces.create_namespace(NamespaceCreateRequest(name="update_test", description="Original description"))

    # Update namespace
    namespaces.update_namespace("update_test", NamespaceUpdateRequest(description="Updated description"))

    # Verify update
    all_namespaces = namespaces.list_namespaces()
    updated_ns = next(ns for ns in all_namespaces if ns.name == "update_test")
    assert updated_ns.description == "Updated description"


def test_update_nonexistent_namespace(temp_namespaces):
    """Test updating non-existent namespace"""
    namespaces, _ = temp_namespaces

    # Updating non-existent namespace should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.update_namespace("nonexistent", NamespaceUpdateRequest(description="Description"))

    assert "not found" in str(excinfo.value)


def test_delete_namespace(temp_namespaces):
    """Test deleting namespace"""
    namespaces, db = temp_namespaces

    # Create namespace
    namespaces.create_namespace(NamespaceCreateRequest(name="delete_test", description="To be deleted"))

    # Verify namespace exists - should have 'takoc' + 'delete_test' = 2 namespaces
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 2
    namespace_names = [ns.name for ns in all_namespaces]
    assert "takoc" in namespace_names
    assert "delete_test" in namespace_names

    # Verify namespace directory exists
    namespace_dir = db.global_config.data_dir / "delete_test"
    assert namespace_dir.exists()

    # Delete namespace
    namespaces.delete_namespace("delete_test")

    # Verify namespace has been deleted - should have only 'takoc' left
    all_namespaces = namespaces.list_namespaces()
    assert len(all_namespaces) == 1
    assert all_namespaces[0].name == "takoc"

    # Verify namespace directory has been deleted
    assert not namespace_dir.exists()


def test_delete_nonexistent_namespace(temp_namespaces):
    """Test deleting non-existent namespace"""
    namespaces, _ = temp_namespaces

    # Deleting non-existent namespace should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.delete_namespace("nonexistent")

    assert "not found" in str(excinfo.value)


def test_create_duplicate_namespace(temp_namespaces):
    """Test creating duplicate namespace"""
    namespaces, _ = temp_namespaces

    # Create namespace
    namespaces.create_namespace(NamespaceCreateRequest(name="duplicate", description="First instance"))

    # Creating same namespace again should raise exception
    with pytest.raises(ValueError) as excinfo:
        namespaces.create_namespace(NamespaceCreateRequest(name="duplicate", description="Second instance"))

    assert "already exists" in str(excinfo.value)
