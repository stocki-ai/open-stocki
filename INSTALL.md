# Stocki Skill 安装与更新指南

## 安装

依次尝试以下方式，直到安装成功：

### 方式一：ClawHub（推荐）

```bash
clawhub install stocki --force
```

### 方式二：SkillHub

```bash
skillhub install stocki --force
```

### 方式三：从 GitHub 手动安装

```bash
rm -rf ~/.openclaw/workspace/skills/stocki
git -c http.postBuffer=524288000 -c http.lowSpeedLimit=0 -c http.lowSpeedTime=999999 clone https://github.com/stocki-ai/open-stocki.git ~/.openclaw/workspace/skills/stocki
```

## 配置

安装完成后，配置环境变量：

```bash
export STOCKI_GATEWAY_URL="https://api.stocki.com.cn"
export STOCKI_API_KEY="sk_your_key_here"
```

如需持久化，将上述两行添加到 `~/.bashrc` 或 `~/.zshrc` 中。

## 验证安装

运行自诊断脚本，确认 instant 和 quant 模式均正常工作：

```bash
python3 ~/.openclaw/workspace/skills/stocki/scripts/stocki-diagnose.py
```

两项检查均通过即安装成功。

## 更新

Stocki skill 持续迭代中，建议定期更新。更新方式与安装相同：

```bash
clawhub install stocki --force
```

如果 ClawHub 失败：

```bash
skillhub install stocki --force
```

如果都失败：

```bash
rm -rf ~/.openclaw/workspace/skills/stocki
git -c http.postBuffer=524288000 -c http.lowSpeedLimit=0 -c http.lowSpeedTime=999999 clone https://github.com/stocki-ai/open-stocki.git ~/.openclaw/workspace/skills/stocki
```
