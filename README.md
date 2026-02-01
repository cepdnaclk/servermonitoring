# Server Monitoring Dashboard

Static dashboard for Department of Computer Engineering server utilization
(GPU and storage). Generated daily and published via GitHub Pages.

## Live Site

`https://cepdnaclk.github.io/servermonitoring/`

## Data Source

Base index (logs are under per-server folders):
`https://tesla.ce.pdn.ac.lk/servermonitoring/`

## How It Works

- Logs are synced from the server into `data/logs/`.
- Storage report HTML is generated at `docs/reports/server-storage-util/index.html`.
- GPU plots and index are generated at `docs/reports/server-gpu-util/`.
- GitHub Actions runs daily and pushes `docs/` to GitHub Pages.

## Project Structure

- `scripts/` → report generation and log sync
- `config/servers.json` → server list and storage doc links
- `config/gpu-info.json` → GPU IDs and memory limits
- `config/batches.json` → student batches (for alumni vs student tagging)
- `data/logs/` → downloaded logs (ignored by git)
- `docs/` → published site output

## Local Development

### Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Download Logs

```
python scripts/sync_logs.py
```

Custom base URL (must contain per-server folders like `kepler/`):

```
python scripts/sync_logs.py --base-url https://tesla.ce.pdn.ac.lk/servermonitoring/logging/
```

### Build the Dashboard

Build using local logs:

```
python scripts/build_dashboard.py
```

Build and download logs in one step:

```
python scripts/build_dashboard.py --download-logs
```

## Notes

- Storage: `babbage` highlights alumni (>10GB, orange) and students (>50GB, yellow)
  based on `config/batches.json`.
- GPU plots show daily mean utilization and memory for the last 90 days.

## Contact

- **E/14/Gihan**: https://people.ce.pdn.ac.lk/students/e14/158
- **E/15/Nuwan**: https://nuwanjaliyagoda.com/contact/