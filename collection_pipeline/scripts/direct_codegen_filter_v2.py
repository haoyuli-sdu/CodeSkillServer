#!/usr/bin/env python3
"""Direct code-generation Skill classifier used by the release workflow.

Confirmed and probable direct code-generation Skills are separated, while
review/debugging/advice Skills do not become direct generation merely because
they discuss code.
"""
from __future__ import annotations
import argparse,csv,json,re,sqlite3
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
try:
    from . import targeted_codegen_crawler as targeted
except ImportError:  # Supports direct execution: python scripts/direct_codegen_filter_v2.py
    import targeted_codegen_crawler as targeted

VERSION="direct-codegen-filter-v2.0"
FENCE=re.compile(r"```.*?```|~~~.*?~~~",re.S)
URL=re.compile(r"https?://\S+")
WS=re.compile(r"\s+")
CLAUSE=r"[^,;:.!?。；，！？\n]{0,120}"
NON_CODE=targeted.NON_CODE
NEGATION=targeted.NEGATION
SUPPORT_ONLY=targeted.SUPPORT_ONLY

RULES={
 "function_method_algorithm":[
  rf"\b(?:implement|write|generate|complete|synthesize|fill in|solve)\b{CLAUSE}\b(?:functions?|methods?|function bod(?:y|ies)|method bod(?:y|ies)|algorithms?|data structures?|programming problems?)\b",
  rf"\b(?:functions?|methods?|algorithms?)\b{CLAUSE}\b(?:implementation|code generation|synthesis|completion)\b",
  r"\b(?:docstring[- ]to[- ]code|signature[- ]to[- ]implementation|function synthesis|function[- ]level code generation)\b",
  r"(?:实现|生成|编写|补全)(?:函数|方法|函数体|方法体|算法|数据结构)|(?:函数|方法|算法)(?:实现|代码生成)"],
 "class_module_model":[
  rf"\b(?:generate|create|implement|write|synthesize)\b{CLAUSE}\b(?:classes?|modules?|data models?|domain models?|entity classes?|controllers?|service classes?|repositories|serializers?|validators?|pydantic models?|dataclasses?|typescript types?)\b",
  r"\b(?:schema|json schema)\s*(?:to|into|2)\s*[^,;:.!?。；，！？\n]{0,40}\b(?:classes?|models?|types?|code)\b",
  r"(?:生成|创建|实现|编写)(?:类(?:代码|实现|定义)?(?!似|型|别)|模块(?:代码|实现)?|软件包|程序包|数据模型|领域模型|实体类|控制器|服务类|仓储层|序列化器|验证器|类型定义)"],
 "full_app_scaffold":[
  rf"\b(?:scaffold|generate|create|build)\b{CLAUSE}\b(?:full[- ]stack applications?|web applications?|mobile applications?|starter projects?|project structure|microservices?|serverless applications?|production[- ]ready applications?|application boilerplate)\b",
  r"\b(?:application|project|feature) (?:scaffolder|generator)\b",
  r"(?:生成|创建|构建|搭建|脚手架)(?:全栈应用|Web应用|移动应用|软件项目|代码项目|项目结构|微服务|无服务器应用|应用样板代码)"],
 "frontend_ui":[
  rf"\b(?:generate|implement|build|create|translate|convert)\b{CLAUSE}\b(?:react components?|vue components?|angular components?|frontend code|ui code|web pages?|responsive pages?|next\.?js applications?|html css javascript|state management code|frontend routes?)\b",
  r"\b(?:turn\s+)?(?:figma|design|screenshot)[^,;:.!?。；，！？\n]{0,30}(?:to|into|2)\s*(?:react|vue|frontend|html|code)\b",
  r"(?:生成|实现|创建|还原)(?:前端代码|React组件|Vue组件|Angular组件|页面代码|响应式页面|UI代码|状态管理代码)|(?:设计稿|截图)转(?:前端|React|Vue|代码)"],
 "backend_api":[
  rf"\b(?:generate|implement|write|build|create)\b{CLAUSE}\b(?:backend code|rest apis?|api endpoints?|graphql resolvers?|request handlers?|webhook handlers?|server routes?|middleware|service layer|database access layer|serverless functions?|edge functions?|event handlers?|authentication code|authorization code)\b",
  r"(?:生成|实现|编写|创建)(?:后端代码|REST接口|API接口|接口处理器|GraphQL解析器|请求处理器|Webhook处理器|服务端路由|中间件|服务层|数据库访问层|云函数|边缘函数|事件处理器|认证代码|授权代码)"],
 "cli_sdk_client_plugin":[
  r"\b(?:generate|create|build|scaffold|implement|write)\s+(?:(?:a|an|the|new|complete|production[- ]ready|ship[- ]ready|typed|official|python|typescript|javascript|java|go|rust|php|c#|c\+\+)\s+){0,5}(?:cli|command[- ]line (?:application|tool)|sdk|api clients?|typed clients?|plugin(?: code| project)?|extension(?: code| project)?|mcp servers?|model context protocol servers?|language bindings?|wrapper libraries?|integration adapters?)\b",
  r"\b(?:openapi|protobuf|grpc|graphql)\b[^,;:.!?。；，！？\n]{0,80}\b(?:client|sdk|server stub|code generation|codegen|bindings?)\b",
  r"(?:生成|创建|实现|构建)(?:CLI工具|命令行工具|SDK|API客户端|类型化客户端|插件|扩展程序|MCP服务器|语言绑定|封装库|集成适配器)"],
 "crud_database":[
  rf"\b(?:generate|create|write|implement|scaffold)\b{CLAUSE}\b(?:crud(?: code| application)?|sql quer(?:y|ies)|database schemas?|database migrations?|schema migrations?|orm models?|repository code|stored procedures?|seed code|query builder code|prisma schemas?|sqlalchemy models?)\b",
  r"\b(?:natural language|text)\s*(?:to|into|2)\s*sql\b",
  r"(?:生成|创建|编写|实现)(?:CRUD|增删改查代码|SQL查询|数据库模式|数据库迁移|ORM模型|仓储层代码|存储过程|种子数据代码|查询构建代码)"],
 "test_code":[
  rf"\b(?:generate|write|create|implement|add|synthesize)\b{CLAUSE}\b(?:unit tests?|integration tests?|end[- ]to[- ]end tests?|e2e tests?|test cases?|test code|pytest tests?|jest tests?|property[- ]based tests?|regression tests?|api tests?|test fixtures?|mocks?|stubs?|contract tests?|fuzz tests?)\b",
  r"(?:生成|编写|创建|实现)(?:单元测试|集成测试|端到端测试|测试代码|测试用例|回归测试|接口测试|测试夹具|Mock|桩代码|契约测试|模糊测试)"],
 "infra_config":[
  rf"\b(?:generate|write|create|build)\b{CLAUSE}\b(?:terraform(?: code)?|infrastructure as code|kubernetes manifests?|dockerfiles?|docker compose|github actions workflows?|ci/?cd pipelines?|deployment manifests?|helm charts?|ansible playbooks?|cloud configuration|build configuration|nginx configuration|policy as code)\b",
  r"(?:生成|编写|创建)(?:Terraform代码|基础设施代码|Kubernetes配置|Dockerfile|Docker Compose配置|GitHub Actions|CI流水线|部署清单|Helm Chart|Ansible脚本|云配置|构建配置|Nginx配置|策略代码)"],
 "code_conversion_migration":[
  rf"\b(?:convert|translate|migrate|port|rewrite|modernize|upgrade)\b{CLAUSE}\b(?:code|source code|implementation|codebase|framework code|legacy code)\b",
  r"\b(?:javascript to typescript|python to rust|class component to hooks)\b",
  r"(?:转换|迁移|翻译|移植|重写|现代化|升级)(?:代码|源码|实现|代码库|框架代码|旧代码)"],
 "generator_metaprogramming":[
  r"\b(?:codegen|code generator|source generator|parser generator|lexer generator|binding generator|client generator|orm code generator|template[- ]based code generation|schema[- ]driven code generation|model[- ]driven code generation|ast code generation|compiler code generation|protobuf code generation|grpc code generation|graphql code generation|openapi codegen)\b",
  r"(?:代码生成器|源码生成器|解析器生成器|词法分析器生成器|绑定生成器|客户端生成器|模板驱动代码生成|模式驱动代码生成|模型驱动代码生成)"],
 "specialized_executable":[
  rf"\b(?:generate|write|create|implement)\b{CLAUSE}\b(?:regular expressions?|parser code|validation code|serialization code|deserialization code|mapping code|dependency injection code|configuration parsers?|data transformation code|etl pipelines?|spark jobs?|airflow dags?|automation scripts?|browser automation code|web scraping code|smart contracts?|shader code|firmware code|hardware description code)\b",
  r"(?:生成|编写|创建|实现)(?:正则表达式|解析器代码|验证代码|序列化代码|反序列化代码|映射代码|依赖注入代码|数据转换代码|ETL代码|自动化脚本|浏览器自动化代码|爬虫代码|智能合约|着色器代码|固件代码)"],
 "general_explicit":targeted.DIRECT_PHRASES,
}
GUIDANCE_CONTEXT=re.compile(r"\b(?:use when|guidance|guide|best practices?|documentation|reference|library)\b[^,;:.!?。；，！？\n]{0,100}\b(?:writing|building|implementing|creating|developing)\b|(?:用于|适用于|指南|最佳实践|参考|文档)[^。；，！？\n]{0,80}(?:编写|构建|实现|创建|开发)",re.I)
STRONG_OUTPUT=re.compile(r"\b(?:generat(?:e|es|ed|ing)|codegen|scaffold(?:s|ed|ing)?|synthesi[sz](?:e|es|ed|ing)|convert(?:s|ed|ing)?|translat(?:e|es|ed|ing)|migrat(?:e|es|ed|ing)|port(?:s|ed|ing)|rewrite(?:s|n|ing)?|creat(?:es|ed|ing) a new|writes? (?:the |a |an )?(?:complete|full|production|runnable|source))\b|(?:生成|自动生成|代码生成|脚手架|转换|迁移|翻译|移植|重写)",re.I)
def strip_market_title(text):
 return re.split(r"\s*(?:⊕|\||�{1,4}|—)\s*",str(text or ""),maxsplit=1)[0]
