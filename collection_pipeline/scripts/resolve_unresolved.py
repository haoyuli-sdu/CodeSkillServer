#!/usr/bin/env python3
import argparse,json,sqlite3
from pathlib import Path
try:
    from . import skill_crawler
except ImportError:  # Supports direct execution: python scripts/resolve_unresolved.py
    import skill_crawler

def main():
 p=argparse.ArgumentParser(description='Resolve GitHub SKILL.md bodies for metadata-only marketplace occurrences');p.add_argument('--db',required=True);p.add_argument('--source',default='skills_sh,claude_plugins,skillsmp,smithery');p.add_argument('--limit',type=int,default=0);p.add_argument('--delay',type=float,default=1.0);p.add_argument('--user-agent',default=skill_crawler.DEFAULT_UA);a=p.parse_args();sources=[x.strip() for x in a.source.split(',') if x.strip()]
 store=skill_crawler.Store(a.db);http=skill_crawler.Http(a.user_agent,a.delay);marks=','.join('?' for _ in sources);sql=f'''select source,external_id,page_url,title,description,repo_url,path,raw_url,slug,metadata_json from occurrences where content_sha256 is null and repo_url!='' and source in ({marks}) order by source,occurrence_id''';rows=store.db.execute(sql,sources).fetchall();rows=rows[:a.limit] if a.limit else rows;ok=ambiguous=errors=0
 for i,row in enumerate(rows,1):
  source,eid,page,title,desc,repo,path,raw,slug,meta_raw=row
  try:meta=json.loads(meta_raw or '{}')
  except:meta={}
  c=skill_crawler.Candidate(source,eid,page,title,desc,repo,path,raw,slug,meta)
  try:
   content=skill_crawler.resolve_github_skill(http,c);store.save(c,content)
   if content:ok+=1
   else:ambiguous+=1
  except Exception as e:
   errors+=1;c.metadata['resolver_error']=str(e);store.save(c,'')
  if i%50==0:print(json.dumps({'processed':i,'resolved':ok,'unresolved':ambiguous,'errors':errors},ensure_ascii=False),flush=True)
 print(json.dumps({'processed':len(rows),'resolved':ok,'unresolved':ambiguous,'errors':errors,'repo_cache':len(http.github_repo_cache),'tree_cache':len(http.github_tree_cache)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
