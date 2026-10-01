"""Public MEB school pages -> source-backed, grade-grouped JSON. stdlib only."""
import argparse,concurrent.futures,datetime,hashlib,html,json,pathlib,re,urllib.request,urllib.parse

def plain(s):
 s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',s,flags=re.I|re.S)
 return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def grade(name):
 n=name.casefold().replace('i̇','i')
 if 'özel eğitim' in n:return 'ozel_egitim'
 if 'anaokul' in n:return 'anaokulu'
 if 'imam hatip' in n and 'ortaokul' in n:return 'imam_hatip_ortaokulu'
 if 'ortaokul' in n:return 'ortaokul'
 if 'ilkokul' in n:return 'ilkokul'
 if 'lisesi' in n or 'lise' in n:return 'lise'
 if 'mesleki eğitim merkezi' in n:return 'mesem'
 if 'rehberlik ve araştırma' in n:return 'ram'
 return 'diger_kurum'
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'PDRNormResearch/1.0 (public school statistics)'})
 with urllib.request.urlopen(req,timeout=10) as r:
  if not urllib.parse.urlparse(r.url).hostname.endswith('.meb.k12.tr'):raise ValueError('Unexpected host')
  b=r.read(3*1024*1024);s=b.decode('utf-8','replace');return r.url,s,hashlib.sha256(b).hexdigest()
def collect(url,overrides=None):
 host=urllib.parse.urlparse(url).hostname;out={'id':host.split('.')[0],'source_url':url,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'year':None,'source_date':None,'students':None,'grade':None,'attempts':[]}
 if overrides and out['id'] in overrides:
  out.update(overrides[out['id']]);out['grade']=grade(out['name']);out['identity_source']='override'
 for path in ['','tema/okulumuz_hakkinda.php','okulumuz_hakkinda.html']:
  u='https://'+host+'/'+path
  try:
   actual,s,digest=fetch(u);t=plain(s)
   # MEB themes vary. Resolve identity from h1/title/full text, while requiring Bayburt.
   headings=[plain(x) for x in re.findall(r'<h1\\b[^>]*>(.*?)</h1>',s,re.I|re.S)]
   titles=[plain(x) for x in re.findall(r'<title\\b[^>]*>(.*?)</title>',s,re.I|re.S)]
   identity=None
   for candidate in headings+titles+[t[:3000]]:
    m=re.search(r'BAYBURT\\s*/\\s*(MERKEZ|AYDINTEPE|DEMİRÖZÜ)\\s*(?:/|-)\\s*([^|\\n<]{3,180})',candidate,re.I)
    if m:
     identity=m;break
   if identity:
    district=identity[1].strip().replace('i̇','i').title()
    school=re.split(r'\\s{2,}|(?:T\\.?C\\.?\\s*)?M[İI]LL[ÎİI]\\s+EĞ[İI]T[İI]M',identity[2])[0].strip(' -–|')
    out.update(province='Bayburt',district=district,name=school)
   elif not out.get('province') and re.search(r'BAYBURT\\s*/\\s*(MERKEZ|AYDINTEPE|DEMİRÖZÜ)',t,re.I):
    m=re.search(r'BAYBURT\\s*/\\s*(MERKEZ|AYDINTEPE|DEMİRÖZÜ)',t,re.I)
    out.update(province='Bayburt',district=m[1].strip().replace('i̇','i').title())
   if out.get('name'):out['grade']=grade(out['name'])
   hits=list(re.finditer(r'Öğrenci\s*(?:Sayısı)?\s*[:|]?\s*([0-9]+(?:[.,][0-9]{3})*)(?![0-9])',t,re.I))
   # Only labelled statistics; no news/year inference.
   nums=list(dict.fromkeys(int(m[1].replace('.','').replace(',','')) for m in hits))
   out['attempts'].append({'url':actual,'page':path or 'homepage','status':'fetched','sha256':digest,'student_candidates':nums})
   if nums and out.get('province')=='Bayburt' and out.get('name') and (len(nums)==1 or path==''):
    # Homepage KPI is preferred when an older embedded/about value also appears.
    out.update(students=nums[0],source_url=actual,evidence=t[max(0,hits[0].start()-20):hits[0].end()+30],status='source_snapshot_homepage' if path=='' else 'source_snapshot')
    if len(nums)>1:out['alternate_student_candidates']=nums[1:]
    break
   if len(nums)>1:out['status']='conflicting_counts'
  except Exception as e:out['attempts'].append({'url':u,'status':'failed','error':type(e).__name__})
 out.setdefault('status','students_not_found' if out.get('province')=='Bayburt' else 'identity_unverified')
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seeds',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
 seed_path=pathlib.Path(args.seeds);urls=json.loads(seed_path.read_text());root=pathlib.Path(args.output);root.mkdir(parents=True,exist_ok=True)
 override_path=seed_path.with_name('site-overrides.json')
 overrides=json.loads(override_path.read_text()) if override_path.exists() else {}
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for r in pool.map(lambda u:collect(u,overrides),urls):
   results.append(r);(root/'checkpoint.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 grouped={}
 for r in results:grouped.setdefault(r['grade'] or 'siniflandirilamayan',[]).append(r)
 summary={'candidate_sites':len(results),'student_count_found':sum(r['students'] is not None for r in results),'unresolved':sum(r['students'] is None for r in results),'complete_province_inventory':False,'unknown_academic_year':True,'note':'School page snapshots, not a verified common-year province total. Other-province/unverified identities excluded from school totals.','grades':{k:{'records':len(v),'count_found':sum(r['students'] is not None for r in v)} for k,v in grouped.items()}}
 (root/'students-by-grade.json').write_text(json.dumps({'summary':summary,'grades':grouped},ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
