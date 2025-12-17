import tempfile
from pathlib import Path

import pytest

from .file_io import Files


@pytest.fixture
def temp_dir():
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory(dir='.test') as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_data():
    return {
        "name": "test",
        "value": 123,
        "nested": {
            "key": "value"
        }
    }


def test_file_info_yaml(temp_dir, test_data):
    """Test getting YAML file information"""
    # Create YAML file
    yaml_file = temp_dir / "test.yaml"
    with open(yaml_file, "w") as f:
        import yaml
        yaml.dump(test_data, f)

    files = Files(dir=temp_dir, read_only=True, format="yaml")
    info = files.file_info("test")

    assert info is not None
    assert info[0] == yaml_file
    assert info[1] == "yaml"


def test_file_info_json(temp_dir, test_data):
    """Test getting JSON file information"""
    # Create JSON file
    json_file = temp_dir / "test.json"
    with open(json_file, "w") as f:
        import json
        json.dump(test_data, f)

    files = Files(dir=temp_dir, read_only=True, format="json")
    info = files.file_info("test")

    assert info is not None
    assert info[0] == json_file
    assert info[1] == "json"


def test_file_info_not_found(temp_dir):
    """Test when file does not exist"""
    files = Files(dir=temp_dir, read_only=True, format="yaml")
    info = files.file_info("non_existent")

    assert info is None


def test_read_yaml_file(temp_dir, test_data):
    """Test reading YAML file"""
    # Create YAML file
    yaml_file = temp_dir / "test.yaml"
    with open(yaml_file, "w") as f:
        import yaml
        yaml.dump(test_data, f)

    files = Files(dir=temp_dir, read_only=True, format="yaml")
    content = files.read_file("test")

    assert content == test_data


def test_read_json_file(temp_dir, test_data):
    """Test reading JSON file"""
    # Create JSON file
    json_file = temp_dir / "test.json"
    with open(json_file, "w") as f:
        import json
        json.dump(test_data, f)

    files = Files(dir=temp_dir, read_only=True, format="json")
    content = files.read_file("test")

    assert content == test_data


def test_write_yaml_file(temp_dir, test_data):
    """Test writing YAML file"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")
    files.write_file("test", test_data)

    # Verify file exists and contains correct content
    yaml_file = temp_dir / "test.yaml"
    assert yaml_file.exists()

    with open(yaml_file, "r") as f:
        import yaml
        content = yaml.safe_load(f)
        assert content == test_data


def test_write_json_file(temp_dir, test_data):
    """Test writing JSON file"""
    files = Files(dir=temp_dir, read_only=False, format="json")
    files.write_file("test", test_data)

    # Verify file exists and contains correct content
    json_file = temp_dir / "test.json"
    assert json_file.exists()

    with open(json_file, "r") as f:
        import json
        content = json.load(f)
        assert content == test_data


def test_write_read_only(temp_dir, test_data):
    """Test writing file in read-only mode"""
    files = Files(dir=temp_dir, read_only=True, format="yaml")

    from ..api.error import ReadOnlyError
    with pytest.raises(ReadOnlyError):
        files.write_file("test", test_data)


def test_delete_file(temp_dir, test_data):
    """Test deleting file"""
    # Create YAML file
    yaml_file = temp_dir / "test.yaml"
    with open(yaml_file, "w") as f:
        import yaml
        yaml.dump(test_data, f)

    files = Files(dir=temp_dir, read_only=False, format="yaml")
    files.delete_file("test")

    assert not yaml_file.exists()


def test_default_ext_yaml():
    """Test YAML default extension"""
    files = Files(dir=Path(".test"), read_only=True, format="yaml")
    assert files.default_ext == ".yaml"


def test_default_ext_json():
    """Test JSON default extension"""
    files = Files(dir=Path(".test"), read_only=True, format="json")
    assert files.default_ext == ".json"
