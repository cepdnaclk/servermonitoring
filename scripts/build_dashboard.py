import argparse
import datetime
from pathlib import Path

from generate_gpu_plots import build_gpu_plots, load_servers as load_gpu_servers
from generate_storage_report import (
    build_storage_report,
    load_storage_servers,
    load_student_batches,
)
from sync_logs import sync_logs


ROOT_DIR = Path(__file__).resolve().parents[1]


def write_root_index(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    index_path = output_root / "index.html"
    index_path.write_text(
        f"""<html>
<head>
<title>Server Monitoring Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; }}
.header {{ padding: 18px 20px; background: #e9eef7; font-size: 18px; font-weight: 600; }}
.nav {{ background: #0b3d91; color: #fff; padding: 10px 20px; }}
.nav a {{ color: #fff; text-decoration: none; margin-right: 12px; font-weight: bold; padding: 6px 10px; border-radius: 4px; display: inline-block; }}
.nav a.active {{ background: #ffffff; color: #0b3d91; }}
.content {{ padding: 20px; }}
</style>
</head>
<body>
<div class="header">
  <a href="https://www.pdn.ac.lk/">University of Peradeniya</a>:
  <a href="https://www.ce.pdn.ac.lk/">Department of Computer Engineering</a>:
  Server Monitoring
</div>
<div class="nav">
  <a class="active" href="index.html">Home</a>
  <a href="reports/server-storage-util/index.html">Storage</a>
  <a href="reports/server-gpu-util/index.html">GPU</a>
</div>
<div class="content">
  <h1>Server Monitoring Dashboard</h1>
  <p>Daily updated storage and GPU utilization reports.</p>
  <ul>
    <li><a href="reports/server-storage-util/index.html">Storage Usage Report</a></li>
    <li><a href="reports/server-gpu-util/index.html">GPU Usage Plots</a></li>
  </ul>
  <hr>
  <footer>
    <p>This page was last updated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.</p>
    <p>This webpage was vibecoded by <a href="https://people.ce.pdn.ac.lk/students/e14/158">E/14/Gihan</a> with GPT-5.2 Codex. Feel free to email him regarding any questions.</p>
    <p>The sourcecode is available <a href="https://github.com/cepdnaclk/servermonitoring">here</a>.</p>
  </footer>
</div>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dashboard assets.")
    parser.add_argument(
        "--base-url",
        default="https://tesla.ce.pdn.ac.lk/servermonitoring/",
        help="Base URL for data source (used to derive default log URLs).",
    )
    parser.add_argument(
        "--download-logs",
        action="store_true",
        help="Download logs from the data source before building reports.",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=ROOT_DIR / "config",
        help="Config directory containing servers.json and gpu-info.json.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT_DIR / "data",
        help="Data directory containing logs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT_DIR / "docs",
        help="Output root directory (GitHub Pages).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to include in GPU plots.",
    )
    args = parser.parse_args()

    storage_logs = args.data_dir / "logs" / "storage"
    gpu_logs = args.data_dir / "logs" / "gpu"

    if args.download_logs:
        logging_url = f"{args.base_url.rstrip('/')}/logging/"
        sync_logs(logging_url, storage_logs, gpu_logs)

    servers_config = args.config_dir / "servers.json"
    gpu_info = args.config_dir / "gpu-info.json"

    storage_servers = load_storage_servers(servers_config)
    student_batches = load_student_batches(args.config_dir / "batches.json")
    output_storage = args.output_root / "reports" / "server-storage-util" / "index.html"

    gpu_servers = load_gpu_servers(servers_config)
    output_gpu_dir = args.output_root / "reports" / "server-gpu-util" / "plots"
    output_gpu_index = args.output_root / "reports" / "server-gpu-util" / "index.html"

    build_storage_report(storage_logs, output_storage, storage_servers, student_batches)
    build_gpu_plots(
        logs_dir=gpu_logs,
        gpu_info_path=gpu_info,
        output_dir=output_gpu_dir,
        output_index=output_gpu_index,
        servers=gpu_servers,
        days=args.days,
    )
    write_root_index(args.output_root)
    print("Dashboard build complete.")


if __name__ == "__main__":
    main()
