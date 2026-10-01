import {GRADES,integer} from './engine.js';
export const FIELDS=['id','code','name','province','district','grade','ownership','students','year','source_url','source_date','observed_at','boarding','district_fallback','pdr','pdr_year','pdr_source_url','apprentices','group_id','group_students','group_complete','group_recipient','population','notes'];
const nums=['students','pdr','apprentices','group_students','population'];const bools=['boarding','district_fallback','group_complete','group_recipient'];
const allowed=new Set([...FIELDS,'status','evidence','all_teachers','classrooms']);
export function safeUrl(s){if(!s)return '';try{const u=new URL(s);return ['https:','http:'].includes(u.protocol)?u.href:'';}catch{return '';}}
export function parseCSV(text){
 text=text.replace(/^\uFEFF/,'');const delimiter=text.split(/\r?\n/,1)[0].includes(';')?';':',';let rows=[],row=[],field='',quoted=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else if(!quoted&&field!=='')throw new Error('CSV tırnak yapısı hatalı.');else quoted=!quoted;}else if(!quoted&&c===delimiter){row.push(field);field='';}else if(!quoted&&(c==='\n'||c==='\r')){if(c==='\r'&&text[i+1]==='\n')i++;row.push(field);if(row.some(x=>x!==''))rows.push(row);row=[];field='';}else field+=c;}
 if(quoted)throw new Error('CSV içinde kapanmamış tırnak var.');row.push(field);if(row.some(x=>x!==''))rows.push(row);
 const headers=rows.shift()?.map(x=>x.trim());if(!headers?.length)throw new Error('Dosya boş.');if(new Set(headers).size!==headers.length)throw new Error('Yinelenen sütun adı.');
 const unknown=headers.filter(x=>!allowed.has(x));if(unknown.length)throw new Error('Tanınmayan sütunlar: '+unknown.join(', '));
 return rows.map((r,i)=>{if(r.length!==headers.length)throw new Error(`Satır ${i+2}: sütun sayısı başlıkla eşleşmiyor.`);return Object.fromEntries(headers.map((h,j)=>[h,r[j]]));});
}
export function validateRows(input){
 if(!Array.isArray(input)||input.length===0)throw new Error('En az bir okul kaydı gerekli.');if(input.length>50000)throw new Error('En fazla 50.000 kayıt içe aktarılabilir.');
 const ids=new Set(),codes=new Set();const output=input.map((raw,i)=>{
 if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new Error(`Kayıt ${i+1}: nesne olmalı.`);
 for(const k of Object.keys(raw))if(!allowed.has(k))throw new Error(`Kayıt ${i+1}: tanınmayan alan ${k}.`);
 const r={};for(const k of FIELDS)r[k]=raw[k]??null;
 for(const k of ['id','name','province','district','grade','ownership']){if(typeof r[k]!=='string'||!r[k].trim())throw new Error(`Kayıt ${i+1}: ${k} gerekli.`);r[k]=r[k].trim();}
 if(!Object.hasOwn(GRADES,r.grade))throw new Error(`Kayıt ${i+1}: grade tanınmıyor.`);if(!['public','private'].includes(r.ownership))throw new Error(`Kayıt ${i+1}: ownership public/private olmalı.`);
 for(const k of nums){if(r[k]===''||r[k]===null)r[k]=null;else {if(!['number','string'].includes(typeof r[k]))throw new Error(`Kayıt ${i+1}: ${k} sayı olmalı.`);if(typeof r[k]==='string'&&!/^\d+$/.test(r[k]))throw new Error(`Kayıt ${i+1}: ${k} negatif olmayan tam sayı olmalı.`);r[k]=Number(r[k]);if(!integer(r[k]))throw new Error(`Kayıt ${i+1}: ${k} geçersiz.`);}}
 for(const k of bools){if(r[k]===''||r[k]===null)r[k]=null;else if(r[k]==='true')r[k]=true;else if(r[k]==='false')r[k]=false;else if(typeof r[k]!=='boolean')throw new Error(`Kayıt ${i+1}: ${k} true/false/boş olmalı.`);}
 for(const k of ['year','pdr_year']){if(!r[k])r[k]=null;else if(!/^\d{4}-\d{4}$/.test(r[k])||Number(r[k].slice(5))!==Number(r[k].slice(0,4))+1)throw new Error(`Kayıt ${i+1}: ${k} 2025-2026 gibi olmalı.`);}
 for(const k of ['source_date','observed_at']){if(!r[k])r[k]=null;else if(!/^\d{4}-\d{2}-\d{2}$/.test(r[k])||Number.isNaN(Date.parse(r[k]))||new Date(r[k]).toISOString().slice(0,10)!==r[k])throw new Error(`Kayıt ${i+1}: ${k} YYYY-MM-DD olmalı.`);}
 for(const k of ['source_url','pdr_source_url']){if(r[k]&&!safeUrl(r[k]))throw new Error(`Kayıt ${i+1}: ${k} http/https bağlantısı olmalı.`);r[k]=r[k]||null;}
 if(!r.source_url)throw new Error(`Kayıt ${i+1}: öğrenci verisi için source_url gerekli.`);
 const key=r.id+'|'+(r.year||'unknown');if(ids.has(key))throw new Error(`Kayıt ${i+1}: aynı okul ve eğitim yılı iki kez girilmiş.`);ids.add(key);if(r.code){const codeKey=r.code+'|'+(r.year||'unknown');if(codes.has(codeKey))throw new Error(`Kayıt ${i+1}: aynı kurum kodu ve yıl tekrarlanıyor.`);codes.add(codeKey);}
 if(r.group_complete===true&&(!r.group_id||!integer(r.group_students)||typeof r.group_recipient!=='boolean'))throw new Error(`Kayıt ${i+1}: özel eğitim grubu eksik.`);
 r.status='user_import';r.evidence=typeof raw.evidence==='string'?raw.evidence:null;r.notes=typeof r.notes==='string'?r.notes:null;
 return r;
 });
 const groups=new Map();for(const r of output)if(r.grade==='ozel_egitim' && r.group_complete===true){const key=r.group_id+'|'+(r.year||'unknown');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r);}
 for(const members of groups.values()){
  const total=members[0].group_students,recipients=members.filter(r=>r.group_recipient);
  if(recipients.length!==1||members.some(r=>r.group_students!==total)||members.reduce((s,r)=>s+(r.students??0),0)!==total||members.some(r=>r.students===null))throw new Error('Özel eğitim grubu eksik veya tutarsız: tüm üyeler, aynı toplam ve tek norm alıcısı gerekli.');
  if(recipients[0].students!==Math.max(...members.map(r=>r.students)))throw new Error('Özel eğitim norm alıcısı öğrenci sayısı en yüksek kurum olmalı.');
 }
 return output;
}
export function csv(rows,fields=FIELDS){return '\uFEFF'+[fields,...rows.map(r=>fields.map(k=>r[k]??''))].map(row=>row.map(v=>{let s=String(v);if(/^[=+@\-\t\r]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';}).join(',')).join('\r\n');}
