#!/usr/bin/env python3
"""Build all data files for Jekyll site."""

import argparse
import json
from pathlib import Path

from servermonitoring.config import (
    load_gpu_info,
    load_gpu_servers,
    load_storage_servers,
    load_student_batches,
)
from servermonitoring.gpu import build_gpu_data
from servermonitoring.storage import build_storage_data

ROOT_DIR = Path(__file__).resolve().parents[1]


def save_json(data: dict, output_path: Path) -> None:
    """Save data as formatted JSON.

    Args:
        data: Data to save
        output_path: Output file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {output_path}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Jekyll data files")
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=ROOT_DIR / "config",
        help="Config directory (default: config/)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT_DIR / "data",
        help="Data directory containing logs (default: data/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "_data",
        help="Output directory for JSON files (default: _data/)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days for GPU metrics (default: 90)",
    )
    args = parser.parse_args()

    # Load configurations
    print("Loading configurations...")
    servers_config = args.config_dir / "servers.json"
    gpu_info_config = args.config_dir / "gpu-info.json"
    batches_config = args.config_dir / "batches.json"

    storage_servers = load_storage_servers(servers_config)
    gpu_servers = load_gpu_servers(servers_config)
    gpu_info = load_gpu_info(gpu_info_config)
    student_batches = load_student_batches(batches_config)

    # Build storage data
    print("Building storage data...")
    storage_logs = args.data_dir / "logs" / "storage"
    storage_data = build_storage_data(storage_logs, storage_servers, student_batches)
    save_json(storage_data, args.output_dir / "storage.json")

    # Build GPU data
    print("Building GPU data...")
    gpu_logs = args.data_dir / "logs" / "gpu"
    gpu_data = build_gpu_data(gpu_logs, gpu_servers, gpu_info, args.days)
    save_json(gpu_data, args.output_dir / "gpu.json")

    # Build site metadata
    print("Building site metadata...")
    metadata = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "storage_servers": list(storage_servers.keys()),
        "gpu_servers": gpu_servers,
    }
    save_json(metadata, args.output_dir / "metadata.json")

    print("Data build complete!")


if __name__ == "__main__":
    main()
