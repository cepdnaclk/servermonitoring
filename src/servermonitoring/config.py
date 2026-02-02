"""Configuration file loading utilities."""

import json
from pathlib import Path
from typing import Any


def load_json_config(config_path: Path) -> dict[str, Any]:
    """Load a JSON configuration file.

    Args:
        config_path: Path to the JSON config file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_servers_config(config_path: Path) -> dict[str, Any]:
    """Load servers configuration.

    Args:
        config_path: Path to servers.json

    Returns:
        Server configuration dictionary
    """
    return load_json_config(config_path)


def load_storage_servers(config_path: Path) -> dict[str, Any]:
    """Load storage server configuration.

    Args:
        config_path: Path to servers.json

    Returns:
        Storage server configuration
    """
    config = load_servers_config(config_path)
    return config.get("storage", {})


def load_gpu_servers(config_path: Path) -> list[str]:
    """Load GPU server list.

    Args:
        config_path: Path to servers.json

    Returns:
        List of GPU server names
    """
    config = load_servers_config(config_path)
    return config.get("gpu", [])


def load_gpu_info(info_path: Path) -> dict[str, Any]:
    """Load GPU information configuration.

    Args:
        info_path: Path to gpu-info.json

    Returns:
        GPU info configuration
    """
    return load_json_config(info_path)


def load_student_batches(batches_path: Path) -> set[str]:
    """Load student batch identifiers.

    Args:
        batches_path: Path to batches.json

    Returns:
        Set of batch identifiers (lowercase)
    """
    config = load_json_config(batches_path)
    batches = config.get("students", [])
    return {batch.lower() for batch in batches}
