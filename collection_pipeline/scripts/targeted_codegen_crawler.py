#!/usr/bin/env python3
"""Targeted, high-recall discovery for direct code-generation Agent Skills.

The script separates cheap search/metadata discovery from expensive SKILL.md
resolution. It never executes downloaded Skill code.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse

try:
    from . import skill_crawler as legacy
except ImportError:  # Supports direct execution: python scripts/targeted_codegen_crawler.py
    import skill_crawler as legacy

VERSION = "targeted-direct-codegen-crawler-v1.2"
GATE_VERSION = "direct-codegen-metadata-gate-v2.0"
PROFILE_DEFAULT = Path(__file__).with_name("direct_codegen_queries.json")
API_MAX_BYTES = 20_000_000

class DailyQuotaExceeded(legacy.CrawlError):
    """A source-wide daily API quota is exhausted; remaining queries must stop."""
    pass

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

SOURCE_SPECS = {
    "github": {
        "kind": "github_code_search",
        "enabled": True,
        "endpoint": "https://api.github.com/search/code",
        "auth_env": "GITHUB_TOKEN",
        "note": "Official GitHub Code Search; exact SKILL.md paths are resolved through the GitHub API.",
    },
    "skills_sh": {
        "kind": "official_json_search",
        "enabled": True,
        "endpoint": "https://skills.sh/api/search",
        "auth_env": "SKILLS_SH_TOKEN",
        "note": "Official search API. Token is optional only when the endpoint permits anonymous access.",
    },
    "skillsmp": {
        "kind": "official_json_search",
        "enabled": True,
        "endpoint": "https://skillsmp.com/api/v1/skills/search",
        "auth_env": "SKILLSMP_API_KEY",
        "note": "Official SkillsMP search API. API key may be required.",
    },
    "clawhub": {
        "kind": "official_json_search",
        "enabled": True,
        "endpoint": "https://clawhub.ai/api/v1/search",
        "auth_env": "CLAWHUB_TOKEN",
        "note": "Official ClawHub search. Resolution reads SKILL.md only; packages are not installed or executed.",
    },
    "smithery": {
        "kind": "official_json_search",
        "enabled": True,
        "endpoint": "https://registry.smithery.ai/skills",
        "auth_env": "SMITHERY_API_KEY",
        "note": "Official Smithery Skills listing/search; results are restricted to Skill resources.",
    },
    "claude_plugins": {
        "kind": "official_json_search",
        "enabled": True,
        "endpoint": "https://claude-plugins.dev/api/skills",
        "auth_env": "CLAUDE_PLUGINS_TOKEN",
        "note": "Official registry search when available; use --endpoint to override if the registry changes.",
    },
    "tessl": {
        "kind": "official_cli",
        "enabled": False,
        "endpoint": "tessl search",
        "auth_env": "",
        "note": "Uses the authenticated official Tessl CLI with --type skills; website scraping is not used.",
    },
}

TARGETED_SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS discovery_runs(
  discovery_run_id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,
  query_id TEXT NOT NULL,
  query_text TEXT NOT NULL,
  query_group TEXT,
  query_tier TEXT,
  profile_version TEXT,
  requested_limit INTEGER,
  started_at TEXT,
  finished_at TEXT,
  status TEXT,
  returned_count INTEGER DEFAULT 0,
  stored_count INTEGER DEFAULT 0,
  error TEXT
);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_lookup
  ON discovery_runs(source, query_id, profile_version, status);
CREATE TABLE IF NOT EXISTS discovery_hits(
  discovery_hit_id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,
  external_id TEXT NOT NULL,
  query_id TEXT NOT NULL,
  query_text TEXT NOT NULL,
  query_group TEXT,
  query_tier TEXT,
  rank INTEGER,
  native_score REAL,
  route TEXT DEFAULT 'targeted',
  hit_metadata_json TEXT,
  discovered_at TEXT,
  UNIQUE(source, external_id, query_id, route)
);
CREATE INDEX IF NOT EXISTS idx_discovery_hits_item
  ON discovery_hits(source, external_id);
CREATE TABLE IF NOT EXISTS candidate_queue(
  source TEXT NOT NULL,
  external_id TEXT NOT NULL,
  gate_version TEXT NOT NULL,
  gate_label TEXT NOT NULL,
  gate_score INTEGER NOT NULL,
  gate_evidence_json TEXT,
  best_rank INTEGER,
  query_count INTEGER,
  status TEXT,
  updated_at TEXT,
  PRIMARY KEY(source, external_id, gate_version)
);
CREATE TABLE IF NOT EXISTS fetch_receipts(
  receipt_id INTEGER PRIMARY KEY,
  source TEXT,
  external_id TEXT,
  resolver TEXT,
  target TEXT,
  status TEXT,
  content_sha256 TEXT,
  detail_json TEXT,
  fetched_at TEXT
);
"""

