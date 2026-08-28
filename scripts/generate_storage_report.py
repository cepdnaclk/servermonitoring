import argparse
import datetime
import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT_DIR / "config" / "servers.json"
DEFAULT_BATCHES = ROOT_DIR / "config" / "batches.json"
DEFAULT_LOGS_DIR = ROOT_DIR / "data" / "logs" / "storage"
DEFAULT_OUTPUT = ROOT_DIR / "docs" / "reports" / "server-storage-util" / "index.html"


def load_storage_servers(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    return config.get("storage", {})


def load_student_batches(config_path: Path) -> set[str]:
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    batches = config.get("students", [])
    return {batch.lower() for batch in batches}


def parse_usage_gb(usage: str) -> float | None:
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)", usage)
    if not match:
        return None
    return float(match.group(1))


def classify_babbage(
    folder: str, usage_gb: float | None, student_batches: set[str]
) -> tuple[str | None, str | None]:
    match = re.search(r"/(e\d{5})(?:/|$)", folder)
    if not match:
        return None, None
    student_id = match.group(1)
    batch = student_id[:3].lower()
    profile_url = f"https://people.ce.pdn.ac.lk/students/{batch}/{student_id[3:6]}/"
    if batch in student_batches:
        if usage_gb is not None and usage_gb > 50:
            return "yellow", profile_url
        return None, profile_url
    if usage_gb is not None and usage_gb > 10:
        return "orange", profile_url
    return None, profile_url


def build_storage_report(
    logs_dir: Path,
    output_file: Path,
    storage_servers: dict,
    student_batches: set[str],
    generated_at: datetime.datetime | None = None,
) -> None:
    generated_at = generated_at or datetime.datetime.now()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f_out:
        f_out.write(
            """<html>
<head>
<title>Server Storage Usage</title>
<style>
body { font-family: Arial, sans-serif; margin: 0; }
.header { padding: 18px 20px; background: #e9eef7; font-size: 18px; font-weight: 600; }
.nav { background: #0b3d91; color: #fff; padding: 10px 20px; }
.nav a { color: #fff; text-decoration: none; margin-right: 12px; font-weight: bold; padding: 6px 10px; border-radius: 4px; display: inline-block; }
.nav a.active { background: #ffffff; color: #0b3d91; }
.content { padding: 20px; }
.bookmarks ul { list-style: none; padding-left: 0; }
.bookmarks li { margin: 6px 0; }
.bookmarks a { text-decoration: none; }
table { width: auto; }
footer { padding: 10px 20px 20px 20px; }
</style>
</head>
<body>
<div class="header">
  <a href="https://www.pdn.ac.lk/">University of Peradeniya</a>:
  <a href="https://www.ce.pdn.ac.lk/">Department of Computer Engineering</a>:
  Server Monitoring
</div>
<div class="nav">
  <a href="../../">Home</a>
  <a class="active" href="../server-storage-util/">Storage</a>
  <a href="../server-gpu-util/">GPU</a>
</div>
<div class="content">
  <h1>Server Storage Usage</h1>
  <hr>
  <p>This table shows the usage reports for folders that are larger than 10G on the CO Department server.</p>
  <div class="bookmarks">
    <h3>Contents</h3>
    <ol>
"""
        )

        for server in storage_servers.keys():
            f_out.write(f'      <li><a href="#{server}">{server}</a></li>\n')

        f_out.write(
            """
    </ol>
  </div>
"""
        )

        for server, details in storage_servers.items():
            print(f"Generating storage report for {server}...")
            log_file = logs_dir / f"{server}-storage.log"
            if not log_file.exists():
                f_out.write(f"<br><br><h3 id=\"{server}\">{server}</h3>\n")
                f_out.write("<p><em>No log file found for this server.</em></p>\n")
                continue

            with log_file.open("r", encoding="utf-8") as f_in:
                lines = f_in.readlines()

            read_on = lines[0].strip() if lines else "Unknown"
            f_out.write(
                f"<br><br><h3 id=\"{server}\">{server}</h3> Read on: {read_on}.\n"
            )

            doc_url = details.get("doc_url")
            if doc_url:
                f_out.write(f'[<a href="{doc_url}">Documentation</a>]')

            if server == "babbage":
                f_out.write(
                    "<p><span style=\"background: orange\">ORANGE = Alumni using more than 10GB</span></p>"
                )
                f_out.write(
                    "<p><span style=\"background: yellow\">YELLOW = Students using more than 50GB</span></p>"
                )

            f_out.write(
                """
<table border="1" style="border-collapse:collapse;">
<tr>
<th>Usage</th>
<th>Path</th>
<th>Owner</th>
</tr>
"""
            )

            for line in lines[1:]:
                parts = line.strip().split(maxsplit=1)
                if len(parts) != 2:
                    continue
                usage, folder = parts
                usage_gb = parse_usage_gb(usage)

                row_style = ""
                profile_url = None
                if server == "babbage":
                    color, profile_url = classify_babbage(
                        folder, usage_gb, student_batches
                    )
                    if color:
                        row_style = f' bgcolor="{color}"'

                f_out.write(f"<tr{row_style}><td>{usage}</td><td>{folder}</td>")

                if server == "babbage" and profile_url:
                    f_out.write(f"<td><a href=\"{profile_url}\">profile</a></td>")
                else:
                    f_out.write("<td></td>")

                f_out.write("</tr>\n")

            f_out.write("</table>\n<br><br>")

        f_out.write(
            """
  </div>
</div>
<hr>
<footer>
  <p>This page was last updated on {}.</p>
  <p>This webpage was vibecoded by <a href="https://people.ce.pdn.ac.lk/students/e14/158">E/14/Gihan</a> with GPT-5.2 Codex. Feel free to email him regarding any questions.</p>
  <p>The sourcecode is available <a href="https://github.com/cepdnaclk/servermonitoring">here</a>.</p>
</footer>
</body>
</html>
""".format(
                generated_at.strftime("%Y-%m-%d %H:%M:%S")
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate storage usage report HTML.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to server config JSON.",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=DEFAULT_LOGS_DIR,
        help="Directory containing *-storage.log files.",
    )
    parser.add_argument(
        "--batches",
        type=Path,
        default=DEFAULT_BATCHES,
        help="Path to batches config JSON.",
    )
    parser.add_argument(
        "--out-file",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output HTML file.",
    )
    args = parser.parse_args()

    storage_servers = load_storage_servers(args.config)
    student_batches = load_student_batches(args.batches)
    build_storage_report(args.logs_dir, args.out_file, storage_servers, student_batches)
    print(f"Storage report generated at {args.out_file}")


if __name__ == "__main__":
    main()
