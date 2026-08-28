# Server Monitoring Dashboard

Static dashboard for Department of Computer Engineering server utilization (GPU and storage). Generated daily and published via GitHub Pages.

## 🌐 Live Site

**[https://cepdnaclk.github.io/servermonitoring/](https://cepdnaclk.github.io/servermonitoring/)**

## 📋 Overview

This project provides automated monitoring and visualization of:
- **Storage utilization** across multiple department servers
- **GPU metrics** including utilization and memory usage over time
- **Historical trends** for the last 90 days

The system uses:
- **Python** for data collection and transformation
- **Jekyll** (minima theme) for static site generation
- **GitHub Actions** for automated daily updates

## 🏗️ Architecture

### Data Pipeline

```
External Logs → Python Scripts → JSON Data → Jekyll → Static Site
```

1. **Data Collection**: `sync_logs.py` downloads logs from the monitoring server
2. **Data Transformation**: `build_data.py` processes logs into Jekyll-friendly JSON
3. **Site Generation**: Jekyll renders templates using data from `_data/*.json`
4. **Publishing**: GitHub Actions deploys to GitHub Pages

### Directory Structure

```
├── _config.yml              # Jekyll configuration
├── _data/                   # Generated JSON data (consumed by Jekyll)
│   ├── storage.json         # Storage usage data
│   ├── gpu.json             # GPU metrics data
│   └── metadata.json        # Site metadata
├── _includes/               # Jekyll template fragments
├── config/                  # Configuration files
│   ├── servers.json         # Server list and documentation links
│   ├── gpu-info.json        # GPU specifications
│   └── batches.json         # Student batch identifiers
├── src/servermonitoring/    # Python data processing modules
│   ├── config.py            # Configuration loading utilities
│   ├── storage.py           # Storage data processing
│   └── gpu.py               # GPU data processing
├── scripts/                 # Executable scripts
│   ├── build_data.py        # Main data generation entrypoint
│   └── sync_logs.py         # Log synchronization
├── tests/                   # Python unit tests
├── index.md                 # Homepage
├── storage.md               # Storage report page
├── gpu.md                   # GPU report page
└── Makefile                 # Build automation
```

## 🚀 Local Development

### Prerequisites

- **Python 3.11+**
- **Ruby 3.x** and **Bundler** (for Jekyll)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cepdnaclk/servermonitoring.git
   cd servermonitoring
   ```

2. **Install Python dependencies**:
   ```bash
   make setup
   ```

3. **Install Jekyll dependencies** (requires Ruby):
   ```bash
   gem install bundler
   bundle install
   ```

### Generate Data

```bash
make data
```

### Download Logs

```bash
python scripts/sync_logs.py
```

### Build and Serve Site

```bash
make site    # Build
make serve   # Serve locally at http://localhost:4000/servermonitoring/
```

## 🧪 Testing

```bash
make test    # Run tests with coverage
make lint    # Run linting checks
make format  # Auto-format code
```

## 🤖 CI/CD

- **Testing**: Automatic PR checks (`.github/workflows/test.yml`)
- **Deployment**: Daily updates (`.github/workflows/update-dashboard.yml`)

## 📝 Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make setup` | Install dependencies |
| `make data` | Generate JSON data |
| `make test` | Run tests |
| `make lint` | Check code quality |
| `make site` | Build Jekyll site |
| `make serve` | Serve locally |
| `make clean` | Remove artifacts |

## 👥 Contributors

- **E/14/Gihan**: [Profile](https://people.ce.pdn.ac.lk/students/e14/158)
- **E/15/Nuwan**: [Website](https://nuwanjaliyagoda.com/contact/)

## 🔗 Links

- **Live Site**: [cepdnaclk.github.io/servermonitoring](https://cepdnaclk.github.io/servermonitoring/)
- **Repository**: [github.com/cepdnaclk/servermonitoring](https://github.com/cepdnaclk/servermonitoring)