def evidence_is_strong(items,declared):
 if declared.count("�")>=3:return False
 subtypes={x.get("subtype","") for x in items}
 matches=" ".join(x.get("match","") for x in items)
 if subtypes=={"general_explicit"} and re.fullmatch(r"(?i)\s*(?:code generation|codegen|generated code)\s*",matches):return False
 if subtypes=={"test_code"} and re.search(r"(?i)\btest cases?\b",matches) and not re.search(r"(?i)\b(?:unit|integration|e2e|end[- ]to[- ]end|pytest|jest|test code|fixture|mock|stub|contract|fuzz)\b",matches):return False
 if GUIDANCE_CONTEXT.search(declared) and not re.search(r"(?i)\b(?:generat(?:e|es|ed|ing)|codegen|scaffold|synthesize|creates? a new)\b|(?:生成|代码生成|脚手架)",matches):return False
 if STRONG_OUTPUT.search(declared):return True
 return any(re.search(r"\b(?:implement|write|build|create|complete|fill)\b|(?:实现|编写|创建|构建|补全)",x.get("match",""),re.I) for x in items)
GENERIC_CODING_ASSISTANT=re.compile(r"\b(?:coding assistant|software engineering agent|developer assistant|helps? (?:you )?(?:write|build) code|assist(?:s|ing)? with coding|pair programmer)\b|(?:编程助手|软件工程智能体|帮助编写代码|辅助开发)",re.I)

