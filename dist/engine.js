export const GRADES = {anaokulu:'Anaokulu',ilkokul:'İlkokul',ortaokul:'Ortaokul',imam_hatip_ortaokulu:'İmam hatip ortaokulu',lise:'Ortaöğretim',mesem:'Mesleki eğitim merkezi',ozel_egitim:'Özel eğitim',ram:'RAM'};
export const BASELINE = Object.freeze({id:'madde21-research-v1',primary:300,other:150,mesem:200,special:25,step:500,specialStep:100});
export function integer(n){return typeof n==='number' && Number.isSafeInteger(n) && n>=0;}
export function validatePolicy(p){for(const k of ['primary','other','mesem','special','step','specialStep']) if(!integer(p[k]) || p[k]<1 || p[k]>1000000) throw new Error('Eşikler 1–1.000.000 arasında tam sayı olmalı.');return p;}
export function norm(row,policy=BASELINE){
 validatePolicy(policy);
 const reasons=[], warnings=[];
 const unavailable=(why)=>({min:null,max:null,reasons:[why],warnings,exact:false});
 if(row.ownership!=='public')return unavailable('Bu model yalnızca MEB resmî kurumlarını kapsar.');
 if(!Object.hasOwn(GRADES,row.grade))return unavailable('Kurum türü tanımlı değil.');
 if(row.grade==='ram'){
  if(!integer(row.population)||row.population<1)return unavailable('RAM görev bölgesi nüfusu gerekli.');
  const excess=Math.max(0,row.population-100000),n=4+Math.floor(excess/50000)+(excess%50000>=25000?1:0);
  return {min:n,max:n,exact:true,reasons:['Madde 21/1: ilk 100.000 nüfus için 4; sonraki her 50.000 için 1; kalan en az 25.000 ise 1.'],warnings};
 }
 if(!integer(row.students))return unavailable('Öğrenci sayısı bilinmiyor.');
 if(!row.year)warnings.push('Öğrenci sayısının eğitim yılı belirtilmemiş; bu sonuç kaynak anlık görüntüsüne aittir.');
 let count=row.students,threshold;
 if(row.grade==='ozel_egitim'){
  if(row.group_complete!==true || !row.group_id || !integer(row.group_students) || typeof row.group_recipient!=='boolean')return unavailable('Özel eğitim için aynı bina/bahçe grubu, toplam öğrenci ve normun verileceği kurum doğrulanmalı.');
  if(!row.group_recipient)return {min:0,max:0,exact:true,reasons:['Ortak özel eğitim grubu normu başka kurumda sayılır; çift sayım yapılmadı.'],warnings};
  count=row.group_students;threshold=policy.special;
 } else if(row.grade==='mesem'){
  if(!integer(row.apprentices))return unavailable('MESEM için çırak/kursiyer sayısı ayrıca doğrulanmalı; genel öğrenci sayısı yerine kullanılmaz.');
  count=row.apprentices;threshold=policy.mesem;
 } else threshold=row.grade==='ilkokul'?policy.primary:policy.other;
 let base=count>=threshold?1:0,min=base,max=base;
 reasons.push(`${count} ${row.grade==='mesem'?'çırak/kursiyer':'öğrenci'}; ilk norm eşiği ${threshold}: ${base} temel norm.`);
 if(base===0){
  if(row.boarding===true){min=1;max=1;reasons.push('Madde 21/2-ç: yatılı/pansiyonlu kuruma öğrenci sayısından bağımsız 1 temel norm.');}
  else if(row.boarding!==false){max=1;warnings.push('Yatılı/pansiyon durumu bilinmediğinden temel norm 0–1 aralığında.');}
  const eligible=['ilkokul','ortaokul','imam_hatip_ortaokulu','lise'].includes(row.grade);
  if(eligible && min===0 && row.district_fallback===true){min=1;max=1;reasons.push('Madde 21/2-d: ilçe merkezi istisnası kaynakla doğrulanmış.');}
  else if(eligible && min===0 && row.district_fallback!==false){max=1;warnings.push('İlçe merkezi istisnası tüm ilgili kurumlar üzerinden doğrulanmalı.');}
 }
 const step=row.grade==='ozel_egitim'?policy.specialStep:policy.step,extra=Math.floor(count/step);
 min+=extra;max+=extra;reasons.push(`Her ${step} ${row.grade==='mesem'?'çırak':'öğrenci'} ve katında ilave norm: ${extra}. Temel normla toplanır.`);
 return {min,max,exact:min===max,reasons,warnings};
}
export function gap(row,result){
 if(!integer(row.pdr)||result.min===null)return {min:null,max:null};
 // Öğretmen ve öğrenci sayıları aynı eğitim yılına ait olmalıdır.
 if(!row.year || row.pdr_year!==row.year || !row.pdr_source_url)return {min:null,max:null};
 return {min:Math.max(0,result.min-row.pdr),max:Math.max(0,result.max-row.pdr)};
}
export function compare(row,policy){
 const current=norm(row),scenario=norm(row,policy);let delta=null;
 if(current.min!==null && scenario.min!==null){
  const values=[];
  for(const boarding of typeof row.boarding==='boolean'?[row.boarding]:[false,true])
   for(const district_fallback of typeof row.district_fallback==='boolean'?[row.district_fallback]:[false,true]){
    const complete={...row,boarding,district_fallback};values.push(norm(complete,policy).min-norm(complete).min);
   }
  delta={min:Math.min(...values),max:Math.max(...values)};
 }
 return {current,scenario,currentGap:gap(row,current),scenarioGap:gap(row,scenario),delta};
}
export function summarize(rows,policy=BASELINE){
 const out={records:rows.length,computed:0,uncomputed:0,exact:0,normMin:0,normMax:0,scenarioMin:0,scenarioMax:0,gapKnown:0,gapMin:0,gapMax:0,scenarioGapMin:0,scenarioGapMax:0,deltaMin:0,deltaMax:0,unknownYear:0};
 for(const row of rows){if(!row.year)out.unknownYear++;const r=compare(row,policy);if(r.current.min===null||r.scenario.min===null){out.uncomputed++;continue;}out.computed++;if(r.current.exact)out.exact++;out.normMin+=r.current.min;out.normMax+=r.current.max;out.scenarioMin+=r.scenario.min;out.scenarioMax+=r.scenario.max;out.deltaMin+=r.delta.min;out.deltaMax+=r.delta.max;if(r.currentGap.min!==null&&r.scenarioGap.min!==null){out.gapKnown++;out.gapMin+=r.currentGap.min;out.gapMax+=r.currentGap.max;out.scenarioGapMin+=r.scenarioGap.min;out.scenarioGapMax+=r.scenarioGap.max;}}
 return out;
}
export const range = (r) => r?.min===null||r?.min===undefined?'Bilinmiyor':r.min===r.max?String(r.min):`${r.min}–${r.max}`;
