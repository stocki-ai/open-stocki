# Stocki — AI Financial Analyst

Professional AI financial analyst powered by institutional-grade financial data and quantitative analysis tools.

## Features

- **Instant Mode** — Quick financial Q&A: market prices, news, sector outlooks, company analysis
- **Quant Mode** — Complex quantitative analysis: backtesting, strategy modeling, portfolio review
- **Scheduled Monitoring** — Periodic market updates via cron-triggered tasks
- **Zero Dependencies** — Python stdlib only, no pip install needed

## Install

```bash
clawhub install stocki --force
```

See [INSTALL.md](INSTALL.md) for all installation methods and configuration.

## Quick Start

**Instant Q&A:**
```bash
stocki instant "What's the outlook for US tech stocks?"
```

**Quant Analysis:**
```bash
stocki quant "Backtest CSI 300 momentum strategy"
stocki status <task_id>
stocki files <task_id>
stocki download <task_id> runs/run_001/report.md
```

## CLI Commands

| Command | Purpose |
|---------|---------|
| `stocki instant` | Quick financial Q&A |
| `stocki quant` | Submit quantitative analysis |
| `stocki tasks` | List all quant tasks |
| `stocki status` | Show task details and run statuses |
| `stocki files` | List result files for a task |
| `stocki download` | Download report or image |
| `stocki diagnose` | Self-diagnostic to verify installation |

## License

Proprietary. All rights reserved.
