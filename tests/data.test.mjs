import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateRows} from '../dist/import.js';
test('pilot records preserve unknown years and staff',async()=>{const rows=JSON.parse(await readFile(new URL('../dist/data/schools.json',import.meta.url)));assert.equal(validateRows(rows).length,28);for(const r of rows){assert.equal(r.year,null);assert.equal(r.pdr,null);}});
test('historical vacancies reconcile without becoming current province totals',async()=>{const a=JSON.parse(await readFile(new URL('../dist/data/historical-norms.json',import.meta.url)));assert.equal(a.current_data,false);assert.equal(a.academic_year,null);assert.equal(a.rows.length,5);for(const r of a.rows)assert.equal(r.approved_norm-r.staff,r.reported_vacancy);assert.equal(a.rows.reduce((s,r)=>s+r.reported_vacancy,0),5);});
