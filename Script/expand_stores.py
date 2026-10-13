"""Mở rộng kịch bản từ 20 lên 50 cửa hàng; giữ nguyên các dòng nguồn cũ."""
import json
import numpy as np
import pandas as pd
from pipeline import ROOT, STORE_FILE, CSV_PRIMARY, load_clean, derive

DISTRICTS = ['Quận 2','Quận 4','Quận 6','Quận 8','Quận 9','Quận 11','Quận 12','Tân Phú','Phú Nhuận','Bình Tân']

def expand(project=ROOT):
    raw=project/'DataGoc'
    stores,fact=load_clean(raw,{})
    if len(stores)==50:
        print('Nguồn đã có 50 cửa hàng; không thêm dòng trùng.')
        return
    if len(stores)!=20:
        raise ValueError('Mở rộng này yêu cầu bộ nguồn gốc có đúng 20 cửa hàng.')
    rng=np.random.default_rng(20261007)
    config_path=project/'Script/gia_dinh_menu_khu_vuc.json'
    config=json.loads(config_path.read_text(encoding='utf-8'))
    types=list(config['trong_so_theo_vi_tri'])
    new_stores,new_facts=[],[]
    for i in range(30):
        sid=f'SIM{i+21:03d}'
        # Luân phiên địa bàn để các đợt mở cửa không tập trung vào một quận.
        area='Khu vực '+DISTRICTS[i%10]
        kind=types[(i//10+i)%len(types)]
        config['vi_tri'][sid]=[area,kind]
        opened=pd.Timestamp(year=2023 if i<18 else 2024 if i<26 else 2025,month=1,day=1)
        donor=stores.iloc[i%12].copy()
        demand=float(rng.uniform(.72,1.22))
        overhead=float(rng.uniform(.78,1.18))
        donor['store_id']=sid;donor['ngay_mo']=opened
        donor['don_co_so']=int(round(donor.don_co_so*demand))
        donor['AOV_co_so_VND']=int(round(donor.AOV_co_so_VND*rng.uniform(.92,1.06)))
        for cost in ['luong_co_so_VND','thue_co_so_VND','khac_co_so_VND','khau_hao_VND']:
            donor[cost]=int(round(donor[cost]*overhead))
        donor['ty_le_gia_von']=float(rng.uniform(.40,.48))
        donor['ty_le_nen_tang']=float(rng.uniform(.20,.33))
        donor['ty_le_online_rieng']=float(rng.uniform(.09,.16))
        new_stores.append(donor)
        for month in pd.date_range(opened,'2025-12-01',freq='MS'):
            year_delta=month.year-2023
            season=1+.08*np.sin((month.month-3)*np.pi/6)
            ramp=.80 if month<opened+pd.DateOffset(months=3) else 1
            orders=int(round(donor.don_co_so*season*(1.06**year_delta)*ramp*rng.uniform(.94,1.06)))
            shares=[1-donor.ty_le_nen_tang-donor.ty_le_online_rieng,donor.ty_le_nen_tang,donor.ty_le_online_rieng]
            counts=[int(round(orders*shares[0])),int(round(orders*shares[1]))]
            counts.append(orders-sum(counts))
            row=dict(thang=month,nam=month.year,quy=month.quarter,store_id=sid,thanh_pho='TP.HCM',
                ty_le_gia_von=donor.ty_le_gia_von,ty_le_phi_nen_tang=.22,ty_le_nhuong_quyen=.04,
                luong_VND=int(round(donor.luong_co_so_VND*1.04**year_delta)),
                thue_VND=int(round(donor.thue_co_so_VND*1.03**year_delta)),
                khac_VND=int(round(donor.khac_co_so_VND*1.03**year_delta)),khau_hao_VND=donor.khau_hao_VND,
                loai_du_lieu='MO_PHONG',phien_ban='HCM_SIM_v1')
            for channel,count,mult in zip(['tai_quan','nen_tang','online_rieng'],counts,[1,1.08,1.04]):
                row['don_'+channel]=count
                row['AOV_'+channel]=int(round(donor.AOV_co_so_VND*mult*1.02**year_delta*rng.uniform(.97,1.03)))
            new_facts.append(row)
    additions=derive(pd.DataFrame(new_facts))
    for filename,new,datecol in [(STORE_FILE,pd.DataFrame(new_stores),'ngay_mo'),(CSV_PRIMARY,additions,'thang')]:
        original=pd.read_csv(raw/filename,dtype=str,keep_default_na=False,encoding='utf-8-sig')
        new=new[original.columns].copy()
        new[datecol]=new[datecol].dt.strftime('%m/%d/%Y')
        combined=pd.concat([original,new],ignore_index=True)
        combined.to_csv(raw/filename,index=False,encoding='utf-8-sig',float_format='%.10f')
    config['mo_rong_50_cua_hang']={'seed':20261007,'so_cua_hang_moi':30,
        'ghi_chu':'Địa bàn theo tên quận cũ, gồm Quận 2, Quận 9 và Thủ Đức. Không phải địa giới hiện hành. Các cửa hàng và vận hành bổ sung là mô phỏng; 20 cửa hàng ban đầu giữ nguyên. Các giả thiết tạo vận hành được khai báo trong Script/expand_stores.py.'}
    config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Đã bổ sung 30 cửa hàng và',len(additions),'bản ghi vận hành; giữ nguyên lỗi mô phỏng nguồn cũ.')

if __name__=='__main__': expand()
