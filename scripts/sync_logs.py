import argparse
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

from tqdm import tqdm


def fetch_listing(url: str) -> str | None:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "servermonitoring-bot"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def parse_links(
    html: str,
    base_url: str,
    suffixes: tuple[str, ...],
    contains: tuple[str, ...] = (),
) -> list[str]:
    links = []
    for href in re.findall(r'href=["\']([^"\']+)["\']', html):
        if href.startswith("?") or href.startswith("../"):
            continue
        if not href.lower().endswith(suffixes):
            continue
        if contains and not any(token in href for token in contains):
            continue
        links.append(urljoin(base_url, href))
    return sorted(set(links))


def parse_directories(html: str, base_url: str) -> list[str]:
    dirs = []
    for href in re.findall(r'href=["\']([^"\']+/)["\']', html):
        if href.startswith("?") or href.startswith("../"):
            continue
        dirs.append(urljoin(base_url, href))
    return sorted(set(dirs))


def extract_date(url: str) -> datetime | None:
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", url)
    if not match:
        return None
    try:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def download_files(
    urls: list[str],
    dest_dir: Path,
    since: datetime | None,
    workers: int,
    label: str,
    days: int | None,
) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    to_download = []
    for url in urls:
        if since:
            file_date = extract_date(url)
            if file_date and file_date < since:
                continue
        to_download.append(url)

    def _download(url: str) -> bool:
        filename = url.split("/")[-1]
        dest_path = dest_dir / filename
        try:
            urllib.request.urlretrieve(url, dest_path)
            return True
        except Exception:
            return False

    downloaded = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_download, url) for url in to_download]
        desc = f"{label} ({days} days)" if days is not None else label
        for future in tqdm(as_completed(futures), total=len(futures), desc=desc, unit="file"):
            if future.result():
                downloaded += 1
    return downloaded


def sync_logs(
    base_url: str, storage_dir: Path, gpu_dir: Path, days: int, workers: int
) -> None:
    base_html = fetch_listing(base_url)
    if not base_html:
        return

    server_dirs = parse_directories(base_html, base_url)
    since = datetime.now() - timedelta(days=days)
    for server_dir in server_dirs:
        server_html = fetch_listing(server_dir)
        if not server_html:
            continue
        server_name = server_dir.rstrip("/").split("/")[-1]
        print(f"Server: {server_name}")

        storage_links = parse_links(server_html, server_dir, (".log",), ("-storage.log",))
        gpu_links = parse_links(server_html, server_dir, (".log",), ("-gpu-",))

        if storage_links:
            print("  Storage logs")
            download_files(storage_links, storage_dir, since, workers, "storage", None)
        if gpu_links:
            print(f"  GPU logs (last {days} days)")
            download_files(gpu_links, gpu_dir, since, workers, "gpu", days)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download storage and GPU logs.")
    parser.add_argument(
        "--base-url",
        default="https://tesla.ce.pdn.ac.lk/servermonitoring/logging/",
        help="Base URL that contains per-server log directories.",
    )
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=Path("data/logs/storage"),
        help="Output directory for storage logs.",
    )
    parser.add_argument(
        "--gpu-dir",
        type=Path,
        default=Path("data/logs/gpu"),
        help="Output directory for GPU logs.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days of logs to download.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Number of concurrent download threads.",
    )
    args = parser.parse_args()

    sync_logs(args.base_url, args.storage_dir, args.gpu_dir, args.days, args.workers)
    print("Log sync completed.")


if __name__ == "__main__":
    main()
