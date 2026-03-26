# Stocki — AI Financial Analyst

Professional AI financial analyst powered by top-tier quantitative hedge fund data and analytical tools.

## Features

- **Instant Mode** — Quick financial Q&A: market prices, news, sector outlooks, company analysis
- **Task Mode** — Complex quantitative analysis: backtesting, strategy modeling, portfolio review
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
python3 scripts/stocki-instant.py "What's the outlook for US tech stocks?"
```

**Quant Analysis:**
```bash
python3 scripts/stocki-task.py create "Semiconductor Sector Analysis"
python3 scripts/stocki-run.py submit <task_id> "Backtest CSI 300 momentum strategy"
python3 scripts/stocki-run.py status <task_id> <run_id>
python3 scripts/stocki-report.py download <task_id> summary.md
```

## Scripts

| Script | Purpose |
|--------|---------|
| `stocki-instant.py` | Quick financial Q&A |
| `stocki-task.py` | Create, list, and view task history |
| `stocki-run.py` | Submit quant runs and check status |
| `stocki-report.py` | List and download analysis reports |
| `stocki-diagnose.py` | Self-diagnostic to verify installation |

## License

Proprietary. All rights reserved.
