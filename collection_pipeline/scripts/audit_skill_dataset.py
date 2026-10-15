#!/usr/bin/env python3
import argparse,csv,json,sqlite3
from collections import Counter
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description='Audit crawler data quality and suspicious many-to-one mappings');p.add_argument('--db',required=True);p.add_argument('--out-dir',default='data/audit');p.add_argument('--mapping-threshold',type=int,default=5);a=p.parse_args();out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(a.db);total=db.execute('select count(*) from occurrences').fetchone()[0];contents=db.execute('select count(*) from contents').fetchone()[0]
 source_rows=db.execute("select source,count(*),sum(case when content_sha256 is null then 1 else 0 end) from occurrences group by source order by source").fetchall()
 suspicious=db.execute("""select source,repo_url,path,content_sha256,count(*) n,count(distinct page_url) pages,group_concat(substr(page_url,1,180),' | ') samples from occurrences where content_sha256 is not null group by source,repo_url,path,content_sha256 having count(distinct page_url)>=? order by n desc""",(a.mapping_threshold,)).fetchall()
 hash_groups=db.execute("select content_sha256,count(*) n,count(distinct source) sources from occurrences where content_sha256 is not null group by content_sha256").fetchall()
 statuses=Counter()
 for (raw,) in db.execute('select metadata_json from occurrences'):
  try:statuses[json.loads(raw or '{}').get('resolution_status','not_recorded')]+=1
  except:statuses['invalid_metadata_json']+=1
 with (out/'source_completeness.csv').open('w',encoding='utf-8-sig',newline='') as h:
  w=csv.writer(h);w.writerow(['source','occurrences','missing_content','content_rate'])
  for source,n,missing in source_rows:w.writerow([source,n,missing,round((n-missing)/n,6) if n else 0])
 with (out/'suspicious_many_to_one.csv').open('w',encoding='utf-8-sig',newline='') as h:
  w=csv.writer(h);w.writerow(['source','repo_url','path','content_sha256','occurrences','distinct_pages','sample_pages']);w.writerows(suspicious)
 summary={'occurrences':total,'unique_contents':contents,'sources':{s:{'occurrences':n,'missing_content':m,'content_rate':round((n-m)/n,6) if n else 0} for s,n,m in source_rows},'duplicate_occurrences':sum(n-1 for _,n,_ in hash_groups),'duplicate_hash_groups':sum(n>1 for _,n,_ in hash_groups),'cross_source_hash_groups':sum(ns>1 for _,n,ns in hash_groups),'max_hash_occurrences':max([n for _,n,_ in hash_groups] or [0]),'suspicious_many_to_one_groups':len(suspicious),'resolution_statuses':dict(statuses)}
 (out/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
