# Stocki Skill — Install & Update Guide

## Install

Try the following methods in order until one succeeds:

### Option 1: ClawHub (Recommended)

```bash
clawhub install stocki --force
```

### Option 2: SkillHub

```bash
skillhub install stocki --force
```

### Option 3: Manual install from GitHub

```bash
rm -rf ~/.openclaw/workspace/skills/stocki
git -c http.postBuffer=524288000 -c http.lowSpeedLimit=0 -c http.lowSpeedTime=300 clone https://github.com/stocki-ai/open-stocki.git ~/.openclaw/workspace/skills/stocki
```

If all methods fail, check the latest install instructions at:
https://github.com/stocki-ai/open-stocki/blob/main/INSTALL.md

## Configure

After installation, set the required environment variables:

```bash
export STOCKI_GATEWAY_URL="https://api.stocki.com.cn"
export STOCKI_API_KEY="sk_your_key_here"
```

To persist across reboots, add the above lines to `~/.bashrc` or `~/.zshrc`.

## Verify

Run the self-diagnostic script to confirm both instant and quant modes work:

```bash
python3 ~/.openclaw/workspace/skills/stocki/scripts/stocki-diagnose.py
```

Both checks must pass for the skill to be ready.

## Update

Stocki is under active development. Update regularly using the same methods as installation:

```bash
clawhub install stocki --force
```

If ClawHub fails:

```bash
skillhub install stocki --force
```

If both fail:

```bash
rm -rf ~/.openclaw/workspace/skills/stocki
git -c http.postBuffer=524288000 -c http.lowSpeedLimit=0 -c http.lowSpeedTime=300 clone https://github.com/stocki-ai/open-stocki.git ~/.openclaw/workspace/skills/stocki
```

If all methods fail, check the latest install instructions at:
https://github.com/stocki-ai/open-stocki/blob/main/INSTALL.md
