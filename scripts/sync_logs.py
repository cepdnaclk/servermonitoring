import argparse
import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


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


def download_files(urls: list[str], dest_dir: Path) -> int:
    dest_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for url in urls:
        filename = url.split("/")[-1]
        dest_path = dest_dir / filename
        try:
            urllib.request.urlretrieve(url, dest_path)
            downloaded += 1
        except Exception:
            continue
    return downloaded


def sync_logs(base_url: str, storage_dir: Path, gpu_dir: Path) -> None:
    base_html = fetch_listing(base_url)
    if not base_html:
        return

    server_dirs = parse_directories(base_html, base_url)
    for server_dir in server_dirs:
        server_html = fetch_listing(server_dir)
        if not server_html:
            continue

        storage_links = parse_links(server_html, server_dir, (".log",), ("-storage.log",))
        gpu_links = parse_links(server_html, server_dir, (".log",), ("-gpu-",))

        if storage_links:
            download_files(storage_links, storage_dir)
        if gpu_links:
            download_files(gpu_links, gpu_dir)


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
    args = parser.parse_args()

    sync_logs(args.base_url, args.storage_dir, args.gpu_dir)
    print("Log sync completed.")


if __name__ == "__main__":
    main()
