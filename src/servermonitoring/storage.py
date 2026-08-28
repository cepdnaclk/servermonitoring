"""Storage data processing utilities."""

import re
from pathlib import Path
from typing import Any


def parse_usage_gb(usage: str) -> float | None:
    """Parse usage string to extract GB value.

    Args:
        usage: Usage string like "123.45G" or "1.2T"

    Returns:
        Usage in GB, or None if parsing fails
    """
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)", usage)
    if not match:
        return None
    return float(match.group(1))


def classify_babbage_user(
    folder: str, usage_gb: float | None, student_batches: set[str]
) -> tuple[str | None, str | None]:
    """Classify babbage server user and determine highlighting.

    Args:
        folder: Folder path containing user ID (e.g., "/home/e14123/...")
        usage_gb: Storage usage in GB
        student_batches: Set of current student batch IDs

    Returns:
        Tuple of (color, profile_url) where color is 'yellow' or 'orange'
        for highlighting, or None if no highlighting needed
    """
    match = re.search(r"/(e\d{5})(?:/|$)", folder)
    if not match:
        return None, None

    student_id = match.group(1)
    batch = student_id[:3].lower()
    profile_url = f"https://people.ce.pdn.ac.lk/students/{batch}/{student_id[3:6]}/"

    if batch in student_batches:
        # Current student: highlight if > 50GB
        if usage_gb is not None and usage_gb > 50:
            return "yellow", profile_url
        return None, profile_url

    # Alumni: highlight if > 10GB
    if usage_gb is not None and usage_gb > 10:
        return "orange", profile_url

    return None, profile_url


def process_storage_log(
    log_path: Path, server_name: str, student_batches: set[str]
) -> list[dict[str, Any]]:
    """Process a storage log file into structured data.

    Args:
        log_path: Path to the storage log file
        server_name: Name of the server
        student_batches: Set of current student batch IDs

    Returns:
        List of storage entry dictionaries
    """
    entries = []

    if not log_path.exists():
        return entries

    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue

            usage, folder = parts
            usage_gb = parse_usage_gb(usage)

            entry: dict[str, Any] = {
                "folder": folder,
                "usage": usage,
                "usage_gb": usage_gb,
            }

            # Add classification for babbage
            if server_name == "babbage":
                color, profile_url = classify_babbage_user(
                    folder, usage_gb, student_batches
                )
                if color:
                    entry["color"] = color
                if profile_url:
                    entry["profile_url"] = profile_url

            entries.append(entry)

    return entries


def build_storage_data(
    logs_dir: Path,
    servers: dict[str, Any],
    student_batches: set[str],
) -> dict[str, Any]:
    """Build complete storage data for Jekyll.

    Args:
        logs_dir: Directory containing storage log files
        servers: Storage server configuration
        student_batches: Set of current student batch IDs

    Returns:
        Dictionary with storage data for all servers
    """
    storage_data = {}

    for server_name, server_config in servers.items():
        log_files = list(logs_dir.glob(f"{server_name}-*.csv"))
        if not log_files:
            log_files = list(logs_dir.glob(f"{server_name}-*.log"))

        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            entries = process_storage_log(latest_log, server_name, student_batches)
        else:
            entries = []

        storage_data[server_name] = {
            "name": server_name,
            "doc_url": server_config.get("doc_url"),
            "entries": entries,
        }

    return {"servers": storage_data}