DIRECT_PHRASES = [
    r"\bcode\s*gen(?:eration|erator)?\b", r"\bgenerate(?:s|d|ing)?\s+(?:production\s+|runnable\s+|executable\s+|source\s+)?code\b",
    r"\bwrite(?:s|ten|ing)?\s+(?:source\s+)?code\b", r"\bcode synthesis\b", r"\bprogram synthesis\b",
    r"\b(?:specification|requirements?|natural language|prompt|text)\s*(?:to|into|2)\s*code\b",
    r"\bdocstring\s*(?:to|into|2)\s*code\b", r"\bfunction[- ]level code generation\b",
    r"\bsource generator\b", r"\bclient generator\b", r"\bserver stub generation\b",
    r"\bscaffold(?:ing)?\s+(?:an?\s+)?(?:application|project|feature|service|component|module|code)\b",
    r"\bboilerplate generator\b", r"\bcomplete (?:the )?(?:implementation|function|method|code)\b",
    r"(?:代码生成|生成源代码|生成代码|编写代码|写代码|自然语言生成代码|根据(?:需求|规格)生成代码|生成可运行代码|生成完整实现|项目脚手架)",
]
ACTION_WORDS = [
    "generate", "generates", "generated", "generating", "implement", "implements", "implementation", "write", "writes", "create", "creates",
    "build", "builds", "scaffold", "scaffolds", "synthesize", "complete", "fill", "produce", "convert", "translate", "migrate", "port", "rewrite",
    "生成", "实现", "编写", "创建", "构建", "搭建", "脚手架", "补全", "转换", "迁移", "翻译", "移植", "重写",
]
ARTIFACT_WORDS = [
    "code", "source code", "function", "method", "class", "module", "algorithm", "data structure", "implementation", "application", "app", "project",
    "component", "page", "frontend", "backend", "api", "endpoint", "handler", "resolver", "middleware", "service", "controller", "repository", "model",
    "cli", "command line", "sdk", "api client", "plugin", "extension", "mcp server", "crud", "test", "test case", "fixture", "mock", "stub",
    "sql", "query", "schema", "migration", "orm", "terraform", "dockerfile", "kubernetes", "manifest", "workflow", "pipeline", "configuration", "config",
    "代码", "源代码", "函数", "方法", "类", "模块", "算法", "数据结构", "实现", "应用", "项目", "组件", "页面", "前端", "后端", "接口",
    "处理器", "中间件", "服务", "控制器", "模型", "客户端", "插件", "扩展", "测试", "用例", "SQL", "查询", "模式", "迁移", "配置",
]
SOFTWARE_DOMAIN = re.compile(
    r"\b(?:python|javascript|typescript|java|golang|go|rust|c\+\+|c#|kotlin|swift|php|ruby|scala|react|vue|angular|next\.?js|fastapi|django|flask|spring|asp\.?net|laravel|rails|nestjs|express|software|developer|programming|codebase|repository|compiler|parser|openapi|protobuf|graphql|database|devops)\b|(?:编程|软件开发|代码库|开发者|数据库|前端|后端)",
    re.I,
)
SUPPORT_ONLY = re.compile(
    r"\b(?:code review|review code|debug(?:ging)?|bug diagnosis|root cause analysis|refactor(?:ing)? advice|coding standards?|best practices?|architecture planning|documentation|explain code|code explanation|static analysis|linting)\b|(?:代码审查|调试|问题诊断|重构建议|编码规范|最佳实践|架构规划|代码解释|静态分析)",
    re.I,
)
NON_CODE = re.compile(
    r"\b(?:image generation|video generation|music generation|audio generation|presentation generation|slide deck|marketing copy|social media content|blog writing|seo content|resume writing|translation only|diagram generation|generate(?:s|d|ing)? diagrams?|mermaid diagrams?|draw\\.io|xmind|storyboards?|screenplays?|video projects?|scientific figures?|api documentation|google (?:docs|slides|forms)|formatted reports?)\b|(?:图片生成|视频生成|音乐生成|音频生成|幻灯片|演示文稿|营销文案|社交媒体文案|博客写作|简历写作|图表生成|接口文档|API文档|思维导图|分镜|剧本|短剧|视频项目|科学图表|测试文档)",
    re.I,
)
NEGATION = re.compile(
    r"\b(?:not|never|without|does not|do not)\b[^\n,;:.!?]{0,50}\b(?:generate(?:\s+[^,;:.!?。；，！？\n]{0,35})?\s+(?:code|schemas?|sql|tests?|clients?|sdks?|apis?|functions?|classes?|modules?)|code generation|write code|implementation)\b|(?:不生成|不要生成|不用于生成|无需生成|禁止生成)(?:代码|程序)",
    re.I,
)


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def compact_space(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def flatten_text(value, depth=0):
    if depth > 4 or value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten_text(x, depth + 1) for x in value[:80])
    if isinstance(value, dict):
        preferred = []
        for key, val in value.items():
            if str(key).lower() in {"title", "name", "description", "summary", "tags", "tag", "category", "categories", "occupation", "language", "topics", "keywords", "type"}:
                preferred.append(flatten_text(val, depth + 1))
        return " ".join(preferred)
    return ""


def first_value(item, *paths):
    for path in paths:
        cur = item
        ok = True
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                ok = False
                break
            cur = cur[part]
        if ok and cur not in (None, "", [], {}):
            return cur
    return ""