def clean(text):
 text=FENCE.sub(" ",str(text or ""));text=URL.sub(" ",text);return WS.sub(" ",text).strip()
def parse_frontmatter(raw):
 try:
  data=json.loads(raw or "{}");return data if isinstance(data,dict) else {}
 except Exception:return {}
def matches_rules(text):
 evidence=[]
 for subtype,patterns in RULES.items():
  for pattern in patterns:
   found=re.search(pattern,text,re.I)
   if found:evidence.append({"subtype":subtype,"match":found.group(0)[:240]});break
 return evidence
def choose_subtype(evidence):
 priority=["test_code","function_method_algorithm","class_module_model","full_app_scaffold","frontend_ui","backend_api","cli_sdk_client_plugin","crud_database","infra_config","code_conversion_migration","generator_metaprogramming","specialized_executable","general_explicit"]
 names={item["subtype"] for item in evidence};return next((name for name in priority if name in names),"unknown")
def query_provenance(db,source,external_id):
 try:rows=db.execute("SELECT query_id,query_text,query_group,query_tier,MIN(rank) FROM discovery_hits WHERE source=? AND external_id=? GROUP BY query_id,query_text,query_group,query_tier ORDER BY MIN(rank)",(source,external_id)).fetchall()
 except sqlite3.OperationalError:return []
 return [{"query_id":r[0],"query_text":r[1],"query_group":r[2],"query_tier":r[3],"rank":r[4]} for r in rows]
