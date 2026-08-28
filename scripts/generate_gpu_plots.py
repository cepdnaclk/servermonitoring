import argparse
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT_DIR / "config" / "servers.json"
DEFAULT_GPU_INFO = ROOT_DIR / "config" / "gpu-info.json"
DEFAULT_LOGS_DIR = ROOT_DIR / "data" / "logs" / "gpu"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "docs" / "reports" / "server-gpu-util" / "plots"
DEFAULT_OUTPUT_INDEX = ROOT_DIR / "docs" / "reports" / "server-gpu-util" / "index.html"


def load_servers(config_path: Path) -> list[str]:
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    return config.get("gpu", [])


def load_gpu_info(info_path: Path) -> dict:
    with info_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clean_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^0-9.]+", "", regex=True),
        errors="coerce",
    )


def read_gpu_logs(logs_dir: Path, servers: list[str]) -> dict[str, pd.DataFrame]:
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

        frame = frame.rename(columns=lambda col: col.strip())
        if "gpuid" not in frame.columns and "index" in frame.columns:
            frame = frame.rename(columns={"index": "gpuid"})
        frame = frame.dropna()

        if "timestamp" not in frame.columns or "gpuid" not in frame.columns:
            continue

        frame["gpuid"] = pd.to_numeric(frame["gpuid"], errors="coerce")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
        if frame["timestamp"].dt.tz is not None:
            frame["timestamp"] = frame["timestamp"].dt.tz_localize(None)
        frame = frame.dropna(subset=["gpuid", "timestamp"])
        frame["gpuid"] = frame["gpuid"].astype(int)

        for column in ["power.draw [W]", "utilization.gpu [%]", "memory.used [MiB]"]:
            if column in frame.columns:
                frame[column] = clean_numeric(frame[column])

        if server not in data:
            data[server] = frame
        else:
            data[server] = pd.concat([data[server], frame], ignore_index=True)

    return data


