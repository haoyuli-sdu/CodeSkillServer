#!/usr/bin/env python3
"""Merge per-source targeted databases without losing discovery provenance."""
import argparse,sqlite3
from pathlib import Path
try:
    from . import skill_crawler
    from . import targeted_codegen_crawler as targeted
except ImportError:  # Supports direct execution from the scripts directory.
    import skill_crawler
    import targeted_codegen_crawler as targeted

def has_table(db,alias,name):
 return db.execute(f"SELECT 1 FROM {alias}.sqlite_master WHERE type='table' AND name=?",(name,)).fetchone() is not None

def main():
 p=argparse.ArgumentParser(description='Merge targeted per-source databases');p.add_argument('--out',required=True);p.add_argument('inputs',nargs='+');a=p.parse_args();Path(a.out).parent.mkdir(parents=True,exist_ok=True)
 out=sqlite3.connect(a.out);out.executescript(skill_crawler.SCHEMA);out.executescript(targeted.TARGETED_SCHEMA);out.execute('PRAGMA busy_timeout=30000')
 for idx,src in enumerate(a.inputs):
  src_path=str(Path(src).resolve());alias=f'src{idx}';print('merging',src_path);out.execute(f'ATTACH DATABASE ? AS {alias}',(src_path,))
  out.execute(f'INSERT OR IGNORE INTO contents SELECT * FROM {alias}.contents')
  out.execute(f'''INSERT INTO occurrences(source,external_id,page_url,title,description,repo_url,path,raw_url,slug,content_sha256,metadata_json,fetched_at)
   SELECT source,external_id,page_url,title,description,repo_url,path,raw_url,slug,content_sha256,metadata_json,fetched_at FROM {alias}.occurrences WHERE 1
   ON CONFLICT(source,external_id) DO UPDATE SET page_url=excluded.page_url,title=excluded.title,description=excluded.description,repo_url=excluded.repo_url,path=excluded.path,raw_url=excluded.raw_url,slug=excluded.slug,content_sha256=COALESCE(excluded.content_sha256,occurrences.content_sha256),metadata_json=excluded.metadata_json,fetched_at=MAX(excluded.fetched_at,occurrences.fetched_at)''')
  if has_table(out,alias,'discovery_runs'):
   out.execute(f'''INSERT INTO discovery_runs(source,query_id,query_text,query_group,query_tier,profile_version,requested_limit,started_at,finished_at,status,returned_count,stored_count,error)
    SELECT source,query_id,query_text,query_group,query_tier,profile_version,requested_limit,started_at,finished_at,status,returned_count,stored_count,error FROM {alias}.discovery_runs''')
  if has_table(out,alias,'discovery_hits'):
   out.execute(f'''INSERT INTO discovery_hits(source,external_id,query_id,query_text,query_group,query_tier,rank,native_score,route,hit_metadata_json,discovered_at)
    SELECT source,external_id,query_id,query_text,query_group,query_tier,rank,native_score,route,hit_metadata_json,discovered_at FROM {alias}.discovery_hits WHERE 1
    ON CONFLICT(source,external_id,query_id,route) DO UPDATE SET rank=MIN(discovery_hits.rank,excluded.rank),native_score=COALESCE(excluded.native_score,discovery_hits.native_score),hit_metadata_json=excluded.hit_metadata_json,discovered_at=MAX(discovery_hits.discovered_at,excluded.discovered_at)''')
  if has_table(out,alias,'candidate_queue'):
   out.execute(f'''INSERT INTO candidate_queue(source,external_id,gate_version,gate_label,gate_score,gate_evidence_json,best_rank,query_count,status,updated_at)
    SELECT source,external_id,gate_version,gate_label,gate_score,gate_evidence_json,best_rank,query_count,status,updated_at FROM {alias}.candidate_queue WHERE 1
    ON CONFLICT(source,external_id,gate_version) DO UPDATE SET gate_label=excluded.gate_label,gate_score=MAX(candidate_queue.gate_score,excluded.gate_score),gate_evidence_json=excluded.gate_evidence_json,best_rank=MIN(candidate_queue.best_rank,excluded.best_rank),query_count=MAX(candidate_queue.query_count,excluded.query_count),status=CASE WHEN candidate_queue.status='resolved' OR excluded.status='resolved' THEN 'resolved' ELSE excluded.status END,updated_at=MAX(candidate_queue.updated_at,excluded.updated_at)''')
  if has_table(out,alias,'fetch_receipts'):
   out.execute(f'''INSERT INTO fetch_receipts(source,external_id,resolver,target,status,content_sha256,detail_json,fetched_at)
    SELECT source,external_id,resolver,target,status,content_sha256,detail_json,fetched_at FROM {alias}.fetch_receipts''')
  out.commit();out.execute(f'DETACH DATABASE {alias}')
 print('sources',out.execute('SELECT source,COUNT(*) FROM occurrences GROUP BY source ORDER BY source').fetchall())
 print('occurrences',out.execute('SELECT COUNT(*) FROM occurrences').fetchone()[0],'contents',out.execute('SELECT COUNT(*) FROM contents').fetchone()[0],'hits',out.execute('SELECT COUNT(*) FROM discovery_hits').fetchone()[0]);out.close()
if __name__=='__main__':main()