def result(label,subtype,confidence,evidence,declared,provenance):
 return {"classifier_version":VERSION,"label":label,"subtype":subtype,"confidence":confidence,"evidence":evidence,"declared_text":declared[:1800],"query_provenance":provenance}
def classify(title,description,frontmatter_raw,body,content_available,provenance=None):
 provenance=provenance or [];fm=parse_frontmatter(frontmatter_raw)
 declared=clean(" ".join([strip_market_title(title),description or "",str(fm.get("name") or ""),str(fm.get("description") or "")]))
 intro=clean(body or "")[:9000];declared_ev=matches_rules(declared);intro_ev=matches_rules(intro)
 actions=[w for w in targeted.ACTION_WORDS if w.casefold() in declared.casefold()];artifacts=[w for w in targeted.ARTIFACT_WORDS if w.casefold() in declared.casefold()]
 intro_actions=[w for w in targeted.ACTION_WORDS if w.casefold() in intro.casefold()];intro_artifacts=[w for w in targeted.ARTIFACT_WORDS if w.casefold() in intro.casefold()]
 negation=NEGATION.search(declared);non_code=NON_CODE.search(declared);support=SUPPORT_ONLY.search(declared);generic=GENERIC_CODING_ASSISTANT.search(declared);evidence=[]
 if negation:return result("not_direct","negated_codegen",0.98,[{"field":"declared","kind":"negation","match":negation.group(0)}],declared,provenance)
 if non_code:
  return result("not_direct","non_code_output",0.98,[{"field":"declared","kind":"non_code_output","match":non_code.group(0)}],declared,provenance)
 if declared_ev:
  evidence.extend({"field":"declared",**item} for item in declared_ev)
  if support:evidence.append({"field":"declared","kind":"support_also_present","match":support.group(0)})
  strong=evidence_is_strong(declared_ev,declared)
  if strong and content_available:return result("confirmed_direct",choose_subtype(declared_ev),0.96,evidence,declared,provenance)
  return result("probable_direct",choose_subtype(declared_ev),0.78 if not content_available else 0.72,evidence,declared,provenance)
 if actions and artifacts:
  evidence=[{"field":"declared","kind":"weak_action_artifact","actions":actions[:8],"artifacts":artifacts[:10]}]
  if provenance:return result("manual_review","weak_action_artifact",0.48,evidence,declared,provenance)
  return result("not_direct","weak_action_artifact_only",0.76,evidence,declared,provenance)
 if support:return result("not_direct","codegen_support_only",0.94,[{"field":"declared","kind":"support_only","match":support.group(0)}],declared,provenance)
 if generic:
  evidence=[{"field":"declared","kind":"generic_coding_assistant","match":generic.group(0)}]
  if intro_ev:
   evidence.extend({"field":"intro",**item} for item in intro_ev);return result("probable_direct",choose_subtype(intro_ev),0.76,evidence,declared,provenance)
  return result("manual_review","generic_coding_assistant",0.55,evidence,declared,provenance)
 if intro_ev:
  evidence=[{"field":"intro",**item} for item in intro_ev]
  if len(intro_ev)>=2 or (intro_actions and intro_artifacts and targeted.SOFTWARE_DOMAIN.search(intro)):return result("probable_direct",choose_subtype(intro_ev),0.75,evidence,declared,provenance)
  return result("manual_review","body_only_direct_evidence",0.58,evidence,declared,provenance)
 if provenance:
  evidence=[{"field":"search","kind":"targeted_search_only","queries":[x["query_text"] for x in provenance[:8]]}]
  return result("insufficient_metadata" if not content_available else "manual_review","search_hit_without_content" if not content_available else "search_hit_without_direct_evidence",0.35 if not content_available else 0.40,evidence,declared,provenance)
 if len(declared)<20 and not intro:return result("insufficient_metadata","insufficient_metadata",0.25,[],declared,provenance)
 return result("not_direct","no_direct_generation_evidence",0.84,[],declared,provenance)
