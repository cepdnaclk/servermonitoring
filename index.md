---
layout: home
title: Server Monitoring Dashboard
---

## Welcome

Daily updated storage and GPU utilization reports for the Department of Computer Engineering servers.

### Quick Links

- [Storage Usage Report](/servermonitoring/storage/)
- [GPU Usage Report](/servermonitoring/gpu/)

### About

This dashboard provides automated monitoring of:
- **Storage utilization** across multiple servers
- **GPU metrics** including utilization and memory usage
- **Historical trends** for the last 90 days

Data is automatically collected, processed, and published daily via GitHub Actions.

---

{% if site.data.metadata %}
*Last updated: {{ site.data.metadata.generated_at | date: "%Y-%m-%d %H:%M" }}*
{% endif %}

**Maintained by**: [E/14/Gihan](https://people.ce.pdn.ac.lk/students/e14/158) and [E/15/Nuwan](https://nuwanjaliyagoda.com/contact/)

**Source Code**: [github.com/cepdnaclk/servermonitoring](https://github.com/cepdnaclk/servermonitoring)

---

*This webpage was **VibeCoded** with **ChatGPT 5.2** + **GitHub Copilot Agent***
