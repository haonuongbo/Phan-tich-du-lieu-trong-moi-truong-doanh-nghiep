// Kiểm tra logic dashboard offline bằng Node, không cần thư viện trình duyệt.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, '../BaoCao/dashboard.html'), 'utf8');
const payload = html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const nodes = new Map();
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {value: ['quarter','store'].includes(id) ? 'all' : '', innerHTML:'', textContent:'', handlers:{},
    add(option){if(this.value==='')this.value=option.value;}, addEventListener(event,handler){this.handlers[event]=handler;}});
  return nodes.get(id);
}
node('data').textContent=payload;
const context = vm.createContext({document:{getElementById:node,querySelectorAll:()=>[],querySelector:()=>null},
  Option: function(text,value){this.text=text;this.value=String(value);}, console, setTimeout});
vm.runInContext(script, context);
assert.match(node('summary').innerHTML, /146,39 tỷ/);
assert.match(node('summary').innerHTML, /1\.210\.478/);
assert.match(node('summary').innerHTML, /YoY: 25,43%/);
let scenarios=0;
const data=JSON.parse(payload);
for(const year of [...new Set(data.fact.map(r=>r.nam))]) {
node('year').value=String(year);
for(const quarter of ['all','1','2','3','4']) {
  for(const store of ['all',...new Set(data.fact.map(r=>r.store_id))]) {
    node('quarter').value=quarter;node('store').value=store;
    node('quarter').handlers.change();
    const independent=data.fact.filter(r=>r.nam===year&&(quarter==='all'||r.quy===Number(quarter))&&(store==='all'||r.store_id===store));
    const expected=independent.reduce((s,r)=>s+r.DT_tong,0);
    const actual=vm.runInContext('metrics(selected(), Number($("quarter").value) ? 3 : 12).revenue',context);
    assert.equal(actual,expected);
    const menuTotal=vm.runInContext('sum(selectedMenu(),"doanh_thu_phan_bo_VND")',context);
    assert.ok(Math.abs(menuTotal-expected)<.01,'Menu phải đối chiếu cùng bộ lọc với vận hành');
    for(const id of ['menuGroups','menuTable','areaTable','locationTable'])assert.doesNotMatch(node(id).innerHTML,/NaN|Infinity|undefined/);
    assert.doesNotMatch(node('summary').innerHTML,/NaN|Infinity|undefined/);
    assert.match(node('summary').innerHTML,new RegExp((expected/1e9).toLocaleString('vi-VN',{minimumFractionDigits:2,maximumFractionDigits:2})+' tỷ'));
    scenarios++;
  }
}
}
node('reset').handlers.click();
assert.equal(node('store').value,'all');
assert.match(node('summary').innerHTML,/146,39 tỷ/);
assert.doesNotMatch(html,/__PAYLOAD__/);
vm.runInContext("currentPage='menuView'",context);
assert.ok(vm.runInContext("exportData().cols.includes('co_so_du_lieu')",context));
assert.ok(Math.abs(vm.runInContext("sum(exportData().rows,'doanh_thu_phan_bo_VND')",context)-data.fact.filter(r=>r.nam===2025).reduce((s,r)=>s+r.DT_tong,0))<.01);
vm.runInContext("currentPage='areaView'",context);
assert.ok(vm.runInContext("exportData().rows.every(r=>r.khu_vuc_gia_dinh && r.co_so_vi_tri)",context));
console.log(`Dashboard: ${scenarios} filter combinations and reset passed.`);
// Các bộ lọc chung phải giữ cùng phạm vi cho KPI, menu và kỳ so sánh.
const info=Object.fromEntries(data.stores.map(r=>[r.store_id,r]));
let extra=0;
for(const year of [2023,2024,2025])for(const area of ['all',...new Set(data.stores.map(r=>r.khu_vuc_gia_dinh))])for(const position of ['all',...new Set(data.stores.map(r=>r.loai_vi_tri_gia_dinh))]){
 node('year').value=String(year);node('area').value=area;node('position').value=position;
 const expected=data.fact.filter(r=>r.nam===year&&(area==='all'||info[r.store_id].khu_vuc_gia_dinh===area)&&(position==='all'||info[r.store_id].loai_vi_tri_gia_dinh===position)).reduce((s,r)=>s+r.DT_tong,0);
 assert.ok(Math.abs(vm.runInContext("sum(selected(),'DT_tong')",context)-expected)<.01);
 assert.ok(Math.abs(vm.runInContext("sum(selectedMenu(),'doanh_thu_phan_bo_VND')",context)-expected)<.01);
 extra++;
}
node('reset').handlers.click();
node('storeSearch').value='quan 1';node('storeSearch').handlers.input();
assert.ok(vm.runInContext("selected().every(r=>storeInfo[r.store_id].khu_vuc_gia_dinh.includes('Quận 1'))",context));
node('reset').handlers.click();
node('menuGroup').value='Gà';node('menuChannel').value='nen_tang';node('menuSearch').value='ga ran';node('menuSearch').handlers.input();
const expectedMenu=data.menu.filter(r=>r.nam===2025&&r.nhom_mon==='Gà'&&r.kenh==='nen_tang'&&r.menu_id==='M01').reduce((s,r)=>s+r.doanh_thu_phan_bo_VND,0);
assert.ok(Math.abs(vm.runInContext("sum(selectedMenu(),'doanh_thu_phan_bo_VND')",context)-expectedMenu)<.01);
assert.match(node('menuTable').innerHTML,/Gà rán truyền thống/);
assert.doesNotMatch(node('menuTable').innerHTML,/Gà sốt cay/);
assert.match(node('summary').innerHTML,/146,39 tỷ/,'Lọc món không được thay đổi KPI vận hành');
vm.runInContext("currentPage='menuView'",context);
assert.ok(vm.runInContext("exportData().rows.every(r=>r.menu_id==='M01' && r.kenh==='nen_tang')",context));
node('reset').handlers.click();node('storeStatus').value='loss';node('storeSort').value='profit_asc';node('storeStatus').handlers.change();
const lossIds=data.fact.filter(r=>r.nam===2025).reduce((acc,r)=>(acc[r.store_id]=(acc[r.store_id]||0)+r.LN_van_hanh_mo_hinh,acc),{});
const expectedIds=Object.keys(lossIds).filter(id=>lossIds[id]<0).sort((a,b)=>lossIds[a]-lossIds[b]);
assert.deepEqual(Array.from(vm.runInContext("sortRecords(storeRecords(selected(),12),$('storeSort').value).map(r=>r.id)",context)),expectedIds);
vm.runInContext("currentPage='stores'",context);
assert.ok(vm.runInContext('exportData().rows.length',context)===expectedIds.length*12);
node('reset').handlers.click();node('areaSearch').value='thu duc';node('areaSearch').handlers.input();
assert.match(node('areaTable').innerHTML,/Thủ Đức/);assert.doesNotMatch(node('areaTable').innerHTML,/Quận 1/);
vm.runInContext("currentPage='areaView'",context);
assert.ok(vm.runInContext("exportData().rows.every(r=>r.khu_vuc_gia_dinh.includes('Thủ Đức'))",context));
for(const mode of ['revenue_desc','revenue_asc','name_asc','quantity_desc','quantity_asc']){
 const input=[{name:'B',revenue:1,quantity:30},{name:'A',revenue:3,quantity:10},{name:'C',revenue:2,quantity:20}];
 context.sortInput=input;context.sortMode=mode;
 const sorted=Array.from(vm.runInContext('sortRecords(sortInput,sortMode)',context));
 const field=mode.startsWith('quantity')?'quantity':mode.startsWith('name')?'name':'revenue';
 for(let i=1;i<sorted.length;i++)assert.ok(mode.endsWith('desc')?sorted[i-1][field]>=sorted[i][field]:sorted[i-1][field]<=sorted[i][field]);
}
node('storeSearch').value='khongco';node('storeSearch').handlers.input();
assert.match(node('storeTable').innerHTML,/Không có kết quả phù hợp/);
assert.doesNotMatch(node('summary').innerHTML,/NaN|Infinity|undefined/);
node('reset').handlers.click();
for(const id of ['area','position','storeStatus','menuGroup','menuChannel'])assert.equal(node(id).value,'all');
for(const id of ['storeSearch','menuSearch','areaSearch'])assert.equal(node(id).value,'');
node('monthSort').value='date_desc';node('monthSort').handlers.change();
assert.ok(node('monthly').innerHTML.indexOf('2025-12')<node('monthly').innerHTML.indexOf('2025-01'));
console.log(`Additional: ${extra} geography/position cases, search without accents, local filters, sorting, empty results and filtered exports passed.`);
