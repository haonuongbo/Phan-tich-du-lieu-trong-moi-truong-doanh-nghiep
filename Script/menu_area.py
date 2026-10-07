"""Kịch bản phân bổ giả định; không suy ra dữ liệu POS từ doanh thu tổng."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

NOTE = 'GIA_DINH_PHAN_BO_KHONG_PHAI_POS'

def extend(tables, project):
    config = json.loads((Path(project) / 'Script/gia_dinh_menu_khu_vuc.json').read_text(encoding='utf-8'))
    stores = tables['Dim_Store'].copy()
    ids = set(stores.store_id)
    if ids != set(config['vi_tri']):
        raise ValueError('Cần khai báo vị trí giả định cho đúng tập cửa hàng nguồn.')
    stores['khu_vuc_gia_dinh'] = stores.store_id.map(lambda s: config['vi_tri'][s][0])
    stores['loai_vi_tri_gia_dinh'] = stores.store_id.map(lambda s: config['vi_tri'][s][1])
    stores['co_so_vi_tri'] = NOTE
    menu = pd.DataFrame(config['menu'])
    if menu.menu_id.duplicated().any() or not menu.gia_tham_chieu_VND.gt(0).all():
        raise ValueError('Menu giả định cần mã duy nhất, giá tham chiếu dương.')
    groups = list(menu.nhom_mon.unique())
    for profile in config['trong_so_theo_vi_tri'].values():
        if set(profile) != set(groups) or any(v <= 0 for v in profile.values()):
            raise ValueError('Trọng số phải dương và đủ nhóm món.')
    records = []
    for r in tables['Fact_Channel'].itertuples():
        kind = config['vi_tri'][r.store_id][1]
        weights = np.array([config['trong_so_theo_vi_tri'][kind][g] / int(menu.nhom_mon.eq(g).sum()) for g in menu.nhom_mon])
        # Điều chỉnh kênh là giả định công khai, không phải hệ số ước lượng.
        if r.kenh != 'tai_quan':
            weights *= np.where(menu.nhom_mon.eq('Combo'), 1.2, 1.0)
        amounts = r.doanh_thu * weights / weights.sum()
        amounts[-1] = r.doanh_thu - amounts[:-1].sum()
        for item, amount in zip(menu.itertuples(), amounts):
            qty = int(round(amount / item.gia_tham_chieu_VND)) if amount > 0 else 0
            qty = max(1, qty) if amount > 0 else 0
            records.append(dict(thang=r.thang, store_id=r.store_id, kenh=r.kenh,
                menu_id=item.menu_id, ten_mon=item.ten_mon, nhom_mon=item.nhom_mon,
                so_luong_uoc_tinh=qty, doanh_thu_phan_bo_VND=amount,
                gia_binh_quan_uoc_tinh_VND=amount/qty if qty else 0,
                nam=r.thang.year, quy=r.thang.quarter, loai_du_lieu='MO_PHONG', co_so_du_lieu=NOTE))
    sales = pd.DataFrame(records)
    reconciled = sales.groupby(['thang','store_id','kenh']).doanh_thu_phan_bo_VND.sum()
    original = tables['Fact_Channel'].set_index(['thang','store_id','kenh']).doanh_thu
    if not np.allclose(reconciled.reindex(original.index), original, atol=.01, rtol=0):
        raise ValueError('Phân bổ món không khớp doanh thu kênh nguồn.')
    menu['co_so_du_lieu'] = NOTE
    menu['loai_du_lieu'] = 'MO_PHONG'
    tables.update(Dim_Store=stores, Dim_Menu=menu, Fact_Menu=sales)
    for name, keys in [('KPI_Mon_Nam',['nam','menu_id','ten_mon','nhom_mon']), ('KPI_NhomMon_Nam',['nam','nhom_mon'])]:
        out = sales.groupby(keys, as_index=False).agg(doanh_thu_phan_bo_VND=('doanh_thu_phan_bo_VND','sum'),so_luong_uoc_tinh=('so_luong_uoc_tinh','sum'))
        out['ty_trong_doanh_thu'] = out.doanh_thu_phan_bo_VND / out.groupby('nam').doanh_thu_phan_bo_VND.transform('sum')
        out['ty_trong_so_luong_uoc_tinh'] = out.so_luong_uoc_tinh / out.groupby('nam').so_luong_uoc_tinh.transform('sum')
        out['co_so_du_lieu'] = NOTE
        tables[name] = out
    from pipeline import aggregate
    joined = tables['Fact_Operation'].merge(stores[['store_id','khu_vuc_gia_dinh','loai_vi_tri_gia_dinh']], on='store_id',validate='many_to_one')
    tables['KPI_KhuVuc_Nam'] = aggregate(joined,['nam','khu_vuc_gia_dinh'])
    tables['KPI_LoaiViTri_Nam'] = aggregate(joined,['nam','loai_vi_tri_gia_dinh'])
    for name in ['KPI_KhuVuc_Nam','KPI_LoaiViTri_Nam']:
        tables[name]['co_so_vi_tri'] = NOTE
    return tables


def write_summary(tables, project):
    year = int(tables['KPI_Nam'].nam.max())
    fmt = lambda x: f'{x:,.2f}'.replace(',','_').replace('.',',').replace('_','.')
    lines = [f'# Phân tích menu và khu vực — năm {year}', '',
        '**KỊCH BẢN GIẢ ĐỊNH, KHÔNG PHẢI SỐ BÁN THEO MÓN HOẶC VỊ TRÍ THỰC TẾ.**', '',
        'Nguồn 02 và DULIEUTHO không chứa giao dịch POS theo món, khách hàng định danh hoặc địa chỉ. Phần bổ sung minh họa cách phân tích khi có những trường này. Tổng doanh thu vận hành giữ nguyên; không coi phân bổ là dữ liệu thu thập được.', '',
        '## Doanh thu các món trong menu học tập', '',
        '| Món giả định | Nhóm | Doanh thu phân bổ (tỷ VND) | Tỷ trọng DT | Số lượng ước tính |',
        '|---|---|---:|---:|---:|']
    for r in tables['KPI_Mon_Nam'].query('nam == @year').sort_values('doanh_thu_phan_bo_VND',ascending=False).itertuples():
        lines.append(f'| {r.ten_mon} | {r.nhom_mon} | {fmt(r.doanh_thu_phan_bo_VND/1e9)} | {fmt(r.ty_trong_doanh_thu*100)}% | {r.so_luong_uoc_tinh:,} |')
    lines += ['', '## Khách hàng có thể ưu ái loại hình nào?', '',
        'Chưa kết luận được từ nguồn hiện có. Tỷ trọng doanh thu phụ thuộc giá, số lượng và trọng số được đặt trước; tỷ trọng số lượng ở đây cũng là ước tính, không phải khảo sát sở thích. Combo được tính nguyên gói, không đếm lại thành phần. Không dùng số lượng món để suy ra số khách hoặc số đơn.', '',
        'Giả thuyết để thử: combo nhóm ở điểm thương mại; cơm/burger hoặc combo một người ở văn phòng và gần trường học; gói mang về ở khu dân cư. Thu thập POS gồm mã đơn, mã món, số lượng, giá, chiết khấu, doanh thu thuần, cửa hàng, thời gian và kênh để kiểm chứng. Xem số đơn có món / tổng số đơn và số lượng bán song song với doanh thu; bổ sung khảo sát nếu muốn đo sở thích.', '',
        '## Khu vực và doanh thu', '',
        '| Khu vực giả định | DT (tỷ) | CH bình quân | DT/CH/năm (tỷ) | LN vận hành (tỷ) | Biên LN |',
        '|---|---:|---:|---:|---:|---:|']
    for r in tables['KPI_KhuVuc_Nam'].query('nam == @year').sort_values('DT_CH',ascending=False).itertuples():
        lines.append(f'| {r.khu_vuc_gia_dinh} | {fmt(r.DT_tong/1e9)} | {fmt(r.CH_binh_quan)} | {fmt(r.DT_CH/1e9)} | {fmt(r.LN_van_hanh_mo_hinh/1e9)} | {fmt(r.bien_LN_van_hanh*100)}% |')
    lines += ['', 'Danh sách cửa hàng–khu vực–loại vị trí nằm trong Dim_Store.csv và trang Khu vực giả định của dashboard. Tên địa bàn là nhãn mô tả quen thuộc, không phải bảng địa giới hiện hành. Doanh thu không được thay đổi dựa vào vị trí. Vì vị trí được gán chủ quan, bảng này không chứng minh khu vực nào thực tế kinh doanh tốt hơn.', '',
        '## Hành động để tăng doanh thu có kiểm chứng', '',
        '1. Thu thập giao dịch theo món và địa chỉ thực; thêm giá vốn món, khuyến mại, phí giao hàng để tính lãi đóng góp.',
        '2. Thử gói món phù hợp từng loại điểm trong 4–8 tuần, có nhóm cửa hàng đối chứng cùng tuổi cửa hàng và cùng mùa. So doanh thu/CH/ngày hoạt động, số đơn, giá trị đơn và lãi đóng góp.',
        '3. Nhân rộng khi doanh thu và lãi đóng góp cùng tăng. Với cửa hàng lỗ, rà soát mặt bằng, giá vốn, nhân sự trước khi tăng ngân sách quảng cáo hoặc mở thêm điểm.', '',
        '## Quy tắc và khả năng truy vết', '',
        'Giả định duy nhất: Script/gia_dinh_menu_khu_vuc.json. Mỗi nhóm có trọng số riêng theo loại vị trí; chia đều trong nhóm, tăng trọng số combo ×1,2 cho giao hàng rồi chuẩn hóa tổng bằng 1. Phân bổ theo từng cửa hàng–tháng–kênh, số lượng = làm tròn doanh thu phân bổ / giá tham chiếu. Giá bình quân ước tính = doanh thu phân bổ / số lượng; giá tham chiếu không phải giá niêm yết thật.', '',
        'Fact_Menu có độ hạt tháng–cửa hàng–kênh–món. Không nối trực tiếp hai fact và không cộng doanh thu món với doanh thu vận hành. DULIEUSACH vẫn là một tệp cửa hàng–tháng; giữ nguyên nguồn thô bẩn. Word/PowerPoint cũ trình bày phân tích vận hành; phụ lục này và dashboard là phần bổ sung menu/khu vực hiện hành.', '']
    (Path(project)/'BaoCao/PhanTich_Menu_KhuVuc.md').write_text('\n'.join(lines),encoding='utf-8')
