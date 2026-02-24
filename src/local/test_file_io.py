import tempfile
import time
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


def test_generate_unique_file_name_new(temp_dir):
    """Test generating unique file name for new file"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # No file exists yet, should return original name
    unique_name = files.generate_file_name("test_file")
    assert unique_name == "test_file"


def test_generate_unique_file_name_existing(temp_dir, test_data):
    """Test generating unique file name for existing file"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Create original file
    files.write_file("test_file", test_data)

    # Now file exists, should return name with timestamp
    unique_name = files.generate_file_name("test_file")
    assert unique_name != "test_file"
    assert "_" in unique_name
    assert unique_name.startswith("test_file_")


def test_generate_file_name_invalid_chars(temp_dir):
    """Test generating file name with invalid characters"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Test with invalid characters
    invalid_name = r"file<name>:with/invalid\chars|and?queries*and\"quotes"
    safe_name = files.generate_file_name(invalid_name)

    # All invalid characters should be replaced with underscores
    assert "<" not in safe_name
    assert ">" not in safe_name
    assert ":" not in safe_name
    assert "/" not in safe_name
    assert "\\" not in safe_name
    assert "|" not in safe_name
    assert "?" not in safe_name
    assert "*" not in safe_name
    assert '"' not in safe_name

    # Should still have the general structure with underscores replacing invalid chars
    assert "file_name" in safe_name
    assert "with_invalid_chars" in safe_name
    assert "and_queries" in safe_name


def test_generate_file_name_empty(temp_dir):
    """Test generating file name from empty base name"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Empty string should become "untitled"
    assert files.generate_file_name("") == "untitled"

    # String with only invalid characters should become a string of underscores
    assert files.generate_file_name("<>:\"/\\|?*") == "_________"

    # String with only spaces should become "untitled"
    assert files.generate_file_name("   ") == "untitled"


def test_generate_file_name_trimming(temp_dir):
    """Test trimming spaces from file name"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Should trim leading/trailing spaces
    assert files.generate_file_name("  test file  ") == "test file"

    # Should preserve internal spaces (not replace with underscores)
    assert "test file with spaces" in files.generate_file_name("  test file with spaces  ")


def test_generate_file_name_truncation(temp_dir):
    """Test truncating long file names"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Create a very long file name
    long_name = "x" * 100
    safe_name = files.generate_file_name(long_name)

    # Should be truncated to 60 characters
    assert len(safe_name) == 60
    assert safe_name == "x" * 60


def test_generate_file_name_truncation_with_timestamp(temp_dir, test_data):
    """Test truncating when adding timestamp would exceed limits"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Create a file with a name that's already close to 255 chars
    base_name = "x" * 250

    # First create the file
    files.write_file(base_name[:60], test_data)

    # Now generate name - should truncate more to fit timestamp
    safe_name = files.generate_file_name(base_name)

    # Should be less than 255 characters even with timestamp
    timestamp = safe_name.split("_")[-1]
    assert len(safe_name) <= 255
    assert safe_name.endswith("_" + timestamp)


def test_generate_file_name_exact_lengths(temp_dir):
    """Test edge cases with exact lengths"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Exactly 60 characters
    name_60 = "x" * 60
    assert files.generate_file_name(name_60) == name_60

    # Exactly 61 characters
    name_61 = "x" * 61
    assert files.generate_file_name(name_61) == "x" * 60


def test_generate_file_name_unicode(temp_dir):
    """Test generating file names with Unicode characters"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Unicode should be preserved
    unicode_name = "测试文件名称"  # Chinese characters
    assert files.generate_file_name(unicode_name) == unicode_name

    # Unicode with invalid characters should still work
    unicode_with_invalid = "测试<文件>:名称"
    result = files.generate_file_name(unicode_with_invalid)
    assert "<" not in result
    assert ":" not in result
    assert "测试" in result
    assert "文件" in result
    assert "名称" in result


def test_generate_file_name_multiple_duplicates(temp_dir, test_data):
    """Test generating unique names for multiple duplicates"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Create initial file
    files.write_file("test", test_data)

    # Generate names for duplicates with a small delay to ensure different timestamps
    name1 = files.generate_file_name("test")

    # Create the file with the first generated name to ensure uniqueness
    files.write_file(name1, test_data)

    # Wait for at least 1 second to ensure timestamp changes
    time.sleep(1)

    # Generate another name for a duplicate
    name2 = files.generate_file_name("test")

    # Both should be unique and different from original and each other
    assert name1 != "test"
    assert name2 != "test"
    assert name2 != name1
    assert name1.startswith("test_")
    assert name2.startswith("test_")


def test_generate_file_name_with_extension_in_base(temp_dir):
    """Test that extensions in base name are preserved"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")

    # Base name with extension (should be preserved since our method doesn't handle extensions)
    base_with_ext = "test_file.txt"
    result = files.generate_file_name(base_with_ext)
    assert result == base_with_ext

    # With invalid characters and extension
    invalid_with_ext = "test<file>:name.txt"
    result = files.generate_file_name(invalid_with_ext)
    assert ".txt" in result
    assert "test" in result
    assert "file" in result
    assert "name" in result
