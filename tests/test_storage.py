"""Test storage data processing utilities."""

from pathlib import Path

from servermonitoring.storage import (
    build_storage_data,
    classify_babbage_user,
    parse_usage_gb,
    process_storage_log,
)


def test_parse_usage_gb_valid():
    """Test parsing valid usage strings."""
    assert parse_usage_gb("123.45") == 123.45
    assert parse_usage_gb("1.2") == 1.2
    assert parse_usage_gb("50") == 50.0


def test_parse_usage_gb_invalid():
    """Test parsing invalid usage strings."""
    assert parse_usage_gb("invalid") is None
    assert parse_usage_gb("") is None
    assert parse_usage_gb("G") is None


def test_classify_babbage_user_student_low_usage():
    """Test classification of current student with low usage."""
    student_batches = {"e20", "e21"}
    color, url = classify_babbage_user("/home/e21123/data", 30.0, student_batches)

    assert color is None
    assert url == "https://people.ce.pdn.ac.lk/students/e21/123/"


def test_classify_babbage_user_student_high_usage():
    """Test classification of current student with high usage."""
    student_batches = {"e20", "e21"}
    color, url = classify_babbage_user("/home/e21123/data", 60.0, student_batches)

    assert color == "yellow"
    assert url == "https://people.ce.pdn.ac.lk/students/e21/123/"


def test_classify_babbage_user_alumni_low_usage():
    """Test classification of alumni with low usage."""
    student_batches = {"e20", "e21"}
    color, url = classify_babbage_user("/home/e14158/data", 5.0, student_batches)

    assert color is None
    assert url == "https://people.ce.pdn.ac.lk/students/e14/158/"


def test_classify_babbage_user_alumni_high_usage():
    """Test classification of alumni with high usage."""
    student_batches = {"e20", "e21"}
    color, url = classify_babbage_user("/home/e14158/data", 15.0, student_batches)

    assert color == "orange"
    assert url == "https://people.ce.pdn.ac.lk/students/e14/158/"


def test_classify_babbage_user_no_match():
    """Test classification with folder not matching pattern."""
    student_batches = {"e20", "e21"}
    color, url = classify_babbage_user("/home/other/data", 50.0, student_batches)

    assert color is None
    assert url is None


def test_process_storage_log_empty_file(tmp_path):
    """Test processing empty log file."""
    log_file = tmp_path / "test.log"
    log_file.write_text("")

    entries = process_storage_log(log_file, "test", set())
    assert entries == []


def test_process_storage_log_nonexistent():
    """Test processing non-existent log file."""
    entries = process_storage_log(Path("/nonexistent.log"), "test", set())
    assert entries == []


def test_process_storage_log_valid_entries(tmp_path):
    """Test processing log file with valid entries."""
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "50.5G\t/home/user1\n"
        "100.0G\t/home/user2\n"
        "# comment line\n"
        "\n"
        "25.3G\t/home/user3\n"
    )

    entries = process_storage_log(log_file, "test", set())
    assert len(entries) == 3
    assert entries[0]["folder"] == "/home/user1"
    assert entries[0]["usage"] == "50.5G"
    assert entries[0]["usage_gb"] == 50.5


def test_process_storage_log_babbage_classification(tmp_path):
    """Test babbage server classification."""
    log_file = tmp_path / "babbage.log"
    log_file.write_text(
        "60.0G\t/home/e21123/data\n"
        "15.0G\t/home/e14158/files\n"
    )

    student_batches = {"e20", "e21"}
    entries = process_storage_log(log_file, "babbage", student_batches)

    assert len(entries) == 2
    assert entries[0]["color"] == "yellow"  # Student > 50GB
    assert entries[1]["color"] == "orange"  # Alumni > 10GB


def test_build_storage_data_no_logs(tmp_path):
    """Test building storage data with no logs."""
    servers = {"server1": {"doc_url": "http://example.com"}}
    student_batches = set()

    data = build_storage_data(tmp_path, servers, student_batches)

    assert "servers" in data
    assert "server1" in data["servers"]
    assert data["servers"]["server1"]["entries"] == []


def test_build_storage_data_with_logs(tmp_path):
    """Test building storage data with log files."""
    # Create log file
    log_file = tmp_path / "server1-20240101.csv"
    log_file.write_text("10.0G\t/home/user1\n20.0G\t/home/user2\n")

    servers = {"server1": {"doc_url": "http://example.com"}}
    student_batches = set()

    data = build_storage_data(tmp_path, servers, student_batches)

    assert "servers" in data
    assert "server1" in data["servers"]
    assert len(data["servers"]["server1"]["entries"]) == 2
    assert data["servers"]["server1"]["doc_url"] == "http://example.com"