def list_items(payload):
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("results", "skills", "items", "entries", "hits", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
    for key in ("data", "result", "response"):
        value = payload.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
        if isinstance(value, dict):
            nested = list_items(value)
            if nested:
                return nested
    return []


def normalize_repo(value):
    if isinstance(value, dict):
        value = first_value(value, "url", "html_url", "githubUrl", "repositoryUrl", "full_name", "nameWithOwner")
    value = compact_space(value)
    if not value:
        return ""
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        return "https://github.com/" + value
    if value.startswith("git@github.com:"):
        return "https://github.com/" + value.split(":", 1)[1].removesuffix(".git")
    if "github.com/" in value:
        repo, _, _ = legacy.split_github(value)
        return repo or value
    return ""


def candidate_from_item(source, item, rank, query_id, query_text):
    title = compact_space(first_value(item, "title", "name", "displayName", "skillName", "qualifiedName", "package.name"))
    description = compact_space(first_value(item, "description", "summary", "shortDescription", "tagline", "package.description"))
    slug = compact_space(first_value(item, "slug", "id", "skillId", "scopedName", "qualifiedName", "name"))
    page = compact_space(first_value(item, "url", "pageUrl", "canonicalUrl", "html_url", "homepage", "links.web", "links.homepage"))
    repo = normalize_repo(first_value(item, "githubUrl", "repo_url", "repoUrl", "repositoryUrl", "sourceUrl", "repository", "source", "links.github", "package.repository"))
    path = compact_space(first_value(item, "path", "skillPath", "filePath", "source.path"))
    raw = compact_space(first_value(item, "rawUrl", "raw_url", "downloadUrl", "contentUrl", "apiUrl"))
    if source == "skills_sh" and not repo:
        source_name = compact_space(first_value(item, "source", "repository", "repo"))
        repo = normalize_repo(source_name)
    if not page:
        page = {
            "skills_sh": "https://skills.sh/" + slug.lstrip("/"),
            "skillsmp": "https://skillsmp.com/skills/" + slug,
            "clawhub": "https://clawhub.ai/skills/" + slug,
            "smithery": "https://smithery.ai/skills/" + slug,
            "claude_plugins": "https://claude-plugins.dev/skills/" + slug,
        }.get(source, "")
    external = compact_space(first_value(item, "id", "skillId", "slug", "scopedName", "qualifiedName", "name"))
    if not external:
        external = hashlib.sha256((source + "\n" + page + "\n" + title + "\n" + repo + "\n" + path).encode("utf-8")).hexdigest()
    metadata = dict(item)
    metadata.update({"targeted_query_id": query_id, "targeted_query": query_text, "targeted_rank": rank})
    return legacy.Candidate(source, external, page, title, description, repo, path, raw, slug, metadata)


def auth_headers(source):
    headers = {}
    env_name = SOURCE_SPECS[source].get("auth_env")
    token = os.getenv(env_name, "") if env_name else ""
    if not token:
        return headers
    headers["Authorization"] = "Bearer " + token
    return headers


def api_get_json(http, url, headers=None, retries=4):
    headers = dict(headers or {})
    headers.update({"User-Agent": http.ua, "Accept": "application/json", "Accept-Encoding": "gzip"})
    parsed = urlparse(url)
    last = None
    for attempt in range(retries):
        try:
            http.wait(parsed.netloc)
            request = urllib.request.Request(legacy.iri_to_uri(url), headers=headers)
            with urllib.request.urlopen(request, timeout=http.timeout) as response:
                raw = response.read(API_MAX_BYTES + 1)
                if len(raw) > API_MAX_BYTES:
                    raise legacy.CrawlError("API response too large: " + url)
                if response.headers.get("Content-Encoding", "").lower() == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                return json.loads(raw.decode("utf-8", "replace")), dict(response.headers)
        except urllib.error.HTTPError as exc:
            body = exc.read(2000).decode("utf-8", "replace")
            last = RuntimeError(f"HTTP {exc.code}: {body[:500]}")
            if exc.code == 429 and "DAILY_QUOTA_EXCEEDED" in body:
                raise DailyQuotaExceeded(f"Daily API quota exhausted for {url}. {body[:500]}") from exc
            if exc.code in {401, 403}:
                env_name = next((spec.get("auth_env") for spec in SOURCE_SPECS.values() if spec.get("endpoint") and url.startswith(spec.get("endpoint"))), "")
                raise legacy.CrawlError(f"Authentication/permission failed for {url}. Check {env_name or 'the source credentials'}. HTTP {exc.code}") from exc
            if exc.code not in {429, 500, 502, 503, 504}:
                raise legacy.CrawlError(f"API HTTP {exc.code}: {url}: {body[:500]}") from exc
            retry_after = exc.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else min(60, 2 ** attempt)
            time.sleep(max(1, wait))
        except Exception as exc:
            last = exc
            time.sleep(min(30, 2 ** attempt))
    raise legacy.CrawlError(f"API request failed: {url}: {last}")


def load_profile(path, tiers, groups, max_queries=0, queries_per_group=0):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    tier_set = {x.strip() for x in tiers.split(",") if x.strip()}
    group_set = {x.strip() for x in groups.split(",") if x.strip()}
    queries = []
    for group in data.get("groups", []):
        if tier_set and group.get("tier") not in tier_set:
            continue
        if group_set and group.get("id") not in group_set:
            continue
        group_queries = group.get("queries", [])[:queries_per_group or None]
        for index, text in enumerate(group_queries, 1):
            qid = f"{group['id']}:{index:03d}"
            queries.append({"id": qid, "text": compact_space(text), "group": group["id"], "tier": group.get("tier", "extended")})
    seen = set()
    unique = []
    for q in queries:
        key = q["text"].casefold()
        if key not in seen:
            seen.add(key)
            unique.append(q)
    if max_queries:
        unique = unique[:max_queries]
    return data, unique


class TargetedStore:
    def __init__(self, path):
        self.base = legacy.Store(path)
        self.db = self.base.db
        self.db.executescript(TARGETED_SCHEMA)
        self.db.commit()

    def search_completed(self, source, query_id, profile_version, requested_limit=0):
        return self.db.execute(
            "SELECT 1 FROM discovery_runs WHERE source=? AND query_id=? AND profile_version=? AND status='completed' AND requested_limit>=? LIMIT 1",
            (source, query_id, profile_version, requested_limit),
        ).fetchone() is not None

    def start_search(self, source, query, profile_version, limit):
        cur = self.db.execute(
            "INSERT INTO discovery_runs(source,query_id,query_text,query_group,query_tier,profile_version,requested_limit,started_at,status) VALUES(?,?,?,?,?,?,?,?,?)",
            (source, query["id"], query["text"], query["group"], query["tier"], profile_version, limit, utcnow(), "running"),
        )
        self.db.commit()
        return cur.lastrowid

    def finish_search(self, run_id, returned, stored, error=""):
        status = "failed" if error else "completed"
        self.db.execute(
            "UPDATE discovery_runs SET finished_at=?,status=?,returned_count=?,stored_count=?,error=? WHERE discovery_run_id=?",
            (utcnow(), status, returned, stored, error, run_id),
        )
        self.db.commit()

    def save_hit(self, candidate, query, rank, native_score=None, route="targeted"):
        self.base.save(candidate, "")
        self.db.execute(
            "INSERT INTO discovery_hits(source,external_id,query_id,query_text,query_group,query_tier,rank,native_score,route,hit_metadata_json,discovered_at) VALUES(?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(source,external_id,query_id,route) DO UPDATE SET rank=MIN(discovery_hits.rank,excluded.rank),native_score=COALESCE(excluded.native_score,discovery_hits.native_score),hit_metadata_json=excluded.hit_metadata_json,discovered_at=excluded.discovered_at",
            (candidate.source, candidate.external_id, query["id"], query["text"], query["group"], query["tier"], rank, native_score, route, json.dumps(candidate.metadata, ensure_ascii=False), utcnow()),
        )
        self.db.commit()


def github_query_expression(text):
    clean = compact_space(text.replace('"', ' '))
    if re.search(r"[\u3400-\u9fff]", clean):
        return f'filename:SKILL.md "{clean}"'
    words = re.findall(r"[A-Za-z0-9+#.-]+", clean.lower())
    if len(words) <= 4:
        return f'filename:SKILL.md "{clean}"'
    action_aliases = ["generate","implement","write","create","build","scaffold","synthesize","convert","translate","migrate","port","rewrite","complete"]
    action = next((a for a in action_aliases if any(w.startswith(a) for w in words)), "")
    artifact_candidates = sorted([x for x in ARTIFACT_WORDS if x.isascii() and x in clean.lower()], key=len, reverse=True)
    artifact = artifact_candidates[0] if artifact_candidates else ("code" if "code" in words else "")
    anchors = []
    if action: anchors.append(action)
    if artifact: anchors.append(f'"{artifact}"' if " " in artifact else artifact)
    if len(anchors) < 2:
        stop = {"a","an","the","from","to","into","and","or","with","for","of","as","new","complete","production","ready"}
        anchors.extend(w for w in words if w not in stop and w not in anchors[:1])
    return "filename:SKILL.md " + " ".join(anchors[:4])

def discover_github(http, query, limit):
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise legacy.CrawlError("GITHUB_TOKEN is required for targeted GitHub discovery")
    count = 0
    queue = [(0, 384000)]
    while queue and count < limit:
        lo, hi = queue.pop(0)
        expression = github_query_expression(query["text"]) + f" size:{lo}..{hi}"
        base = SOURCE_SPECS["github"]["endpoint"] + "?" + urlencode({"q": expression, "per_page": 100})
        first = legacy.github_request(http, base, True)
        total = int(first.get("total_count", 0))
        if legacy.should_split_code_search(total, lo, hi):
            mid = (lo + hi) // 2
            queue.extend([(lo, mid), (mid + 1, hi)])
            continue
        max_pages = min(legacy.CODE_SEARCH_MAX_PAGES, (min(total, limit - count) + 99) // 100 or 1)
        for page in range(1, max_pages + 1):
            payload = first if page == 1 else legacy.github_request(http, base + "&page=" + str(page), True)
            items = payload.get("items", [])
            if not items:
                break
            for item in items:
                repo = item.get("repository") or {}
                full_name = str(repo.get("full_name") or "")
                path = str(item.get("path") or "")
                external = f"github:{full_name.lower()}:{path.lower()}"
                candidate = legacy.Candidate(
                    "github", external, str(item.get("html_url") or ""), full_name, "", str(repo.get("html_url") or ("https://github.com/" + full_name if full_name else "")),
                    path, str(item.get("url") or ""), Path(path).parent.name,
                    {"sha": item.get("sha"), "repository": repo, "commit_specific_html_url": item.get("html_url"), "targeted_query_id": query["id"], "targeted_query": query["text"]},
                )
                count += 1
                yield candidate, count, item.get("score")
                if count >= limit:
                    return
            if len(items) < 100:
                break


def source_url(source, query_text, limit, endpoint="", page=1):
    endpoint = endpoint or os.getenv("TARGETED_" + source.upper() + "_ENDPOINT", "") or SOURCE_SPECS[source]["endpoint"]
    if source == "skills_sh":
        params = {"q": query_text, "limit": min(limit, 200)}
    elif source == "skillsmp":
        params = {"q": query_text, "limit": min(limit, 50), "page": page, "occupation": "software-developers"}
    elif source == "clawhub":
        params = {"q": query_text, "limit": min(limit, 100)}
    elif source == "smithery":
        params = {"query": query_text, "pageSize": min(limit, 100), "page": page}
    elif source == "claude_plugins":
        params = {"q": query_text, "limit": min(limit, 100), "offset": 0}
    else:
        params = {"q": query_text, "limit": limit}
    return endpoint + ("&" if "?" in endpoint else "?") + urlencode(params)


def discover_json_source(http, source, query, limit, endpoint=""):
    # SkillsMP documents a maximum page size of 50. Paginate so --per-query 100
    # means two requests rather than an invalid/ambiguous limit=100 request.
    page = 1
    emitted = 0
    seen = set()
    while emitted < limit:
        request_limit = min(50, limit - emitted) if source == "skillsmp" else limit
        url = source_url(source, query["text"], request_limit, endpoint, page)
        payload, response_headers = api_get_json(http, url, auth_headers(source))
        items = list_items(payload)
        if not items:
            break
        page_emitted = 0
        for item in items[:request_limit]:
            candidate = candidate_from_item(source, item, emitted + page_emitted + 1, query["id"], query["text"])
            dedup_key = candidate.external_id
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            page_emitted += 1
            native_score = first_value(item, "score", "relevance", "similarity", "rankingScore")
            try:
                native_score = float(native_score) if native_score != "" else None
            except Exception:
                native_score = None
            candidate.metadata["api_endpoint"] = url.split("?", 1)[0]
            candidate.metadata["api_page"] = page
            candidate.metadata["response_request_id"] = response_headers.get("x-request-id", "")
            yield candidate, emitted + page_emitted, native_score
        emitted += page_emitted
        if source != "skillsmp" or len(items) < request_limit or page_emitted == 0:
            break
        page += 1


def discover_tessl(query, limit):
    executable = shutil.which("tessl")
    if not executable:
        raise legacy.CrawlError("Tessl CLI not found. Install and authenticate the official Tessl CLI first.")
    commands = [
        [executable, "search", query["text"], "--type", "skills", "--json"],
        [executable, "search", query["text"], "--type", "skills"],
    ]
    output = ""
    error = ""
    for command in commands:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        if completed.returncode == 0:
            output = completed.stdout
            break
        error = completed.stderr
    if not output:
        raise legacy.CrawlError("Tessl CLI search failed: " + error[:500])
    try:
        payload = json.loads(output)
        items = list_items(payload)
    except Exception:
        items = [{"name": line.strip(), "description": "", "cli_raw_line": line} for line in output.splitlines() if line.strip() and not line.lstrip().startswith(("Search", "-"))]
    for rank, item in enumerate(items[:limit], 1):
        yield candidate_from_item("tessl", item, rank, query["id"], query["text"]), rank, None


def metadata_gate(title, description, metadata, query_texts=None, best_rank=999999):
    query_texts = query_texts or []
    meta_text = flatten_text(metadata)
    text = compact_space(" ".join([title or "", description or "", meta_text]))
    lower = text.casefold()
    evidence = []
    score = 0
    direct_matches = []
    for pattern in DIRECT_PHRASES:
        match = re.search(pattern, text, re.I)
        if match:
            direct_matches.append(match.group(0))
    if direct_matches:
        score += 9
        evidence.append({"kind": "explicit_direct", "matches": direct_matches[:8], "weight": 9})
    actions = [word for word in ACTION_WORDS if word.casefold() in lower]
    artifacts = [word for word in ARTIFACT_WORDS if word.casefold() in lower]
    if actions and artifacts:
        score += 7
        evidence.append({"kind": "action_artifact", "actions": actions[:8], "artifacts": artifacts[:10], "weight": 7})
    if SOFTWARE_DOMAIN.search(text):
        score += 2
        evidence.append({"kind": "software_domain", "match": SOFTWARE_DOMAIN.search(text).group(0), "weight": 2})
    if query_texts:
        score += 2
        evidence.append({"kind": "targeted_query_provenance", "queries": query_texts[:8], "weight": 2})
    if best_rank <= 20:
        score += 1
        evidence.append({"kind": "top_native_rank", "rank": best_rank, "weight": 1})
    negated = NEGATION.search(text)
    non_code = NON_CODE.search(text)
    support = SUPPORT_ONLY.search(text)
    if negated:
        score -= 12
        evidence.append({"kind": "negated", "match": negated.group(0), "weight": -12})
    if non_code and not direct_matches and not (actions and artifacts and SOFTWARE_DOMAIN.search(text)):
        score -= 10
        evidence.append({"kind": "non_code_output", "match": non_code.group(0), "weight": -10})
    if support and not direct_matches and not (actions and artifacts):
        score -= 4
        evidence.append({"kind": "support_only", "match": support.group(0), "weight": -4})
    if negated or score < 0:
        label = "metadata_rejected"
    elif direct_matches or (actions and artifacts):
        label = "auto_resolve"
    elif score >= 3 or best_rank <= 20:
        label = "review_or_resolve"
    else:
        label = "metadata_rejected"
    return {"gate_version": GATE_VERSION, "label": label, "score": score, "evidence": evidence, "text": text[:2000]}


def discover_command(args):
    profile, queries = load_profile(args.profile, args.tiers, args.groups, args.max_queries, args.queries_per_group)
    sources = list(SOURCE_SPECS) if args.source == "all" else [x.strip() for x in args.source.split(",") if x.strip()]
    http = legacy.Http(args.user_agent, args.delay, args.timeout)
    store = TargetedStore(args.db)
    totals = {
        "queries_planned": len(queries) * len(sources),
        "queries_completed": 0,
        "queries_skipped": 0,
        "queries_deferred_quota": 0,
        "hits_returned": 0,
        "hits_stored": 0,
        "errors": 0,
        "quota_stopped_sources": [],
    }
    for source in sources:
        if source not in SOURCE_SPECS:
            raise SystemExit("Unknown targeted source: " + source)
        spec = SOURCE_SPECS[source]
        if not spec.get("enabled") and not args.enable_disabled:
            print(f"SKIP {source}: disabled; use --enable-disabled after official setup", file=sys.stderr)
            continue
        for query_index, query in enumerate(queries):
            if args.resume_search and store.search_completed(source, query["id"], profile["version"], args.per_query):
                totals["queries_skipped"] += 1
                continue
            run_id = store.start_search(source, query, profile["version"], args.per_query)
            returned = stored = 0
            error = ""
            quota_exhausted = False
            try:
                if source == "github":
                    iterator = discover_github(http, query, args.per_query)
                elif source == "tessl":
                    iterator = discover_tessl(query, args.per_query)
                else:
                    iterator = discover_json_source(http, source, query, args.per_query, args.endpoint)
                for candidate, rank, native_score in iterator:
                    returned += 1
                    store.save_hit(candidate, query, rank, native_score)
                    stored += 1
                    if args.verbose:
                        print(json.dumps({"source": source, "query": query["text"], "rank": rank, "candidate": asdict(candidate)}, ensure_ascii=False))
                totals["queries_completed"] += 1
            except DailyQuotaExceeded as exc:
                error = str(exc)
                quota_exhausted = True
                totals["errors"] += 1
                totals["queries_deferred_quota"] += len(queries) - query_index - 1
                totals["quota_stopped_sources"].append(source)
                print(f"QUOTA STOP {source}: {error}", file=sys.stderr)
            except Exception as exc:
                error = str(exc)
                totals["errors"] += 1
                print(f"ERROR {source} query={query['text']!r}: {error}", file=sys.stderr)
                if args.stop_on_error:
                    store.finish_search(run_id, returned, stored, error)
                    raise
            store.finish_search(run_id, returned, stored, error)
            totals["hits_returned"] += returned
            totals["hits_stored"] += stored
            if quota_exhausted:
                break
    totals.update(store.base.stats())
    totals["discovery_runs"] = store.db.execute("SELECT COUNT(*) FROM discovery_runs").fetchone()[0]
    totals["discovery_hits"] = store.db.execute("SELECT COUNT(*) FROM discovery_hits").fetchone()[0]
    print(json.dumps(totals, ensure_ascii=False, indent=2))
    store.db.close()


def gate_command(args):
    store = TargetedStore(args.db)
    rows = store.db.execute(
        "SELECT o.source,o.external_id,o.title,o.description,o.metadata_json,COALESCE(MIN(h.rank),999999),COUNT(DISTINCT h.query_id),GROUP_CONCAT(DISTINCT h.query_text) "
        "FROM occurrences o LEFT JOIN discovery_hits h ON h.source=o.source AND h.external_id=o.external_id GROUP BY o.source,o.external_id"
    ).fetchall()
    out_rows = []
    counts = {}
    for source, external_id, title, description, metadata_json, best_rank, query_count, query_concat in rows:
        try:
            metadata = json.loads(metadata_json or "{}")
        except Exception:
            metadata = {}
        query_texts = [x for x in (query_concat or "").split(",") if x]
        result = metadata_gate(title, description, metadata, query_texts, int(best_rank or 999999))
        previous = store.db.execute(
            "SELECT status FROM candidate_queue WHERE source=? AND external_id=? AND gate_version=?",
            (source, external_id, GATE_VERSION),
        ).fetchone()
        status = previous[0] if previous and previous[0] in {"resolved", "failed", "skipped_existing"} else ("pending" if result["label"] != "metadata_rejected" else "rejected")
        store.db.execute(
            "INSERT INTO candidate_queue(source,external_id,gate_version,gate_label,gate_score,gate_evidence_json,best_rank,query_count,status,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(source,external_id,gate_version) DO UPDATE SET gate_label=excluded.gate_label,gate_score=excluded.gate_score,gate_evidence_json=excluded.gate_evidence_json,best_rank=excluded.best_rank,query_count=excluded.query_count,status=excluded.status,updated_at=excluded.updated_at",
            (source, external_id, GATE_VERSION, result["label"], result["score"], json.dumps(result["evidence"], ensure_ascii=False), best_rank, query_count, status, utcnow()),
        )
        counts[result["label"]] = counts.get(result["label"], 0) + 1
        out_rows.append({"source": source, "external_id": external_id, "title": title, "description": description, "gate_label": result["label"], "gate_score": result["score"], "best_rank": best_rank, "query_count": query_count, "query_texts": " | ".join(query_texts), "evidence": json.dumps(result["evidence"], ensure_ascii=False)})
    store.db.commit()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8-sig", newline="") as handle:
        cols = ["source", "external_id", "title", "description", "gate_label", "gate_score", "best_rank", "query_count", "query_texts", "evidence"]
        writer = csv.DictWriter(handle, fieldnames=cols)
        writer.writeheader()
        writer.writerows(out_rows)
    print(json.dumps({"gate_version": GATE_VERSION, "records": len(rows), "counts": counts, "output": args.out}, ensure_ascii=False, indent=2))
    store.db.close()


def decode_github_content(payload):
    encoded = payload.get("content", "") if isinstance(payload, dict) else ""
    if not encoded:
        return ""
    return base64.b64decode(encoded).decode("utf-8", "replace")


def embedded_markdown(metadata):
    for path in ("content", "markdown", "skillMd", "skill_md", "files.SKILL.md", "file.content"):
        value = first_value(metadata, path)
        if isinstance(value, str) and len(value) >= 20:
            return value
    return ""


def clawhub_skill_md(http, candidate):
    slug = quote((candidate.slug or candidate.external_id).strip("/"), safe="@._-")
    endpoints = [
        f"https://clawhub.ai/api/v1/skills/{slug}/file?path=SKILL.md",
        f"https://clawhub.ai/api/v1/skills/{slug}/files/SKILL.md",
    ]
    for endpoint in endpoints:
        try:
            payload, _ = api_get_json(http, endpoint, auth_headers("clawhub"), retries=2)
            if isinstance(payload, str):
                return payload, endpoint
            content = first_value(payload, "content", "data.content", "file.content", "markdown")
            if isinstance(content, str) and content.strip():
                return content, endpoint
        except Exception:
            continue
    return "", endpoints[0]


def resolve_one(http, candidate):
    embedded = embedded_markdown(candidate.metadata)
    if embedded:
        return embedded, "embedded_metadata", candidate.page_url
    if candidate.source == "github" and candidate.raw_url:
        payload = legacy.github_request(http, candidate.raw_url)
        content = decode_github_content(payload)
        if content:
            candidate.metadata["github_blob_sha"] = payload.get("sha")
            return content, "github_exact_content_api", candidate.raw_url
    if candidate.repo_url:
        content = legacy.resolve_github_skill(http, candidate)
        if content:
            return content, "github_confident_resolver", candidate.repo_url
    if candidate.source == "clawhub":
        content, endpoint = clawhub_skill_md(http, candidate)
        if content:
            return content, "clawhub_skill_md_only", endpoint
    return "", "unresolved", candidate.page_url or candidate.repo_url


def resolve_command(args):
    store = TargetedStore(args.db)
    labels = [x.strip() for x in args.labels.split(",") if x.strip()]
    placeholders = ",".join("?" for _ in labels)
    query = (
        "SELECT o.source,o.external_id,o.page_url,o.title,o.description,o.repo_url,o.path,o.raw_url,o.slug,o.metadata_json,o.content_sha256,q.gate_label,q.gate_score "
        "FROM candidate_queue q JOIN occurrences o ON o.source=q.source AND o.external_id=q.external_id "
        f"WHERE q.gate_version=? AND q.gate_label IN ({placeholders}) ORDER BY q.gate_score DESC,q.best_rank ASC"
    )
    params = [GATE_VERSION] + labels
    rows = store.db.execute(query, params).fetchall()
    http = legacy.Http(args.user_agent, args.delay, args.timeout)
    counts = {"selected": len(rows), "resolved": 0, "skipped_existing": 0, "failed": 0, "unresolved": 0}
    processed = 0
    for row in rows:
        source, external_id, page, title, description, repo, path, raw_url, slug, metadata_json, existing_hash, gate_label, gate_score = row
        if args.limit and processed >= args.limit:
            break
        processed += 1
        if existing_hash and not args.force:
            store.db.execute("UPDATE candidate_queue SET status='skipped_existing',updated_at=? WHERE source=? AND external_id=? AND gate_version=?", (utcnow(), source, external_id, GATE_VERSION))
            counts["skipped_existing"] += 1
            continue
        try:
            metadata = json.loads(metadata_json or "{}")
        except Exception:
            metadata = {}
        candidate = legacy.Candidate(source, external_id, page or "", title or "", description or "", repo or "", path or "", raw_url or "", slug or "", metadata)
        resolver = target = ""
        try:
            content, resolver, target = resolve_one(http, candidate)
            if content:
                store.base.save(candidate, content)
                content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                status = "resolved"
                counts["resolved"] += 1
            else:
                content_hash = ""
                status = "unresolved"
                counts["unresolved"] += 1
            detail = {"gate_label": gate_label, "gate_score": gate_score, "resolution_status": candidate.metadata.get("resolution_status", ""), "resolution_reason": candidate.metadata.get("resolution_reason", "")}
        except Exception as exc:
            content_hash = ""
            status = "failed"
            detail = {"error": str(exc), "gate_label": gate_label, "gate_score": gate_score}
            counts["failed"] += 1
        store.db.execute("UPDATE candidate_queue SET status=?,updated_at=? WHERE source=? AND external_id=? AND gate_version=?", (status, utcnow(), source, external_id, GATE_VERSION))
        store.db.execute("INSERT INTO fetch_receipts(source,external_id,resolver,target,status,content_sha256,detail_json,fetched_at) VALUES(?,?,?,?,?,?,?,?)", (source, external_id, resolver, target, status, content_hash, json.dumps(detail, ensure_ascii=False), utcnow()))
        store.db.commit()
        if args.verbose:
            print(json.dumps({"source": source, "external_id": external_id, "status": status, "resolver": resolver, "target": target}, ensure_ascii=False))
    counts["processed"] = processed
    counts.update(store.base.stats())
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    store.db.close()


def stats_command(args):
    store = TargetedStore(args.db)
    result = store.base.stats()
    result["discovery_runs"] = store.db.execute("SELECT COUNT(*) FROM discovery_runs").fetchone()[0]
    result["discovery_hits"] = store.db.execute("SELECT COUNT(*) FROM discovery_hits").fetchone()[0]
    result["unique_discovered"] = store.db.execute("SELECT COUNT(DISTINCT source || ':' || external_id) FROM discovery_hits").fetchone()[0]
    result["gate_counts"] = dict(store.db.execute("SELECT gate_label,COUNT(*) FROM candidate_queue WHERE gate_version=? GROUP BY gate_label", (GATE_VERSION,)).fetchall())
    result["queue_status"] = dict(store.db.execute("SELECT status,COUNT(*) FROM candidate_queue WHERE gate_version=? GROUP BY status", (GATE_VERSION,)).fetchall())
    result["source_hits"] = dict(store.db.execute("SELECT source,COUNT(*) FROM discovery_hits GROUP BY source").fetchall())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    store.db.close()


def export_queue(args):
    store = TargetedStore(args.db)
    rows = store.db.execute(
        "SELECT q.source,q.external_id,o.page_url,o.title,o.description,o.repo_url,o.path,o.content_sha256,q.gate_label,q.gate_score,q.best_rank,q.query_count,q.status,q.gate_evidence_json "
        "FROM candidate_queue q JOIN occurrences o ON o.source=q.source AND o.external_id=q.external_id WHERE q.gate_version=? ORDER BY q.gate_score DESC,q.best_rank ASC",
        (GATE_VERSION,),
    ).fetchall()
    cols = ["source", "external_id", "page_url", "title", "description", "repo_url", "path", "content_sha256", "gate_label", "gate_score", "best_rank", "query_count", "status", "gate_evidence"]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(cols)
        writer.writerows(rows)
    print(args.out)
    store.db.close()


def probe_command(args):
    for source, spec in SOURCE_SPECS.items():
        env_name = spec.get("auth_env") or ""
        print(json.dumps({"source": source, "kind": spec["kind"], "enabled": spec["enabled"], "endpoint": spec["endpoint"], "credential_env": env_name, "credential_configured": bool(os.getenv(env_name, "")) if env_name else None, "cli_available": bool(shutil.which("tessl")) if source == "tessl" else None, "note": spec["note"]}, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(description="Targeted direct code-generation Skill discovery")
    parser.add_argument("--user-agent", default=os.getenv("SKILL_CRAWLER_USER_AGENT", legacy.DEFAULT_UA))
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("probe")

    discover = sub.add_parser("discover", help="Run cheap site-native search and save metadata only")
    discover.add_argument("--source", default="github")
    discover.add_argument("--db", required=True)
    discover.add_argument("--profile", default=str(PROFILE_DEFAULT))
    discover.add_argument("--tiers", default="core", help="Comma-separated: core,extended")
    discover.add_argument("--groups", default="", help="Optional comma-separated group IDs")
    discover.add_argument("--per-query", type=int, default=100)
    discover.add_argument("--max-queries", type=int, default=0)
    discover.add_argument("--queries-per-group", type=int, default=0, help="Round-robin-like cap per selected query group; 3 is recommended for the first pilot")
    discover.add_argument("--endpoint", default="", help="Optional endpoint override for one source")
    discover.add_argument("--resume-search", action=argparse.BooleanOptionalAction, default=True)
    discover.add_argument("--enable-disabled", action="store_true")
    discover.add_argument("--stop-on-error", action="store_true")
    discover.add_argument("--verbose", action="store_true")

    gate = sub.add_parser("gate", help="Apply high-recall metadata gate")
    gate.add_argument("--db", required=True)
    gate.add_argument("--out", default="data/targeted_gate_results.csv")

    resolve = sub.add_parser("resolve", help="Download SKILL.md only for selected candidates")
    resolve.add_argument("--db", required=True)
    resolve.add_argument("--labels", default="auto_resolve,review_or_resolve")
    resolve.add_argument("--limit", type=int, default=0)
    resolve.add_argument("--force", action="store_true")
    resolve.add_argument("--verbose", action="store_true")

    stats = sub.add_parser("stats")
    stats.add_argument("--db", required=True)

    export = sub.add_parser("export-queue")
    export.add_argument("--db", required=True)
    export.add_argument("--out", required=True)
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "probe":
        probe_command(args)
    elif args.command == "discover":
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        discover_command(args)
    elif args.command == "gate":
        gate_command(args)
    elif args.command == "resolve":
        resolve_command(args)
    elif args.command == "stats":
        stats_command(args)
    elif args.command == "export-queue":
        export_queue(args)


if __name__ == "__main__":
    main()












