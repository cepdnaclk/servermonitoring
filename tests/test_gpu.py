"""Test GPU data processing utilities."""

from datetime import datetime, timedelta

import pandas as pd

from servermonitoring.gpu import (
    aggregate_gpu_metrics,
    build_gpu_data,
    clean_numeric,
    read_gpu_logs,
)


def test_clean_numeric_valid():
    """Test cleaning numeric series."""
    series = pd.Series(["10", "20.5", "30"])
    result = clean_numeric(series)
    assert result.tolist() == [10.0, 20.5, 30.0]


def test_clean_numeric_with_text():
    """Test cleaning series with text."""
    series = pd.Series(["10%", "20.5MB", "30GB"])
    result = clean_numeric(series)
    assert result.tolist() == [10.0, 20.5, 30.0]


def test_clean_numeric_invalid():
    """Test cleaning series with invalid data."""
    series = pd.Series(["invalid", "N/A", ""])
    result = clean_numeric(series)
    assert all(pd.isna(result))


def test_read_gpu_logs_no_files(tmp_path):
    """Test reading GPU logs with no files."""
    servers = ["server1"]
    result = read_gpu_logs(tmp_path, servers)
    assert result == {}


def test_read_gpu_logs_valid_file(tmp_path):
    """Test reading valid GPU log file."""
    log_file = tmp_path / "server1-20240101.csv"
    now = datetime.now()
    df = pd.DataFrame(
        {
            "timestamp": [
                now - timedelta(days=1),
                now - timedelta(days=2),
            ],
            "gpu.0.gpu": [50, 60],
            "gpu.0.memory": [1000, 1200],
        }
    )
    df.to_csv(log_file, index=False)

    servers = ["server1"]
    result = read_gpu_logs(tmp_path, servers, days=90)

    assert "server1" in result
    assert len(result["server1"]) == 2


def test_read_gpu_logs_old_data_filtered(tmp_path):
    """Test that old data is filtered out."""
    log_file = tmp_path / "server1-20240101.csv"
    now = datetime.now()
    df = pd.DataFrame(
        {
            "timestamp": [
                now - timedelta(days=100),  # Too old
                now - timedelta(days=10),  # Recent
            ],
            "gpu.0.gpu": [50, 60],
        }
    )
    df.to_csv(log_file, index=False)

    servers = ["server1"]
    result = read_gpu_logs(tmp_path, servers, days=90)

    assert "server1" in result
    assert len(result["server1"]) == 1


def test_aggregate_gpu_metrics_no_columns():
    """Test aggregation with missing columns."""
    df = pd.DataFrame({"timestamp": [datetime.now()], "other": [1]})
    result = aggregate_gpu_metrics(df, "0")
    assert result == {}


def test_aggregate_gpu_metrics_utilization():
    """Test aggregating utilization metrics."""
    now = datetime.now()
    df = pd.DataFrame(
        {
            "timestamp": [
                now.replace(hour=1),
                now.replace(hour=2),
                now.replace(hour=3),
            ],
            "gpu.0.gpu": [50, 60, 70],
        }
    )

    result = aggregate_gpu_metrics(df, "0")

    assert "utilization" in result
    assert len(result["utilization"]) == 1
    assert result["utilization"][0]["value"] == 60.0  # mean


def test_aggregate_gpu_metrics_memory():
    """Test aggregating memory metrics."""
    now = datetime.now()
    df = pd.DataFrame(
        {
            "timestamp": [
                now.replace(hour=1),
                now.replace(hour=2),
            ],
            "gpu.0.memory": [1000, 2000],
        }
    )

    result = aggregate_gpu_metrics(df, "0")

    assert "memory" in result
    assert len(result["memory"]) == 1
    assert result["memory"][0]["value"] == 1500.0


def test_build_gpu_data_no_logs(tmp_path):
    """Test building GPU data with no logs."""
    servers = ["server1"]
    gpu_info = {"server1": {"0": {"active": True, "memory": 24000}}}

    result = build_gpu_data(tmp_path, servers, gpu_info)

    assert "servers" in result
    assert "server1" in result["servers"]
    assert result["servers"]["server1"]["gpus"] == {}


def test_build_gpu_data_with_logs(tmp_path):
    """Test building GPU data with log files."""
    log_file = tmp_path / "server1-20240101.csv"
    now = datetime.now()
    df = pd.DataFrame(
        {
            "timestamp": [now - timedelta(days=1), now - timedelta(days=2)],
            "gpu.0.gpu": [50, 60],
            "gpu.0.memory": [1000, 1200],
        }
    )
    df.to_csv(log_file, index=False)

    servers = ["server1"]
    gpu_info = {"server1": {"0": {"active": True, "memory": 24000}}}

    result = build_gpu_data(tmp_path, servers, gpu_info)

    assert "servers" in result
    assert "server1" in result["servers"]
    assert "0" in result["servers"]["server1"]["gpus"]
    gpu_data = result["servers"]["server1"]["gpus"]["0"]
    assert gpu_data["active"] is True
    assert gpu_data["memory_limit"] == 24000
