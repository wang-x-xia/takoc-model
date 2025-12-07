import pytest
import os
import tempfile
from pathlib import Path

from .file_io import Files, FILE_FORMAT

@pytest.fixture
def temp_dir():
    # 创建临时目录用于测试
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
    """测试获取YAML文件信息"""
    # 创建YAML文件
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
    """测试获取JSON文件信息"""
    # 创建JSON文件
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
    """测试文件不存在时的情况"""
    files = Files(dir=temp_dir, read_only=True, format="yaml")
    info = files.file_info("non_existent")
    
    assert info is None

def test_read_yaml_file(temp_dir, test_data):
    """测试读取YAML文件"""
    # 创建YAML文件
    yaml_file = temp_dir / "test.yaml"
    with open(yaml_file, "w") as f:
        import yaml
        yaml.dump(test_data, f)
    
    files = Files(dir=temp_dir, read_only=True, format="yaml")
    content = files.read_file("test")
    
    assert content == test_data

def test_read_json_file(temp_dir, test_data):
    """测试读取JSON文件"""
    # 创建JSON文件
    json_file = temp_dir / "test.json"
    with open(json_file, "w") as f:
        import json
        json.dump(test_data, f)
    
    files = Files(dir=temp_dir, read_only=True, format="json")
    content = files.read_file("test")
    
    assert content == test_data

def test_write_yaml_file(temp_dir, test_data):
    """测试写入YAML文件"""
    files = Files(dir=temp_dir, read_only=False, format="yaml")
    files.write_file("test", test_data)
    
    # 验证文件存在并包含正确内容
    yaml_file = temp_dir / "test.yaml"
    assert yaml_file.exists()
    
    with open(yaml_file, "r") as f:
        import yaml
        content = yaml.safe_load(f)
        assert content == test_data

def test_write_json_file(temp_dir, test_data):
    """测试写入JSON文件"""
    files = Files(dir=temp_dir, read_only=False, format="json")
    files.write_file("test", test_data)
    
    # 验证文件存在并包含正确内容
    json_file = temp_dir / "test.json"
    assert json_file.exists()
    
    with open(json_file, "r") as f:
        import json
        content = json.load(f)
        assert content == test_data

def test_write_read_only(temp_dir, test_data):
    """测试只读模式下写入文件"""
    files = Files(dir=temp_dir, read_only=True, format="yaml")
    
    with pytest.raises(PermissionError):
        files.write_file("test", test_data)

def test_delete_file(temp_dir, test_data):
    """测试删除文件"""
    # 创建YAML文件
    yaml_file = temp_dir / "test.yaml"
    with open(yaml_file, "w") as f:
        import yaml
        yaml.dump(test_data, f)
    
    files = Files(dir=temp_dir, read_only=False, format="yaml")
    files.delete_file("test")
    
    assert not yaml_file.exists()

def test_default_ext_yaml():
    """测试YAML默认扩展名"""
    files = Files(dir=Path(".test"), read_only=True, format="yaml")
    assert files.default_ext == ".yaml"

def test_default_ext_json():
    """测试JSON默认扩展名"""
    files = Files(dir=Path(".test"), read_only=True, format="json")
    assert files.default_ext == ".json"
