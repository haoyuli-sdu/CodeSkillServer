# Linux 快速使用

在仓库根目录执行。命令使用 `python3`；如果服务器的 Python 命令名是 `python`，可以等价替换。

## 1. 环境和身份

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
```

核心脚本不需要第三方包。

设置一个能联系到你的 User-Agent，不要把 Token 写进脚本：

```bash
export SKILL_CRAWLER_USER_AGENT="YourLabSkillResearch/0.1 (contact=you@example.org)"
export GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
```

## 2. 检查来源

```bash
python3 scripts/skill_crawler.py probe
python3 scripts/targeted_codegen_crawler.py probe
```

先进行小规模试跑；如果来源返回 429，等待配额重置或使用官方 API Key，不要提高并发绕过限制。

## 3. 定向采集

```bash
mkdir -p data/runs results logs datasets/skills

python3 scripts/targeted_codegen_crawler.py --delay 1 discover \
  --source github \
  --db data/runs/github.db \
  --tiers core \
  --queries-per-group 3 \
  --per-query 30 \
  2>&1 | tee logs/github-discover.log
```

其他来源可以复制该命令，替换 `--source` 和数据库名称。SkillsMP 有每日请求配额，建议先使用较小的 `--max-queries`。

## 4. 合并、门控、解析

```bash
python3 scripts/merge_targeted_dbs.py \
  --out data/runs/targeted_master.db \
  data/runs/github.db \
  data/runs/skills_sh.db \
  data/runs/skillsmp.db

python3 scripts/targeted_codegen_crawler.py gate \
  --db data/runs/targeted_master.db \
  --out results/targeted_gate.csv

python3 scripts/targeted_codegen_crawler.py --delay 1 resolve \
  --db data/runs/targeted_master.db \
  --labels auto_resolve,review_or_resolve \
  2>&1 | tee logs/resolve.log
```

## 5. 筛选、审计和导出

```bash
python3 scripts/direct_codegen_filter_v2.py \
  --db data/runs/targeted_master.db \
  --out-dir results/direct_codegen

python3 scripts/audit_skill_dataset.py \
  --db data/runs/targeted_master.db \
  --out-dir results/audit

python3 scripts/export_skills_as_folders.py \
  --db data/runs/targeted_master.db \
  --out-dir datasets/skills \
  --labels confirmed_direct
```

最终 Skill 数据集位于 `datasets/skills/`，数据库位于 `data/runs/`。

## 6. 测试和后台运行

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
nohup bash -c 'python3 scripts/targeted_codegen_crawler.py --delay 1 discover --source github --db data/runs/github.db --tiers core --queries-per-group 3 --per-query 30' > logs/github.log 2>&1 &
```

长时间运行前应先用小参数验证 Token、来源政策和磁盘空间。不要用多个进程同时写同一个 SQLite 数据库；不同来源使用不同数据库，采集完成后再合并。