def write_csv(path,rows):
 cols=["occurrence_id","source","external_id","page_url","title","description","repo_url","path","content_sha256","classifier_version","label","subtype","confidence","query_count","best_query_rank","query_texts","evidence","declared_text"]
 with path.open("w",encoding="utf-8-sig",newline="") as h:
  w=csv.writer(h);w.writerow(cols)
  for r in rows:w.writerow([json.dumps(r.get(c),ensure_ascii=False) if c=="evidence" else r.get(c,"") for c in cols])
def main():
 p=argparse.ArgumentParser(description="Direct code-generation Skill filter v2");p.add_argument("--db",required=True);p.add_argument("--out-dir",default="data/direct_codegen_filter_v2");p.add_argument("--dedup-content",action=argparse.BooleanOptionalAction,default=True);a=p.parse_args();out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(Path(a.db).resolve().as_uri()+"?mode=ro&immutable=1",uri=True);rows=db.execute("SELECT o.occurrence_id,o.source,o.external_id,o.page_url,o.title,o.description,o.repo_url,o.path,o.content_sha256,COALESCE(c.frontmatter_json,''),COALESCE(c.body,'') FROM occurrences o LEFT JOIN contents c ON o.content_sha256=c.content_sha256 ORDER BY o.occurrence_id").fetchall();results=[];duplicates=[];seen=set()
 for row in rows:
  oid,source,eid,page,title,desc,repo,path,ch,fm,body=row;key=ch or f"{source}:{eid}"
  if a.dedup_content and key in seen:duplicates.append({"occurrence_id":oid,"source":source,"external_id":eid,"content_sha256":ch});continue
  seen.add(key);prov=query_provenance(db,source,eid);classified=classify(title,desc,fm,body,bool(ch),prov)
  results.append({"occurrence_id":oid,"source":source,"external_id":eid,"page_url":page,"title":title,"description":desc,"repo_url":repo,"path":path,"content_sha256":ch,"query_count":len(prov),"best_query_rank":min((x["rank"] for x in prov if x.get("rank") is not None),default=""),"query_texts":" | ".join(x["query_text"] for x in prov[:30]),**classified})
 confirmed=[r for r in results if r["label"]=="confirmed_direct"];probable=[r for r in results if r["label"]=="probable_direct"];manual=[r for r in results if r["label"] in {"manual_review","insufficient_metadata"}];not_direct=[r for r in results if r["label"]=="not_direct"];combined=confirmed+probable
 write_csv(out/"00_all_direct_codegen_candidates.csv",combined);write_csv(out/"01_confirmed_direct_codegen.csv",confirmed);write_csv(out/"02_probable_direct_codegen.csv",probable);write_csv(out/"03_manual_review.csv",manual);write_csv(out/"04_not_direct.csv",not_direct)
 with (out/"duplicates.jsonl").open("w",encoding="utf-8") as h:
  for x in duplicates:h.write(json.dumps(x,ensure_ascii=False)+"\n")
 summary={"classifier_version":VERSION,"generated_at":datetime.now(timezone.utc).isoformat(),"input_occurrences":len(rows),"unique_records_classified":len(results),"duplicates_removed":len(duplicates),"label_counts":dict(Counter(r["label"] for r in results)),"confirmed_subtypes":dict(Counter(r["subtype"] for r in confirmed)),"probable_subtypes":dict(Counter(r["subtype"] for r in probable)),"direct_candidates_total":len(combined)}
 (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()










