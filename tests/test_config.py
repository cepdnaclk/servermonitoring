"""Test configuration loading utilities."""

import json
from pathlib import Path

import pytest

from servermonitoring.config import (
    load_gpu_info,
    load_gpu_servers,
    load_json_config,
    load_storage_servers,
    load_student_batches,
)


def test_load_json_config_success(tmp_path):
    """Test successful JSON loading."""
    config_file = tmp_path / "test.json"
    config_data = {"key": "value", "number": 42}
    config_file.write_text(json.dumps(config_data))

    result = load_json_config(config_file)
    assert result == config_data


def test_load_json_config_not_found():
    """Test loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_json_config(Path("/nonexistent/file.json"))


def test_load_json_config_invalid_json(tmp_path):
    """Test loading invalid JSON raises JSONDecodeError."""
    config_file = tmp_path / "invalid.json"
    config_file.write_text("not valid json {")

    with pytest.raises(json.JSONDecodeError):
        load_json_config(config_file)


def test_load_storage_servers(tmp_path):
    """Test loading storage servers."""
    config_file = tmp_path / "servers.json"
    config_data = {
        "storage": {
            "server1": {"doc_url": "http://example.com"},
            "server2": {"doc_url": None},
        },
        "gpu": ["gpu1"],
    }
    config_file.write_text(json.dumps(config_data))

    result = load_storage_servers(config_file)
    assert result == config_data["storage"]


def test_load_storage_servers_empty(tmp_path):
    """Test loading when storage key is missing."""
    config_file = tmp_path / "servers.json"
    config_file.write_text(json.dumps({}))

    result = load_storage_servers(config_file)
    assert result == {}


def test_load_gpu_servers(tmp_path):
    """Test loading GPU servers."""
    config_file = tmp_path / "servers.json"
    config_data = {
        "storage": {},
        "gpu": ["server1", "server2", "server3"],
    }
    config_file.write_text(json.dumps(config_data))

    result = load_gpu_servers(config_file)
    assert result == ["server1", "server2", "server3"]


def test_load_gpu_servers_empty(tmp_path):
    """Test loading when gpu key is missing."""
    config_file = tmp_path / "servers.json"
    config_file.write_text(json.dumps({}))

    result = load_gpu_servers(config_file)
    assert result == []


def test_load_gpu_info(tmp_path):
    """Test loading GPU info."""
    info_file = tmp_path / "gpu-info.json"
    info_data = {
        "server1": {
            "0": {"active": True, "memory": 24000},
            "1": {"active": False, "memory": 12000},
        }
    }
    info_file.write_text(json.dumps(info_data))

    result = load_gpu_info(info_file)
    assert result == info_data


def test_load_student_batches(tmp_path):
    """Test loading student batches."""
    batches_file = tmp_path / "batches.json"
    batches_data = {"students": ["E20", "E21", "E22"]}
    batches_file.write_text(json.dumps(batches_data))

    result = load_student_batches(batches_file)
    assert result == {"e20", "e21", "e22"}


def test_load_student_batches_empty(tmp_path):
    """Test loading when students key is missing."""
    batches_file = tmp_path / "batches.json"
    batches_file.write_text(json.dumps({}))

    result = load_student_batches(batches_file)
    assert result == set()