def build_gpu_plots(
    logs_dir: Path,
    gpu_info_path: Path,
    output_dir: Path,
    output_index: Path,
    servers: list[str],
    days: int = 90,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_index.parent.mkdir(parents=True, exist_ok=True)

    gpu_info = load_gpu_info(gpu_info_path)
    raw_data = read_gpu_logs(logs_dir, servers)

    if not raw_data:
        output_index.write_text(
            "<p><em>No GPU logs found to generate plots.</em></p>", encoding="utf-8"
        )
        return

    today = pd.Timestamp.now().normalize()
    date_range = pd.date_range(end=today, periods=days, freq="D")

    plot_files = []
    plot_bookmarks = []

    for server, frame in raw_data.items():
        server_info = gpu_info.get(server, {})
        for gpuid, info in server_info.items():
            if not info.get("active", False):
                continue
            gpuid_int = int(gpuid)
            print(f"Generating GPU plot for {server} GPU {gpuid_int}...")
            gpu_frame = frame[frame["gpuid"] == gpuid_int].copy()
            if gpu_frame.empty:
                continue

            daily = (
                gpu_frame.groupby(gpu_frame["timestamp"].dt.floor("D"))
                .mean(numeric_only=True)
                .reindex(date_range)
            )
            first_valid = daily.dropna(how="all").index.min()
            if first_valid is not None:
                daily.loc[first_valid:] = daily.loc[first_valid:].fillna(0)

            utilization = daily.get("utilization.gpu [%]", pd.Series(index=daily.index))
            memory_used = daily.get("memory.used [MiB]", pd.Series(index=daily.index))
            utilization_mean = utilization.dropna().mean()
            memory_mean = memory_used.dropna().mean()

            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(
                daily.index,
                utilization,
                "*-r",
                lw=0.6,
                markersize=3,
                label="utilization.gpu [%]",
            )
            ax.set_ylabel("utilization.gpu [%]", color="r")
            ax.set_ylim(0, 100)
            if pd.notna(utilization_mean):
                ax.axhline(utilization_mean, color="r", linestyle=":", lw=1)

            ax2 = ax.twinx()
            ax2.plot(
                daily.index,
                memory_used,
                "*-b",
                lw=0.6,
                markersize=3,
                label="memory.used [MiB]",
            )
            ax2.set_ylabel("memory.used [MiB]", color="b")
            memory_limit = info.get("memory") or max(float(memory_used.max() or 0), 1.0)
            ax2.set_ylim(0, memory_limit)
            if pd.notna(memory_mean):
                ax2.axhline(memory_mean, color="b", linestyle=":", lw=1)

            ax.set_title(f"{server} GPU {gpuid_int} (last {days} days)")
            fig.autofmt_xdate(rotation=45)

            filename = f"plot-{server}-{gpuid_int}.png"
            output_path = output_dir / filename
            fig.savefig(output_path, bbox_inches="tight")
            plt.close(fig)
            plot_files.append(filename)
            plot_bookmarks.append((server, gpuid_int, filename))

    output_index_lines = [
        "<html>",
        "<head>",
        "<title>Server GPU Usage</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 0; }",
        ".header { padding: 18px 20px; background: #e9eef7; font-size: 18px; font-weight: 600; }",
        ".nav { background: #0b3d91; color: #fff; padding: 10px 20px; }",
        ".nav a { color: #fff; text-decoration: none; margin-right: 12px; font-weight: bold; padding: 6px 10px; border-radius: 4px; display: inline-block; }",
        ".nav a.active { background: #ffffff; color: #0b3d91; }",
        ".content { padding: 20px; }",
        ".bookmarks ol { padding-left: 20px; }",
        ".bookmarks li { margin: 6px 0; }",
        ".bookmarks a { text-decoration: none; }",
        ".plot { margin-bottom: 20px; }",
        "</style>",
        "</head>",
        "<body>",
        "<div class=\"header\">",
        "  <a href=\"https://www.pdn.ac.lk/\">University of Peradeniya</a>:",
        "  <a href=\"https://www.ce.pdn.ac.lk/\">Department of Computer Engineering</a>:",
        "  Server Monitoring",
        "</div>",
        "<div class=\"nav\">",
        "  <a href=\"../../\">Home</a>",
        "  <a href=\"../server-storage-util/\">Storage</a>",
        "  <a class=\"active\" href=\"../server-gpu-util/\">GPU</a>",
        "</div>",
        "<div class=\"content\">",
        "<h1>Server GPU Usage</h1>",
        "<p>Plots show daily mean utilization and memory usage for the last 90 days.</p>",
        "<div class=\"bookmarks\">",
        "  <h3>Contents</h3>",
        "  <ol>",
    ]

    for server, gpuid_int, _ in plot_bookmarks:
        anchor = f"{server}-gpu-{gpuid_int}"
        output_index_lines.append(
            f'    <li><a href="#{anchor}">{server} GPU {gpuid_int}</a></li>'
        )

    output_index_lines.extend(
        [
            "  </ol>",
            "</div>",
        ]
    )

    for server, gpuid_int, filename in plot_bookmarks:
        anchor = f"{server}-gpu-{gpuid_int}"
        output_index_lines.append(
            f'<div class="plot" id="{anchor}"><img src="plots/{filename}" alt="{filename}"></div>'
        )

    output_index_lines.extend(
        [
            "<hr>",
            "<footer>",
            f"  <p>This page was last updated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}.</p>",
            "  <p>This webpage was vibecoded by <a href=\"https://people.ce.pdn.ac.lk/students/e14/158\">E/14/Gihan</a> with GPT-5.2 Codex. Feel free to email him regarding any questions.</p>",
            "  <p>The sourcecode is available <a href=\"https://github.com/cepdnaclk/servermonitoring\">here</a>.</p>",
            "</footer>",
            "</div>",
            "</body>",
            "</html>",
        ]
    )
    output_index.write_text("\n".join(output_index_lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GPU utilization plots.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to server config JSON.",
    )
    parser.add_argument(
        "--gpu-info",
        type=Path,
        default=DEFAULT_GPU_INFO,
        help="Path to GPU info JSON.",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=DEFAULT_LOGS_DIR,
        help="Directory containing GPU log CSV files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for plots.",
    )
    parser.add_argument(
        "--out-index",
        type=Path,
        default=DEFAULT_OUTPUT_INDEX,
        help="Output HTML index for plots.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to include in plots.",
    )
    args = parser.parse_args()

    servers = load_servers(args.config)
    build_gpu_plots(
        logs_dir=args.logs_dir,
        gpu_info_path=args.gpu_info,
        output_dir=args.out_dir,
        output_index=args.out_index,
        servers=servers,
        days=args.days,
    )
    print(f"GPU plots generated in {args.out_dir}")


if __name__ == "__main__":
    main()
