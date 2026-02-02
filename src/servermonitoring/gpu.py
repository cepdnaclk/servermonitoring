"""GPU data processing utilities."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd


def clean_numeric(series: pd.Series) -> pd.Series:
    """Clean and convert series to numeric values.

    Args:
        series: Pandas series with potentially non-numeric values

    Returns:
        Series with cleaned numeric values
    """
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^0-9.]+", "", regex=True),
        errors="coerce",
    )


def read_gpu_logs(
    logs_dir: Path, servers: list[str], days: int = 90
) -> dict[str, pd.DataFrame]:
    """Read GPU log files for specified servers.

    Args:
        logs_dir: Directory containing GPU log CSV files
        servers: List of server names to process
        days: Number of days to include (default: 90)

    Returns:
        Dictionary mapping server names to DataFrames
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    data: dict[str, pd.DataFrame] = {}

    for log_file in sorted(logs_dir.glob("*")):
        if log_file.suffix.lower() not in {".csv", ".log"}:
            continue

        server = log_file.name.split("-")[0]
        if server not in servers:
            continue

        try:
            frame = pd.read_csv(log_file)
        except Exception:
            continue

        if "timestamp" not in frame.columns:
            continue

        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
        frame = frame.dropna(subset=["timestamp"])
        frame = frame[frame["timestamp"] >= cutoff_date]

        if frame.empty:
            continue

        if server not in data:
            data[server] = frame
        else:
            data[server] = pd.concat([data[server], frame], ignore_index=True)

    return data


def aggregate_gpu_metrics(
    df: pd.DataFrame, gpu_id: str
) -> dict[str, list[dict[str, Any]]]:
    """Aggregate GPU metrics by date.

    Args:
        df: DataFrame with GPU metrics
        gpu_id: GPU identifier

    Returns:
        Dictionary with daily aggregated metrics
    """
    gpu_col = f"gpu.{gpu_id}.gpu"
    mem_col = f"gpu.{gpu_id}.memory"

    if gpu_col not in df.columns and mem_col not in df.columns:
        return {}

    df = df.copy()
    df["date"] = df["timestamp"].dt.date

    result = {}

    if gpu_col in df.columns:
        gpu_series = clean_numeric(df[gpu_col])
        daily_gpu = gpu_series.groupby(df["date"]).mean()
        result["utilization"] = [
            {"date": str(date), "value": float(value)}
            for date, value in daily_gpu.items()
            if pd.notna(value)
        ]

    if mem_col in df.columns:
        mem_series = clean_numeric(df[mem_col])
        daily_mem = mem_series.groupby(df["date"]).mean()
        result["memory"] = [
            {"date": str(date), "value": float(value)}
            for date, value in daily_mem.items()
            if pd.notna(value)
        ]

    return result


def build_gpu_data(
    logs_dir: Path,
    servers: list[str],
    gpu_info: dict[str, Any],
    days: int = 90,
) -> dict[str, Any]:
    """Build complete GPU data for Jekyll.

    Args:
        logs_dir: Directory containing GPU log files
        servers: List of server names
        gpu_info: GPU configuration info
        days: Number of days to include

    Returns:
        Dictionary with GPU data for all servers
    """
    logs = read_gpu_logs(logs_dir, servers, days)
    gpu_data = {}

    for server in servers:
        if server not in logs:
            gpu_data[server] = {"name": server, "gpus": {}}
            continue

        df = logs[server]
        server_gpu_info = gpu_info.get(server, {})
        gpus = {}

        for gpu_id, info in server_gpu_info.items():
            metrics = aggregate_gpu_metrics(df, gpu_id)
            gpus[gpu_id] = {
                "id": gpu_id,
                "active": info.get("active", True),
                "memory_limit": info.get("memory", 0),
                "metrics": metrics,
            }

        gpu_data[server] = {"name": server, "gpus": gpus}

    return {"servers": gpu_data}
