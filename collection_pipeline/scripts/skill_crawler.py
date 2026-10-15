#!/usr/bin/env python3
"""Polite, provenance-first multi-source Agent Skill crawler (stdlib only)."""
from __future__ import annotations
import argparse, base64, csv, gzip, hashlib, html, json, os, re, sqlite3, sys, time
import urllib.error, urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, urlsplit, urlunsplit

VERSION="0.2.1"
for _stream in (sys.stdout,sys.stderr):
 try:_stream.reconfigure(encoding="utf-8",errors="backslashreplace")
 except Exception:pass
GITHUB_MAX_BYTES=50_000_000
DEFAULT_UA="CodeSkillServerResearch/0.1 (contact=replace-with-email)"
CODE_SEARCH_MAX_RESULTS=1000
CODE_SEARCH_MAX_PAGES=10

def should_split_code_search(total,lo,hi):
 return total>=CODE_SEARCH_MAX_RESULTS and lo<hi

GITHUB_RE=re.compile(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/(?:tree|blob)/[^\"'<>\s]+)?",re.I)

SOURCES={
 "github":{"kind":"github","enabled":True,"note":"Requires GITHUB_TOKEN; official GitHub APIs."},
 "skills_sh":{"kind":"sitemap","enabled":True,"sitemap":"https://skills.sh/sitemap.xml","sitemap_contains":["sitemap-skills-"],"url_contains":["skills.sh/"],"infer":"skills_sh","note":"Sitemap only; robots disallows /api/."},
 "skillsmp":{"kind":"sitemap","enabled":True,"sitemap":"https://skillsmp.com/sitemap.xml","sitemap_contains":["/sitemaps/skills-","/sitemaps/repositories-"],"url_contains":["skillsmp.com/"],"infer":"skillsmp","note":"Sitemaps/pages only; robots disallows /api/."},
 "claude_plugins":{"kind":"sitemap","enabled":True,"sitemap":"https://claude-plugins.dev/sitemap.xml","sitemap_contains":["sitemap-"],"url_contains":["/skills/"],"infer":"claude_plugins","note":"Skill sitemap only; robots disallows /api/."},
 "agentskills":{"kind":"json_pages","enabled":False,"endpoint":"https://agentskills.in/api/skills?limit={limit}&offset={offset}","list_field":"skills","note":"Reference-only; ai-train=no content signal; endpoint was intermittently unstable."},
 "clawhub":{"kind":"json_feed","enabled":True,"endpoint":"https://clawhub.ai/v1/feeds/skills","list_field":"entries","note":"Robots-allowed official feed; /api/ is not used."},
 "smithery":{"kind":"sitemap","enabled":True,"sitemap":"https://smithery.ai/sitemap_index.xml","sitemap_contains":["/skills/sitemap/"],"url_contains":["/skills/"],"infer":"smithery","note":"Public skill sitemaps/pages; /api/ is not used."},
 "tessl":{"kind":"external","enabled":False,"note":"Use authenticated official Tessl CLI/API; website scraping intentionally omitted."},
}

@dataclass
class Candidate:
 source:str; external_id:str; page_url:str=""; title:str=""; description:str=""; repo_url:str=""; path:str=""; raw_url:str=""; slug:str=""; metadata:dict=field(default_factory=dict)
 def text(self): return " ".join([self.title,self.description,self.page_url,self.repo_url,self.path]).lower()

class CrawlError(RuntimeError): pass

class Http:
 def __init__(self,ua=DEFAULT_UA,delay=1.0,timeout=25,max_bytes=8_000_000): self.ua=ua; self.delay=delay; self.timeout=timeout; self.max_bytes=max_bytes; self.last={}; self.robots={}; self.github_repo_cache={}; self.github_tree_cache={}; self.github_404_cache=set()
 def wait(self,host):
  left=self.delay-(time.monotonic()-self.last.get(host,0));
  if left>0: time.sleep(left)
  self.last[host]=time.monotonic()
 def robot_rules(self,url):
  p=urlparse(url); key=f"{p.scheme}://{p.netloc}"
  if key in self.robots:return self.robots[key]
  allow=[]; deny=[]
  try:
   self.wait(p.netloc); req=urllib.request.Request(key+"/robots.txt",headers={"User-Agent":self.ua,"Accept":"text/plain"})
   with urllib.request.urlopen(req,timeout=self.timeout) as r:text=r.read(200_000).decode("utf-8","replace")
   active=False
   for raw in text.splitlines():
    line=raw.split("#",1)[0].strip()
    if ":" not in line:continue
    k,v=[x.strip() for x in line.split(":",1)]; k=k.lower()
    if k=="user-agent":active=(v=="*")
    elif active and k=="allow" and v:allow.append(v)
    elif active and k=="disallow" and v:deny.append(v)
  except Exception:pass
  self.robots[key]=(allow,deny); return allow,deny
 def allowed(self,url):
  p=urlparse(url); allow,deny=self.robot_rules(url); path=p.path or "/"
  rules=[(len(x),True) for x in allow if path.startswith(x)]+[(len(x),False) for x in deny if path.startswith(x)]
  return max(rules,default=(0,True))[1]
 def get(self,url,accept="*/*",check_robots=True,retries=3):
  if check_robots and not self.allowed(url):raise CrawlError(f"robots.txt disallows {url}")
  p=urlparse(url); err=None
  for attempt in range(retries):
   try:
    self.wait(p.netloc); req=urllib.request.Request(url,headers={"User-Agent":self.ua,"Accept":accept,"Accept-Encoding":"gzip"})
    with urllib.request.urlopen(req,timeout=self.timeout) as r:
     b=r.read(self.max_bytes+1)
     if len(b)>self.max_bytes:raise CrawlError(f"response too large: {url}")
     if r.headers.get("Content-Encoding")=="gzip":b=gzip.decompress(b)
     return r.geturl(),r.status,r.headers,b
   except urllib.error.HTTPError as e:
    err=e
    if e.code not in {429,500,502,503,504}:raise CrawlError(f"HTTP {e.code}: {url}") from e
    retry=e.headers.get("Retry-After");time.sleep(float(retry) if retry and retry.isdigit() else 2**attempt)
   except (urllib.error.URLError,TimeoutError) as e:err=e;time.sleep(2**attempt)
  raise CrawlError(f"request failed: {url}: {err}")

def parse_sitemap(data):
 root=ET.fromstring(data);kind="index" if root.tag.endswith("sitemapindex") else "urlset";return kind,[x.text.strip() for x in root.iter() if x.tag.endswith("loc") and x.text]
def repair_text(value):
 value=html.unescape(value or "")
 try:
  repaired=value.encode("latin1").decode("utf-8")
  old_cjk=sum("\u4e00"<=c<="\u9fff" for c in value);new_cjk=sum("\u4e00"<=c<="\u9fff" for c in repaired)
  if new_cjk>old_cjk:return repaired
 except Exception:pass
 return value

def html_meta(text):
 out={"github_urls":[]};m=re.search(r"<title[^>]*>(.*?)</title>",text,re.I|re.S)
 if m:out["title"]=repair_text(re.sub(r"\s+"," ",m.group(1))).strip()
 for name in ["description","og:description","twitter:description"]:
  m=re.search(rf'<meta[^>]+(?:name|property)=["\']{re.escape(name)}["\'][^>]+content=["\'](.*?)["\']',text,re.I|re.S)
  if not m:m=re.search(rf'<meta[^>]+content=["\'](.*?)["\'][^>]+(?:name|property)=["\']{re.escape(name)}["\']',text,re.I|re.S)
  if m:out["description"]=repair_text(m.group(1)).strip();break
 for u in GITHUB_RE.findall(html.unescape(text).replace("\\/","/")):
  u=u.rstrip(".,);]\\")
  if u not in out["github_urls"]:out["github_urls"].append(u)
 return out
def split_github(url):
 p=urlparse(url);parts=[x for x in p.path.split("/") if x]
 if p.netloc.lower() not in {"github.com","www.github.com"} or len(parts)<2:return "","",""
 repo=f"https://github.com/{parts[0]}/{parts[1].removesuffix('.git')}"
 if len(parts)>=5 and parts[2] in {"tree","blob"}:return repo,"/".join(parts[4:]),parts[3]
 return repo,"",""

def repo_key(url):
 repo,_,_=split_github(url)
 return repo.lower().rstrip("/")

def infer_page(url,mode):
 p=urlparse(url);parts=[unquote(x) for x in p.path.split("/") if x]
 if mode=="skills_sh" and len(parts)>=3:return f"https://github.com/{parts[0]}/{parts[1]}",parts[-1]
 if mode=="claude_plugins" and len(parts)>=4 and parts[0]=="skills":return f"https://github.com/{parts[1].lstrip('@')}/{parts[2]}",parts[-1]
 if mode=="skillsmp" and len(parts)>=4 and parts[0]=="creators":return f"https://github.com/{parts[1]}/{parts[2]}",parts[-1]
 if mode=="smithery" and len(parts)>=3 and parts[0]=="skills":return "",parts[-1]
 return "",parts[-1] if parts else ""

def norm_slug(value):
 value=unquote(value or "").lower().replace("_","-")
 value=re.sub(r"[^a-z0-9\u4e00-\u9fff]+","-",value).strip("-")
 return value

def slug_variants(slug):
 base=norm_slug(slug);out={base} if base else set()
 prefixes=["agents-skills-","agent-skills-","skills-","skill-","docs-zh-cn-skills-","docs-ja-jp-skills-","docs-en-skills-","claude-skills-"]
 changed=True
 while changed:
  changed=False
  for item in list(out):
   for prefix in prefixes:
    if item.startswith(prefix) and len(item)>len(prefix):
     candidate=item[len(prefix):]
     if candidate not in out:out.add(candidate);changed=True
 # Marketplace flattened paths often end with the real skill directory.
 parts=base.split("-") if base else []
 for n in range(2,min(7,len(parts)+1)):out.add("-".join(parts[-n:]))
 return {x for x in out if x}

def path_match_score(path,slug):
 path_low=unquote(path).lower();segments=[norm_slug(x) for x in path_low.split("/") if x]
 parent=segments[-2] if len(segments)>=2 else ""
 flat=norm_slug(path_low.rsplit("/skill.md",1)[0])
 best=0;reason=""
 for variant in slug_variants(slug):
  if parent==variant and len(variant)>=3:return 120,"exact_parent"
  if flat.endswith("-"+variant) or flat==variant:
   if len(variant)>=4 and 105>best:best,reason=105,"path_suffix"
  if variant in segments and len(variant)>=4 and 95>best:best,reason=95,"path_segment"
  vt=set(variant.split("-"));pt=set(flat.split("-"));
  if vt and len(vt)>=2:
   j=len(vt&pt)/len(vt|pt)
   if j>=0.75 and int(70+j*20)>best:best,reason=int(70+j*20),"token_similarity"
 return best,reason

def choose_github_url(urls,inferred_repo,slug,owner_hint=""):
 parsed=[]
 for url in urls:
  repo,path,ref=split_github(str(url))
  if repo:parsed.append((repo,path,ref,str(url)))
 inferred_key=repo_key(inferred_repo)
 if inferred_key:
  same=[x for x in parsed if repo_key(x[0])==inferred_key]
  if same:
   same.sort(key=lambda x:(0 if x[1] else 1,-path_match_score(x[1],slug)[0] if x[1] else 0,len(x[3])))
   return same[0],"matched_inferred_repo"
  return (inferred_repo,"","",inferred_repo),"inferred_repo_authoritative"
 scored=[]
 for item in parsed:
  repo,path,ref,url=item;path_score,reason=path_match_score(path,slug) if path else (0,"");score=path_score
  repo_parts=[x for x in urlparse(repo).path.split("/") if x]
  if owner_hint and repo_parts and repo_parts[0].lower()==owner_hint.lower():score+=45
  if slug and norm_slug(slug) in norm_slug(repo):score+=25
  if path_score:score+=20
  scored.append((score,item,reason))
 if not scored:return None,"no_github_url"
 scored.sort(key=lambda x:(-x[0],len(x[1][3])))
 if scored[0][0]<40:return None,"low_confidence_github_url"
 return scored[0][1],scored[0][2] or "best_page_link"

def parse_frontmatter(md):
 if not md.startswith("---"):return {},md
 lines=md.splitlines();end=next((i for i in range(1,min(len(lines),300)) if lines[i].strip()=="---"),None)
 if end is None:return {},md
 meta={}
 for line in lines[1:end]:
  if ":" in line and not line.lstrip().startswith("#"):
   k,v=line.split(":",1);meta[k.strip()]=v.strip().strip('"\'')
 return meta,"\n".join(lines[end+1:]).lstrip()
def matches(text,terms):return not terms or any(x.lower() in text.lower() for x in terms)

def now():return datetime.now(timezone.utc).isoformat()
SCHEMA="""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS crawl_runs(run_id INTEGER PRIMARY KEY,source TEXT,started_at TEXT,finished_at TEXT,query TEXT,status TEXT,discovered INTEGER DEFAULT 0,stored INTEGER DEFAULT 0,errors INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS contents(content_sha256 TEXT PRIMARY KEY,raw_markdown TEXT,frontmatter_json TEXT,body TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS occurrences(occurrence_id INTEGER PRIMARY KEY,source TEXT,external_id TEXT,page_url TEXT,title TEXT,description TEXT,repo_url TEXT,path TEXT,raw_url TEXT,slug TEXT,content_sha256 TEXT,metadata_json TEXT,fetched_at TEXT,UNIQUE(source,external_id));
CREATE TABLE IF NOT EXISTS failures(failure_id INTEGER PRIMARY KEY,run_id INTEGER,source TEXT,target TEXT,error TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS classifications(occurrence_id INTEGER,classifier_version TEXT,score INTEGER,label TEXT,evidence_json TEXT,classified_at TEXT,PRIMARY KEY(occurrence_id,classifier_version));
"""
class Store:
 def __init__(self,path):self.db=sqlite3.connect(path);self.db.executescript(SCHEMA)
 def start(self,source,query):cur=self.db.execute("INSERT INTO crawl_runs(source,started_at,query,status) VALUES(?,?,?,'running')",(source,now(),query));self.db.commit();return cur.lastrowid
 def finish(self,r,d,s,e,status="completed"):self.db.execute("UPDATE crawl_runs SET finished_at=?,status=?,discovered=?,stored=?,errors=? WHERE run_id=?",(now(),status,d,s,e,r));self.db.commit()
 def exists(self,s,e):return self.db.execute("SELECT 1 FROM occurrences WHERE source=? AND external_id=?",(s,e)).fetchone() is not None
 def unresolved(self,s,e):
  row=self.db.execute("SELECT content_sha256 FROM occurrences WHERE source=? AND external_id=?",(s,e)).fetchone()
  return bool(row) and not bool(row[0])
 def save(self,c,content=""):
  h=None
  if content:
   h=hashlib.sha256(content.encode()).hexdigest();fm,body=parse_frontmatter(content);self.db.execute("INSERT OR IGNORE INTO contents VALUES(?,?,?,?,?)",(h,content,json.dumps(fm,ensure_ascii=False),body,now()))
  self.db.execute("""INSERT INTO occurrences(source,external_id,page_url,title,description,repo_url,path,raw_url,slug,content_sha256,metadata_json,fetched_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source,external_id) DO UPDATE SET page_url=excluded.page_url,title=excluded.title,description=excluded.description,repo_url=excluded.repo_url,path=excluded.path,raw_url=excluded.raw_url,slug=excluded.slug,content_sha256=COALESCE(excluded.content_sha256,occurrences.content_sha256),metadata_json=excluded.metadata_json,fetched_at=excluded.fetched_at""",(c.source,c.external_id,c.page_url,c.title,c.description,c.repo_url,c.path,c.raw_url,c.slug,h,json.dumps(c.metadata,ensure_ascii=False),now()));self.db.commit()
 def fail(self,r,s,t,e):self.db.execute("INSERT INTO failures(run_id,source,target,error,created_at) VALUES(?,?,?,?,?)",(r,s,t,e,now()));self.db.commit()
 def stats(self):return {"runs":self.db.execute("SELECT COUNT(*) FROM crawl_runs").fetchone()[0],"occurrences":self.db.execute("SELECT COUNT(*) FROM occurrences").fetchone()[0],"unique_contents":self.db.execute("SELECT COUNT(*) FROM contents").fetchone()[0],"failures":self.db.execute("SELECT COUNT(*) FROM failures").fetchone()[0]}
 def export(self,out,fmt):
  rows=self.db.execute("SELECT source,external_id,page_url,title,description,repo_url,path,slug,content_sha256,fetched_at FROM occurrences ORDER BY source,external_id");cols=["source","external_id","page_url","title","description","repo_url","path","slug","content_sha256","fetched_at"]
  if fmt=="csv":
   with open(out,"w",encoding="utf-8-sig",newline="") as f:w=csv.writer(f);w.writerow(cols);w.writerows(rows)
  else:
   with open(out,"w",encoding="utf-8") as f:
    for row in rows:f.write(json.dumps(dict(zip(cols,row)),ensure_ascii=False)+"\n")

def discover_sitemap(cfg,http,limit,terms,fetch_pages):
 q=deque([cfg["sitemap"]]);seen=set();count=0
 while q and count<limit:
  sm=q.popleft()
  if sm in seen:continue
  seen.add(sm);_,_,_,b=http.get(sm,"application/xml,text/xml,*/*");kind,urls=parse_sitemap(b)
  if kind=="index":
   for u in urls:
    if not cfg.get("sitemap_contains") or any(x in u for x in cfg["sitemap_contains"]):q.append(u)
   continue
  for page in urls:
   if count>=limit:break
   if cfg.get("url_contains") and not any(x in page for x in cfg["url_contains"]):continue
   repo,slug=infer_page(page,cfg.get("infer",""));c=Candidate(cfg["name"],page,page_url=page,repo_url=repo,slug=slug)
   if fetch_pages:
    try:
     _,_,_,pb=http.get(page,"text/html,application/xhtml+xml");meta=html_meta(pb.decode("utf-8","replace"));c.metadata.update(meta);c.title=str(meta.get("title",""));c.description=str(meta.get("description",""));gh=meta.get("github_urls") or []
     page_parts=[unquote(x) for x in urlparse(page).path.split("/") if x];owner_hint=(page_parts[1] if cfg.get("infer")=="smithery" and len(page_parts)>=3 else "");selected,selection_reason=choose_github_url(gh,c.repo_url,c.slug,owner_hint);c.metadata["github_selection_reason"]=selection_reason;c.metadata["github_url_candidates"]=gh[:25]
     if selected:
      rr,path,ref,_=selected
      if not c.repo_url or repo_key(rr)==repo_key(c.repo_url):
       c.repo_url=rr or c.repo_url
       if path:c.path=path
       if ref:c.metadata["github_ref"]=ref
    except Exception as e:c.metadata["page_fetch_error"]=str(e)
   if matches(c.text(),terms):yield c;count+=1

def discover_feed(cfg,http,limit,terms):
 _,_,_,b=http.get(cfg["endpoint"],"application/json");data=json.loads(b);items=data.get(cfg["list_field"],[]);count=0
 for item in items:
  title=str(item.get("title") or item.get("name") or "");desc=str(item.get("description") or item.get("summary") or "");eid=str(item.get("id") or item.get("slug") or hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest())
  repo=str(item.get("githubUrl") or item.get("repo_url") or "");page=str(item.get("url") or item.get("canonicalUrl") or "")
  c=Candidate(cfg["name"],eid,page,title,desc,repo,slug=str(item.get("slug") or title),metadata=item)
  if matches(c.text(),terms):yield c;count+=1
  if count>=limit:break

def discover_agentskills(cfg,http,limit,terms):
 offset=0;count=0;size=min(100,max(1,limit))
 while count<limit:
  u=cfg["endpoint"].format(limit=size,offset=offset);_,_,_,b=http.get(u,"application/json");data=json.loads(b);items=data.get(cfg["list_field"],[])
  if not items:break
  for item in items:
   c=Candidate("agentskills",str(item.get("id") or item.get("scopedName") or ""),str(item.get("url") or ""),str(item.get("name") or ""),str(item.get("description") or ""),str(item.get("githubUrl") or ""),slug=str(item.get("name") or ""),metadata=item)
   if matches(c.text(),terms):yield c;count+=1
   if count>=limit:break
  offset+=len(items)

def iri_to_uri(url):
 """Percent-encode non-ASCII URL path/query characters for urllib."""
 p=urlsplit(url)
 safe_path=quote(unquote(p.path),safe="/:@")
 safe_query=quote(unquote(p.query),safe="=&%:+,;@/?")
 return urlunsplit((p.scheme,p.netloc,safe_path,safe_query,p.fragment))

def github_request(http,url,require_token=False,retries=3):
 url=iri_to_uri(url)
 token=os.getenv("GITHUB_TOKEN","")
 if require_token and not token:raise CrawlError("GITHUB_TOKEN is required for GitHub Code Search")
 headers={"User-Agent":http.ua,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
 if token:headers["Authorization"]=f"Bearer {token}"
 parsed=urlparse(url);last=None
 for attempt in range(retries):
  try:
   http.wait(parsed.netloc);req=urllib.request.Request(url,headers=headers)
   with urllib.request.urlopen(req,timeout=http.timeout) as r:
     raw=r.read(GITHUB_MAX_BYTES+1)
     if len(raw)>GITHUB_MAX_BYTES:raise CrawlError(f"GitHub response too large: {url}")
     try:return json.loads(raw)
     except json.JSONDecodeError as decode_error:raise CrawlError(f"Invalid/truncated GitHub JSON: {url}: {decode_error}")
  except urllib.error.HTTPError as e:
   last=e
   if e.code not in {403,429,500,502,503,504}:raise CrawlError(f"GitHub HTTP {e.code}: {url}") from e
   reset=e.headers.get("X-RateLimit-Reset")
   if e.code==403 and reset and reset.isdigit():time.sleep(max(1,min(60,int(reset)-int(time.time())+1)))
   else:time.sleep(2**attempt)
  except Exception as e:last=e;time.sleep(2**attempt)
 raise CrawlError(f"GitHub request failed: {url}: {last}")

def discover_github(http,limit,terms,fetch_content):
 q=deque([(0,384000)]);count=0
 while q and count<limit:
  lo,hi=q.popleft();query=f"filename:SKILL.md size:{lo}..{hi}";base=f"https://api.github.com/search/code?q={quote(query)}&per_page=100";data=github_request(http,base,True);total=int(data.get("total_count",0))
  if should_split_code_search(total,lo,hi):mid=(lo+hi)//2;q.extend([(lo,mid),(mid+1,hi)]);continue
  page=1
  while count<limit and page<=CODE_SEARCH_MAX_PAGES:
   data=github_request(http,base+f"&page={page}",True);items=data.get("items",[])
   if not items:break
   for item in items:
    repo=item.get("repository") or {};content="";stable_id=f"github:{str(repo.get('full_name') or '').lower()}:{str(item.get('path') or '').lower()}";c=Candidate("github",stable_id,item.get("html_url",""),repo.get("full_name",""),"",repo.get("html_url",""),item.get("path",""),item.get("url",""),metadata={"sha":item.get("sha"),"commit_specific_html_url":item.get("html_url","")})
    if fetch_content:
     try:
      blob=github_request(http,item["url"]);enc=blob.get("content","")
      if enc:content=base64.b64decode(enc).decode("utf-8","replace");c.metadata["content"]=content
     except Exception as content_error:
      # A malformed/unavailable single path must not terminate the whole source run.
      c.metadata["content_fetch_error"]=str(content_error)
    if matches(c.text()+" "+content,terms):yield c;count+=1
    if count>=limit:break
   if len(items)<100:break
   page+=1

def resolve_github_skill(http,c):
 """Resolve one marketplace candidate only when repo/path evidence is confident."""
 repo,explicit_path,ref=split_github(c.repo_url)
 if not repo:c.metadata["resolution_status"]="no_repository";return ""
 parts=[x for x in urlparse(repo).path.split("/") if x]
 if len(parts)<2:return ""
 owner,name=parts[:2];repo_cache_key=f"{owner}/{name}".lower()
 if repo_cache_key not in http.github_repo_cache:http.github_repo_cache[repo_cache_key]=github_request(http,f"https://api.github.com/repos/{owner}/{name}")
 meta=http.github_repo_cache[repo_cache_key]
 branch=ref or c.metadata.get("github_ref") or meta.get("default_branch") or "main"
 page_path=c.path or explicit_path
 # Marketplace pages often link to the skill directory rather than the file.
 direct_paths=[]
 if page_path:
  direct_paths.append(page_path if page_path.split("/")[-1].lower()=="skill.md" else page_path.rstrip("/")+"/SKILL.md")
 for variant in sorted(slug_variants(c.slug),key=len,reverse=True):
  direct_paths.extend([f"skills/{variant}/SKILL.md",f".claude/skills/{variant}/SKILL.md",f".agents/skills/{variant}/SKILL.md",f"agents/skills/{variant}/SKILL.md",f"docs/zh-cn/skills/{variant}/SKILL.md",f"docs/ja-jp/skills/{variant}/SKILL.md"])
 seen_paths=set()
 for direct_path in direct_paths[:18]:
  if direct_path in seen_paths:continue
  seen_paths.add(direct_path)
  try:
   blob=github_request(http,f"https://api.github.com/repos/{owner}/{name}/contents/{quote(direct_path)}?ref={quote(branch,safe='')}")
   enc=blob.get("content","")
   if enc:
    c.path=direct_path;c.raw_url=blob.get("download_url") or "";c.metadata.update({"resolution_status":"direct_path_probe","resolution_score":950,"github_default_branch":branch,"github_blob_sha":blob.get("sha")})
    return base64.b64decode(enc).decode("utf-8","replace")
  except CrawlError as probe_error:
   if "HTTP 404" not in str(probe_error):c.metadata.setdefault("direct_path_probe_errors",[]).append(str(probe_error))
 if page_path and page_path.split("/")[-1].lower()=="skill.md":
  blob=github_request(http,f"https://api.github.com/repos/{owner}/{name}/contents/{quote(page_path)}?ref={quote(branch,safe='')}")
  enc=blob.get("content","")
  if enc:
   c.path=page_path;c.raw_url=blob.get("download_url") or "";c.metadata.update({"resolution_status":"explicit_page_path","resolution_score":1000,"github_default_branch":branch,"github_blob_sha":blob.get("sha")})
   return base64.b64decode(enc).decode("utf-8","replace")
 tree_cache_key=(repo_cache_key,branch)
 if tree_cache_key not in http.github_tree_cache:http.github_tree_cache[tree_cache_key]=github_request(http,f"https://api.github.com/repos/{owner}/{name}/git/trees/{quote(branch,safe='' )}?recursive=1")
 tree=http.github_tree_cache[tree_cache_key]
 candidates=[]
 for item in tree.get("tree",[]):
  pth=str(item.get("path") or "")
  if item.get("type")=="blob" and pth.split("/")[-1].lower()=="skill.md":
   score,reason=path_match_score(pth,c.slug);candidates.append({"score":score,"reason":reason,"path":pth,"sha":item.get("sha")})
 if not candidates:c.metadata.update({"resolution_status":"no_skill_md","github_tree_truncated":tree.get("truncated",False)});return ""
 candidates.sort(key=lambda x:(-x["score"],len(x["path"]),x["path"]))
 if len(candidates)==1 and c.metadata.get("github_selection_reason") in {"matched_inferred_repo","inferred_repo_authoritative"}:
  candidates[0]["score"]=max(candidates[0]["score"],90);candidates[0]["reason"]=candidates[0]["reason"] or "single_skill_authoritative_repo"
 top=candidates[0];ties=[x for x in candidates if x["score"]==top["score"]]
 c.metadata.update({"github_default_branch":branch,"github_commit_or_tree_sha":tree.get("sha"),"github_tree_truncated":tree.get("truncated",False),"github_skill_candidates":len(candidates),"resolution_top_candidates":candidates[:10]})
 if top["score"]<80 or len(ties)>1:
  c.metadata.update({"resolution_status":"ambiguous_source_match","resolution_score":top["score"],"resolution_reason":top["reason"],"resolution_ties":len(ties)});return ""
 pth=top["path"]
 blob=github_request(http,f"https://api.github.com/repos/{owner}/{name}/contents/{quote(pth)}?ref={quote(branch,safe='')}")
 enc=blob.get("content","")
 if not enc:return ""
 c.path=pth;c.raw_url=blob.get("download_url") or "";c.metadata.update({"resolution_status":"resolved","resolution_score":top["score"],"resolution_reason":top["reason"],"github_blob_sha":top["sha"]})
 return base64.b64decode(enc).decode("utf-8","replace")

def run_crawl(args,http):
 selected=list(SOURCES) if args.source=="all" else [args.source];store=Store(args.db);terms=[x.strip() for x in args.query.split(",") if x.strip()]
 for name in selected:
  if name not in SOURCES:raise SystemExit(f"unknown source: {name}")
  cfg={"name":name,**SOURCES[name]}
  if not cfg.get("enabled") and not args.enable_disabled:print(f"SKIP {name}: disabled",file=os.sys.stderr);continue
  run=store.start(name,args.query);d=s=e=0
  try:
   if cfg["kind"]=="sitemap":iterator=discover_sitemap(cfg,http,args.limit,terms,args.fetch_pages)
   elif cfg["kind"]=="json_feed":iterator=discover_feed(cfg,http,args.limit,terms)
   elif cfg["kind"]=="json_pages":iterator=discover_agentskills(cfg,http,args.limit,terms)
   elif cfg["kind"]=="github":iterator=discover_github(http,args.limit,terms,args.fetch_pages)
   else:raise CrawlError("Tessl requires official authenticated CLI/API; no web scraper is provided")
   for c in iterator:
    d+=1
    if args.resume and store.exists(c.source,c.external_id) and not (args.retry_unresolved and store.unresolved(c.source,c.external_id)):continue
    content=str(c.metadata.pop("content",""))
    if args.resolve_github and not content and c.repo_url:
     try:content=resolve_github_skill(http,c)
     except Exception as resolve_error:c.metadata["github_resolve_error"]=str(resolve_error)
    store.save(c,content);s+=1;print(json.dumps(asdict(c),ensure_ascii=False))
   store.finish(run,d,s,e)
  except Exception as ex:e+=1;store.fail(run,name,name,str(ex));store.finish(run,d,s,e,"failed");print(f"ERROR {name}: {ex}",file=os.sys.stderr)
 print(json.dumps(store.stats(),ensure_ascii=False),file=os.sys.stderr)


CODEGEN_CLASSIFIER_VERSION="function-codegen-heuristic-v1"
CODEGEN_RULES={
 "direct":{
  "code generation":6,"generate code":6,"code generator":6,"coding agent":5,"software engineering":4,"programming":4,
  "implement function":6,"function implementation":6,"implement a function":6,"write code":5,"code completion":5,"code synthesis":6
 },
 "function_task":{
  "function":3,"method":2,"docstring":3,"algorithm":3,"data structure":3,"unit test":3,"test generation":3,
  "debugging":2,"debug":2,"refactoring":2,"refactor":2,"type hint":2,"api usage":2,"library usage":2,
  "code review":2,"bug fix":2,"implementation":2
 },
 "language":{
  "python":2,"java":2,"javascript":2,"typescript":2,"golang":2," rust ":2," c++ ":2," c# ":2,
  "pytest":2,"unittest":2,"numpy":1,"pandas":1,"pytorch":1,"tensorflow":1
 },
 "negative":{
  "image generation":-5,"video generation":-5,"music generation":-5,"social media":-3,"marketing copy":-4,
  "seo content":-4,"presentation design":-3,"slide deck":-3,"blog writer":-3
 }
}

def classify_codegen_text(title,description,frontmatter,body,threshold=6):
 """Research heuristic, not a published taxonomy. Returns score/label/evidence."""
 fields={"title":title or "","description":description or "","frontmatter":frontmatter or "","body":body or ""}
 evidence=[];score=0;strong=False
 multipliers={"title":2,"description":2,"frontmatter":1,"body":1}
 for group,rules in CODEGEN_RULES.items():
  for term,weight in rules.items():
   for field_name,text in fields.items():
    if term.strip().lower() in text.lower():
     applied=weight*multipliers[field_name]
     # Negative evidence is only counted once per term to avoid long-body over-penalization.
     if weight<0 and any(e["term"]==term for e in evidence):continue
     score+=applied;evidence.append({"group":group,"term":term.strip(),"field":field_name,"weight":applied})
     if group=="direct":strong=True
     break
 positive_groups={e["group"] for e in evidence if e["weight"]>0}
 label="relevant" if score>=threshold and (strong or {"function_task","language"}.issubset(positive_groups)) else "not_relevant"
 return {"classifier_version":CODEGEN_CLASSIFIER_VERSION,"score":score,"label":label,"evidence":evidence}

def classify_database(db_path,out_path="",threshold=6,fmt="jsonl"):
 store=Store(db_path);rows=store.db.execute("""SELECT o.occurrence_id,o.source,o.external_id,o.page_url,o.title,o.description,o.repo_url,o.path,o.content_sha256,COALESCE(c.frontmatter_json,''),COALESCE(c.body,'') FROM occurrences o LEFT JOIN contents c ON o.content_sha256=c.content_sha256 ORDER BY o.occurrence_id""").fetchall()
 results=[]
 for row in rows:
  oid,source,eid,page,title,desc,repo,path,content_hash,fm,body=row
  result=classify_codegen_text(title,desc,fm,body,threshold)
  store.db.execute("INSERT INTO classifications VALUES(?,?,?,?,?,?) ON CONFLICT(occurrence_id,classifier_version) DO UPDATE SET score=excluded.score,label=excluded.label,evidence_json=excluded.evidence_json,classified_at=excluded.classified_at",(oid,result["classifier_version"],result["score"],result["label"],json.dumps(result["evidence"],ensure_ascii=False),now()))
  obj={"occurrence_id":oid,"source":source,"external_id":eid,"page_url":page,"title":title,"description":desc,"repo_url":repo,"path":path,"content_sha256":content_hash,**result}
  results.append(obj)
 store.db.commit()
 relevant=[x for x in results if x["label"]=="relevant"]
 if out_path:
  if fmt=="csv":
   cols=["occurrence_id","source","external_id","page_url","title","description","repo_url","path","content_sha256","classifier_version","score","label","evidence"]
   with open(out_path,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f);w.writerow(cols)
    for x in relevant:w.writerow([json.dumps(x[k],ensure_ascii=False) if k=="evidence" else x.get(k,"") for k in cols])
  else:
   with open(out_path,"w",encoding="utf-8") as f:
    for x in relevant:f.write(json.dumps(x,ensure_ascii=False)+"\n")
 return {"classified":len(results),"relevant":len(relevant),"threshold":threshold,"classifier_version":CODEGEN_CLASSIFIER_VERSION,"output":out_path}

def main():
 p=argparse.ArgumentParser(description="Polite public Agent Skill crawler starter");p.add_argument("--user-agent",default=os.getenv("SKILL_CRAWLER_USER_AGENT",DEFAULT_UA));p.add_argument("--delay",type=float,default=1);p.add_argument("--timeout",type=float,default=25)
 sp=p.add_subparsers(dest="cmd",required=True);sp.add_parser("probe")
 c=sp.add_parser("crawl");c.add_argument("--source",default="all");c.add_argument("--limit",type=int,default=20);c.add_argument("--query",default="");c.add_argument("--db",default="data/skills.db");c.add_argument("--fetch-pages",action="store_true");c.add_argument("--resolve-github",action="store_true");c.add_argument("--retry-unresolved",action="store_true");c.add_argument("--resume",action=argparse.BooleanOptionalAction,default=True);c.add_argument("--enable-disabled",action="store_true")
 s=sp.add_parser("stats");s.add_argument("--db",default="data/skills.db")
 x=sp.add_parser("export");x.add_argument("--db",default="data/skills.db");x.add_argument("--format",choices=["csv","jsonl"],default="jsonl");x.add_argument("--out",required=True)
 cl=sp.add_parser("classify-codegen");cl.add_argument("--db",default="data/skills.db");cl.add_argument("--threshold",type=int,default=6);cl.add_argument("--format",choices=["csv","jsonl"],default="jsonl");cl.add_argument("--out",default="data/codegen_candidates.jsonl")
 a=p.parse_args();http=Http(a.user_agent,a.delay,a.timeout)
 if a.cmd=="probe":
  for name,cfg in SOURCES.items():
   target=cfg.get("sitemap") or cfg.get("endpoint") or "";print(json.dumps({"source":name,"kind":cfg["kind"],"enabled":cfg["enabled"],"target":target,"robots_allowed":http.allowed(target) if target else None,"note":cfg["note"]},ensure_ascii=False))
 elif a.cmd=="crawl":Path(a.db).parent.mkdir(parents=True,exist_ok=True);run_crawl(a,http)
 elif a.cmd=="stats":print(json.dumps(Store(a.db).stats(),ensure_ascii=False,indent=2))
 elif a.cmd=="classify-codegen":
   raise SystemExit("Deprecated: use scripts/direct_codegen_filter_v2.py instead")
 else:Store(a.db).export(a.out,a.format);print(a.out)
if __name__=="__main__":main()






