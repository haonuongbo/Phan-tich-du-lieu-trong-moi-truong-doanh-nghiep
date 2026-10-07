"""Làm sạch nguồn 02 và DULIEUTHO.csv, tính KPI và xuất dữ liệu phân tích."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from cleaning import clean_sources

ROOT = Path(__file__).resolve().parents[1]
STORE_FILE = "02_KFC_TPHCM_cua_hang_mo_phong.csv"
CSV_PRIMARY = "DULIEUTHO.csv"
LABEL = "MÔ PHỎNG — Không phản ánh kết quả kinh doanh thực tế của KFC."
CHANNELS = ["tai_quan", "nen_tang", "online_rieng"]
BASE_NUMBERS = ([f"don_{c}" for c in CHANNELS] + [f"AOV_{c}" for c in CHANNELS]
                + ["ty_le_gia_von", "ty_le_phi_nen_tang", "ty_le_nhuong_quyen",
                   "luong_VND", "thue_VND", "khac_VND", "khau_hao_VND"])
ADDITIVE = ["DT_tong", "tong_don", "gia_von_VND", "phi_nen_tang_VND",
            "phi_nhuong_quyen_VND", "luong_VND", "thue_VND", "khac_VND", "khau_hao_VND",
            "loi_nhuan_gop", "LN_van_hanh_mo_hinh"] + [f"DT_{c}" for c in CHANNELS]


class DataQualityError(ValueError):
    """Dừng xuất KPI nếu đầu vào không đủ tin cậy."""


def require(condition, message):
    if not condition:
        raise DataQualityError(message)


def safe_div(numerator, denominator):
    if isinstance(denominator, pd.Series):
        return numerator / denominator.replace(0, np.nan)
    return numerator / denominator if denominator else np.nan


def derive(frame):
    frame = frame.copy()
    for channel in CHANNELS:
        frame[f"DT_{channel}"] = frame[f"don_{channel}"] * frame[f"AOV_{channel}"]
    frame["DT_tong"] = frame[[f"DT_{c}" for c in CHANNELS]].sum(axis=1)
    frame["tong_don"] = frame[[f"don_{c}" for c in CHANNELS]].sum(axis=1)
    frame["gia_von_VND"] = frame.DT_tong * frame.ty_le_gia_von
    frame["phi_nen_tang_VND"] = frame.DT_nen_tang * frame.ty_le_phi_nen_tang
    frame["phi_nhuong_quyen_VND"] = frame.DT_tong * frame.ty_le_nhuong_quyen
    frame["loi_nhuan_gop"] = frame.DT_tong - frame.gia_von_VND
    frame["LN_van_hanh_mo_hinh"] = frame.loi_nhuan_gop - frame[
        ["phi_nen_tang_VND", "phi_nhuong_quyen_VND", "luong_VND", "thue_VND", "khac_VND", "khau_hao_VND"]
    ].sum(axis=1)
    frame["bien_LN_van_hanh"] = safe_div(frame.LN_van_hanh_mo_hinh, frame.DT_tong)
    frame["bien_LN_gop"] = safe_div(frame.loi_nhuan_gop, frame.DT_tong)
    frame["AOV_tong"] = safe_div(frame.DT_tong, frame.tong_don)
    frame["ty_trong_DT_online"] = safe_div(frame.DT_nen_tang + frame.DT_online_rieng, frame.DT_tong)
    return frame


def load_clean(raw_dir, quality):
    try:
        stores, fact = clean_sources(raw_dir, STORE_FILE, CSV_PRIMARY, BASE_NUMBERS, derive, quality)
    except ValueError as error:
        raise DataQualityError(str(error)) from error
    # Dữ liệu này không có đóng cửa. Thiếu cửa hàng-tháng là lỗi, không tự điền 0.
    months = pd.date_range(fact.thang.min(), fact.thang.max(), freq="MS")
    expected = {(s.store_id, m) for s in stores.itertuples() for m in months
                if s.ngay_mo.to_period("M").to_timestamp() <= m}
    observed = set(zip(fact.store_id, fact.thang))
    require(expected == observed, f"Thiếu/thừa cửa hàng-tháng: thiếu {len(expected-observed)}, thừa {len(observed-expected)}")
    fact = fact.sort_values(["thang", "store_id"]).reset_index(drop=True)
    fact["nam"] = fact.thang.dt.year
    fact["quy"] = fact.thang.dt.quarter
    quality.update(so_dong_sach=len(fact), so_cua_hang=len(stores), so_thang=len(months),
                   tu_thang=str(fact.thang.min().date()), den_thang=str(fact.thang.max().date()))
    return stores.sort_values("store_id"), fact


def aggregate(fact, keys):
    group = fact.groupby(keys, sort=True, dropna=False)
    out = group[ADDITIVE].sum().reset_index()
    counts = group.agg(so_thang=("thang", "nunique"), CH_co_phat_sinh=("store_id", "nunique"),
                       cua_hang_thang=("store_id", "size")).reset_index()
    out = out.merge(counts, on=keys, validate="one_to_one")
    out["CH_binh_quan"] = out.cua_hang_thang / out.so_thang
    out["DT_CH"] = safe_div(out.DT_tong, out.CH_binh_quan)
    out["AOV_tong"] = safe_div(out.DT_tong, out.tong_don)
    out["bien_LN_gop"] = safe_div(out.loi_nhuan_gop, out.DT_tong)
    out["bien_LN_van_hanh"] = safe_div(out.LN_van_hanh_mo_hinh, out.DT_tong)
    out["ty_trong_DT_online"] = safe_div(out.DT_nen_tang + out.DT_online_rieng, out.DT_tong)
    out["loai_du_lieu"] = "MO_PHONG"
    return out


def period_kpis(fact, stores, freq):
    frame = fact.copy()
    frame["ky"] = frame.thang.dt.to_period(freq).dt.to_timestamp()
    out = aggregate(frame, ["ky"])
    out["nam"] = out.ky.dt.year
    out["quy"] = out.ky.dt.quarter
    out["so_thang_ky"] = {"M": 1, "Q": 3, "Y": 12}[freq]
    out["du_ky"] = out.so_thang.eq(out.so_thang_ky)
    out["CH_dau_ky"] = out.ky.map(lambda d: int(stores.ngay_mo.le(d).sum()))
    out["CH_cuoi_ky"] = out.ky.map(lambda d: int(stores.ngay_mo.le(d.to_period(freq).end_time).sum()))
    out["CH_bq_dau_cuoi"] = (out.CH_dau_ky + out.CH_cuoi_ky) / 2
    indexed = out.set_index("ky")
    for label, offset in [("tang_truong_ky_truoc", {"M": 1, "Q": 3, "Y": 12}[freq]), ("YoY_doanh_thu", 12)]:
        values = []
        for row in out.itertuples():
            prior = row.ky - pd.DateOffset(months=offset)
            if prior in indexed.index and row.du_ky and indexed.loc[prior, "du_ky"]:
                values.append(safe_div(row.DT_tong, indexed.loc[prior, "DT_tong"]) - 1)
            else:
                values.append(np.nan)
        out[label] = values
    return out


def comparable_stores(fact):
    records = []
    for year in sorted(fact.nam.unique()):
        current, previous = fact[fact.nam.eq(year)], fact[fact.nam.eq(year - 1)]
        # Chỉ dùng năm đủ 12 tháng ở cả hai phía và cùng cửa hàng.
        cur_ids = set(current.groupby("store_id").thang.nunique().loc[lambda s: s.eq(12)].index)
        old_ids = set(previous.groupby("store_id").thang.nunique().loc[lambda s: s.eq(12)].index)
        ids = cur_ids & old_ids
        cur_revenue = current[current.store_id.isin(ids)].DT_tong.sum() if ids else np.nan
        old_revenue = previous[previous.store_id.isin(ids)].DT_tong.sum() if ids else np.nan
        records.append({"nam": int(year), "so_CH_tuong_duong": len(ids), "DT_cung_CH_nam_nay": cur_revenue,
                        "DT_cung_CH_nam_truoc": old_revenue, "SSSG": safe_div(cur_revenue, old_revenue) - 1,
                        "loai_du_lieu": "MO_PHONG"})
    return pd.DataFrame(records)


def build_tables(stores, fact):
    monthly, quarterly, annual = [period_kpis(fact, stores, f) for f in ("M", "Q", "Y")]
    annual = annual.merge(comparable_stores(fact), on=["nam", "loai_du_lieu"], validate="one_to_one")
    annual["tang_truong_CH"] = annual.CH_binh_quan.pct_change(fill_method=None)
    annual["tang_truong_DT_CH"] = annual.DT_CH.pct_change(fill_method=None)
    annual["thay_doi_bien_LN_diem_pct"] = annual.bien_LN_van_hanh.diff() * 100
    comparable = annual.du_ky & annual.du_ky.shift(1, fill_value=False) & annual.nam.diff().eq(1)
    annual.loc[~comparable, ["tang_truong_CH", "tang_truong_DT_CH", "thay_doi_bien_LN_diem_pct"]] = np.nan
    annual["trang_thai"] = annual.apply(lambda r: "Chưa có kỳ so sánh" if pd.isna(r.YoY_doanh_thu)
        else "Cần rà soát biên lợi nhuận" if r.thay_doi_bien_LN_diem_pct < 0
        else "Doanh thu và biên LN cải thiện" if r.YoY_doanh_thu > 0 else "Cần theo dõi doanh thu", axis=1)
    dates = pd.DataFrame({"ngay": pd.date_range(f"{fact.nam.min()}-01-01", f"{fact.nam.max()}-12-31")})
    dates["nam"] = dates.ngay.dt.year
    dates["quy"] = dates.ngay.dt.quarter
    dates["thang_so"] = dates.ngay.dt.month
    dates["nam_thang"] = dates.ngay.dt.strftime("%Y-%m")
    dates["nam_quy"] = dates.nam.astype(str) + "-Q" + dates.quy.astype(str)
    dates["loai_du_lieu"] = "MO_PHONG"
    channels = []
    for c in CHANNELS:
        channel = fact[["thang", "store_id", f"don_{c}", f"DT_{c}", "loai_du_lieu"]].copy()
        channel.columns = ["thang", "store_id", "so_don", "doanh_thu", "loai_du_lieu"]
        channel["kenh"] = c
        channels.append(channel)
    full = annual[annual.du_ky]
    cagr = np.nan
    if len(full) >= 2:
        first, last = full.iloc[0], full.iloc[-1]
        if first.DT_tong > 0:
            cagr = (last.DT_tong / first.DT_tong) ** (1 / (last.nam - first.nam)) - 1
    overview = pd.DataFrame([{"nam_dau": int(full.nam.min()) if len(full) else None,
        "nam_cuoi": int(full.nam.max()) if len(full) else None, "CAGR_doanh_thu": cagr,
        "ghi_chu": "CAGR chỉ dùng tổng năm đủ 12 tháng; khoảng cách = năm cuối - năm đầu",
        "loai_du_lieu": "MO_PHONG"}])
    return {"Dim_Store": stores, "Dim_Date": dates, "Fact_Operation": fact,
            "Fact_Channel": pd.concat(channels, ignore_index=True), "KPI_Thang": monthly,
            "KPI_Quy": quarterly, "KPI_Nam": annual, "KPI_CuaHang_Nam": aggregate(fact, ["nam", "store_id"]),
            "KPI_TongQuan": overview}


def write_csv(frame, path):
    frame.to_csv(path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d", float_format="%.10f")


def run(project=ROOT):
    project = Path(project).resolve()
    raw = project / "DataGoc"
    report_dir = project / "BaoCao"
    report_dir.mkdir(exist_ok=True)
    quality = {"nhan_du_lieu": LABEL, "trang_thai": "DANG_KIEM_TRA"}
    try:
        stores, fact = load_clean(raw, quality)
        quality["so_dong_doi_chieu_cong_thuc"] = len(fact)
        tables = build_tables(stores, fact)
        from menu_area import extend
        tables = extend(tables, project)
        stores = tables['Dim_Store']
        quality['phan_tich_menu_khu_vuc'] = 'Kịch bản phân bổ giả định; không phải giao dịch POS, sở thích khách hàng hoặc vị trí thực tế.'
    except (DataQualityError, OSError, ValueError, KeyError) as error:
        quality.pop("_nhat_ky", None)
        quality.pop("_dong_loai", None)
        quality.update(trang_thai="LOI", loi=str(error), luu_y="Không xuất mới. Đầu ra cũ (nếu có) không đại diện lần chạy này.")
        (report_dir / "chat_luong_du_lieu.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    clean_dir, analysis_dir = project / "DataSach", project / "DataPhantich"
    clean_dir.mkdir(exist_ok=True)
    analysis_dir.mkdir(exist_ok=True)
    # Một tệp sạch duy nhất, độ hạt cửa hàng–tháng; dimension/fact chỉ là đầu ra BI.
    store_attributes = stores.rename(columns={"ty_le_gia_von": "ty_le_gia_von_co_so", "khau_hao_VND": "khau_hao_co_so_VND"})
    extra_cols = [c for c in store_attributes if c == "store_id" or c not in fact]
    unified = fact.merge(store_attributes[extra_cols], on="store_id", validate="many_to_one")
    write_csv(unified, clean_dir / "DULIEUSACH.csv")
    write_csv(pd.DataFrame(quality.pop("_nhat_ky")), report_dir / "nhat_ky_lam_sach.csv")
    rejected = quality.pop("_dong_loai")
    write_csv(pd.DataFrame(rejected) if rejected else pd.DataFrame(columns=["tep", "dong_csv", "ly_do"]),
              report_dir / "dong_bi_loai.csv")
    for name, table in tables.items():
        write_csv(table, analysis_dir / f"{name}.csv")
    comparison = pd.DataFrame([{"cot": k, **v, "loai_du_lieu": "MO_PHONG"}
                               for k, v in quality["doi_chieu_cong_thuc"].items()])
    write_csv(comparison, report_dir / "doi_chieu_cong_thuc.csv")
    manifest = {"nhan_du_lieu": LABEL, "tao_luc_UTC": datetime.now(timezone.utc).isoformat(),
        "nguon_chinh": [STORE_FILE, quality["nguon_van_hanh"]],
        "quy_tac": "Chỉ đọc CSV 02 và DULIEUTHO.csv; chuẩn hóa, phục hồi theo công thức, loại dòng lỗi/trùng có nhật ký; tệp sạch duy nhất là DataSach/DULIEUSACH.csv.",
        "nguon": [{"tep": name, "sha256": hashlib.sha256((raw / name).read_bytes()).hexdigest()}
                  for name in (STORE_FILE, quality["nguon_van_hanh"])],
        "bang_xuat": {name: len(table) for name, table in tables.items()}}
    manifest['gia_dinh_menu_khu_vuc'] = {'tep': 'Script/gia_dinh_menu_khu_vuc.json',
        'sha256': hashlib.sha256((project / 'Script/gia_dinh_menu_khu_vuc.json').read_bytes()).hexdigest(),
        'canh_bao': 'Các món, số lượng và vị trí được giả định, không được suy ra từ nguồn 02 + DULIEUTHO.'}
    (analysis_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    quality["trang_thai"] = "DAT"
    from menu_area import write_summary
    write_summary(tables, project)
    (report_dir / "chat_luong_du_lieu.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    return tables, quality
