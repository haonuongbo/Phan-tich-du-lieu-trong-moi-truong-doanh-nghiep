"""Làm sạch CSV thô với nhật ký từng thay đổi, không dùng tệp sạch làm nguồn."""
from __future__ import annotations

import re
from datetime import datetime

import numpy as np
import pandas as pd

STORE_NUMBERS = ["don_co_so", "AOV_co_so_VND", "ty_le_gia_von", "ty_le_nen_tang",
                 "ty_le_online_rieng", "luong_co_so_VND", "thue_co_so_VND",
                 "khac_co_so_VND", "khau_hao_VND"]
TEXT_FIELDS = ["store_id", "thanh_pho", "loai_du_lieu", "phien_ban"]
EMPTY = {"", "error", "null", "none", "n/a", "na", "nan", "#value!", "#n/a"}


def printable(value):
    return "" if pd.isna(value) else str(value)


def parse_number(value):
    text = printable(value).strip()
    if text.casefold() in EMPTY:
        return np.nan
    percent = text.endswith("%")
    text = re.sub(r"(?i)\s*(VND|VNĐ|đ|₫)$", "", text).strip()
    text = text.removesuffix("%").strip().replace("\u00a0", "").replace(" ", "")
    if re.fullmatch(r"[+-]?[1-9]\d{0,2}(,\d{3})+(\.\d+)?", text):
        text = text.replace(",", "")
    elif re.fullmatch(r"[+-]?[1-9]\d{0,2}(\.\d{3})+(,\d+)?", text):
        text = text.replace(".", "").replace(",", ".")
    elif "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        number = float(text)
        return number / 100 if percent else number
    except ValueError:
        return np.nan


def parse_date(value):
    text = printable(value).strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return pd.Timestamp(datetime.strptime(text, fmt))
        except ValueError:
            pass
    return pd.NaT


def clean_sources(raw_dir, store_file, fact_file, base_numbers, derive, quality):
    events, rejected = [], []

    def record(frame, index, col, before, after, rule, action="SUA_O"):
        if pd.isna(before) and col in frame.at[index, "__raw"]:
            before = frame.at[index, "__raw"][col]
        events.append({"tep": frame.at[index, "__file"], "dong_csv": int(frame.at[index, "__row"]),
                       "cot": col, "gia_tri_cu": printable(before), "gia_tri_moi": printable(after),
                       "quy_tac": rule, "hanh_dong": action, "loai_du_lieu": "MO_PHONG"})

    def update(frame, col, values, rule):
        for i in frame.index:
            before, after = frame.at[i, col], values.loc[i]
            numeric_equal = isinstance(before, (int, float, np.number)) and isinstance(after, (int, float, np.number)) and before == after
            if not numeric_equal and printable(before) != printable(after):
                record(frame, i, col, before, after, rule)
        frame[col] = values

    def read(name):
        frame = pd.read_csv(raw_dir / name, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        frame.columns = frame.columns.str.strip()
        if frame.columns.duplicated().any():
            raise ValueError(f"{name}: tên cột bị trùng sau chuẩn hóa")
        frame["__row"] = np.arange(2, len(frame) + 2)
        frame["__file"] = name
        frame["__raw"] = [{k: v for k, v in row.items() if not k.startswith("__")} for row in frame.to_dict("records")]
        return frame

    def reject(frame, reasons):
        for i, reason in reasons.items():
            if not reason:
                continue
            row = dict(frame.at[i, "__raw"])
            row.update(tep=frame.at[i, "__file"], dong_csv=int(frame.at[i, "__row"]), ly_do=reason)
            rejected.append(row)
            record(frame, i, "*", "Bản ghi không hợp lệ", "Loại", reason, "LOAI_DONG")
        return frame.loc[[i for i in frame.index if not reasons.get(i)]].copy()

    def normalize(frame, numbers, date_col):
        required = set(TEXT_FIELDS + numbers + [date_col])
        missing = required - set(frame)
        if missing:
            raise ValueError(f"{frame['__file'].iloc[0]}: thiếu cột {sorted(missing)}")
        blanks = frame[[c for c in frame if not c.startswith("__")]].apply(lambda s: s.str.strip().eq("")).all(axis=1)
        frame = reject(frame, {i: "Dòng rỗng" for i in frame.index[blanks]})
        for col in TEXT_FIELDS:
            values = frame[col].str.strip()
            if col == "store_id":
                values = values.str.upper().str.replace(r"[\s_-]+", "", regex=True)
            elif col == "thanh_pho":
                aliases = {"tp.hcm": "TP.HCM", "tp hcm": "TP.HCM", "tp. hồ chí minh": "TP.HCM",
                           "hồ chí minh": "TP.HCM", "ho chi minh": "TP.HCM", "hcm": "TP.HCM"}
                values = values.map(lambda v: aliases.get(v.casefold(), v))
            elif col == "loai_du_lieu":
                values = values.str.upper()
            else:
                values = values.map(lambda v: "HCM_SIM_v1" if v.casefold() == "hcm_sim_v1" else v)
            update(frame, col, values, "CHUAN_HOA_CHU")
        dates = frame[date_col].map(parse_date)
        update(frame, date_col, dates, "CHUAN_HOA_NGAY")
        for col in numbers:
            original = frame[col].copy()
            values = original.map(parse_number)
            # Không ghi mọi chuyển đổi string → float như lỗi dữ liệu.
            for i in frame.index:
                text = original.loc[i]
                if (any(x in text for x in [",", "%", "₫", "VND", "VNĐ", "đ"]) or text != text.strip()
                        or (pd.isna(values.loc[i]) and text.casefold() not in EMPTY)):
                    record(frame, i, col, text, values.loc[i], "CHUAN_HOA_SO")
            frame[col] = values
        return frame

    def invalid(frame, numbers, date_col, fact=False, known_stores=None):
        reasons = {}
        for i, row in frame.iterrows():
            problems = []
            if not re.fullmatch(r"SIM\d{3}", row.store_id):
                problems.append("Mã cửa hàng sai/thiếu")
            if row.thanh_pho != "TP.HCM" or row.loai_du_lieu != "MO_PHONG" or row.phien_ban != "HCM_SIM_v1":
                problems.append("Sai/thiếu phạm vi, nhãn hoặc phiên bản")
            if pd.isna(row[date_col]):
                problems.append("Ngày sai/thiếu")
            elif fact and row[date_col].day != 1:
                problems.append("Tháng không phải ngày đầu tháng")
            for col in numbers:
                value = row[col]
                if not np.isfinite(value) or value < 0:
                    problems.append(f"{col}: số thiếu/sai/âm")
                elif col.startswith("ty_le_") and value > 1:
                    problems.append(f"{col}: tỷ lệ ngoài [0,1]")
                elif col.startswith("don_") and value % 1 != 0:
                    problems.append(f"{col}: số đơn không nguyên")
            if fact and known_stores is not None:
                if row.store_id not in known_stores:
                    problems.append("Không có cửa hàng trong bảng 02")
                elif pd.notna(row[date_col]) and row[date_col] < known_stores[row.store_id].to_period("M").to_timestamp():
                    problems.append("Hoạt động trước tháng mở")
            if problems:
                reasons[i] = "; ".join(problems)
        return reject(frame, reasons)

    def deduplicate(frame, key, quality_key):
        business = [c for c in frame if not c.startswith("__")]
        duplicate = frame.duplicated(business, keep="first")
        quality[quality_key] = int(duplicate.sum())
        for i in frame.index[duplicate]:
            record(frame, i, "*", "Bản ghi trùng", "Loại", "TRUNG_HOAN_TOAN_SAU_CHUAN_HOA", "BO_TRUNG")
        frame = frame.loc[~duplicate].copy()
        if frame.duplicated(key).any():
            raise ValueError(f"Khóa trùng mâu thuẫn {key}; không tự chọn bản ghi")
        return frame

    stores, fact = read(store_file), read(fact_file)
    raw_counts = {store_file: len(stores), fact_file: len(fact)}
    stores = normalize(stores, STORE_NUMBERS, "ngay_mo")
    stores = invalid(stores, STORE_NUMBERS, "ngay_mo")
    stores = deduplicate(stores, ["store_id"], "cua_hang_trung_hoan_toan_da_bo")
    known = dict(zip(stores.store_id, stores.ngay_mo))

    derived_numbers = [c for c in fact if not c.startswith("__") and c not in set(TEXT_FIELDS + ["thang"] + base_numbers)]
    fact = normalize(fact, base_numbers + derived_numbers, "thang")
    # Phục hồi số đơn/AOV chỉ khi đã có hai thành phần còn lại trong cùng dòng.
    for channel in ("tai_quan", "nen_tang", "online_rieng"):
        order_col, aov_col, revenue_col = f"don_{channel}", f"AOV_{channel}", f"DT_{channel}"
        if revenue_col not in fact:
            continue
        for i in fact.index:
            order, aov, revenue = fact.loc[i, [order_col, aov_col, revenue_col]]
            if pd.isna(order) and np.isfinite(aov) and aov > 0 and np.isfinite(revenue) and revenue >= 0:
                recovered = revenue / aov
                if abs(recovered - round(recovered)) < 1e-7:
                    record(fact, i, order_col, order, round(recovered), "PHUC_HOI_TU_DT_AOV")
                    fact.at[i, order_col] = round(recovered)
            elif pd.isna(aov) and np.isfinite(order) and order > 0 and np.isfinite(revenue) and revenue >= 0:
                record(fact, i, aov_col, aov, revenue / order, "PHUC_HOI_TU_DT_DON")
                fact.at[i, aov_col] = revenue / order
    fact = invalid(fact, base_numbers, "thang", fact=True, known_stores=known)
    if fact.empty or stores.empty:
        raise ValueError("Không còn dữ liệu hợp lệ sau làm sạch")
    for col, values in [("nam", fact.thang.dt.year), ("quy", fact.thang.dt.quarter)]:
        if col in fact:
            update(fact, col, values, "SUY_RA_TU_THANG")
        else:
            fact[col] = values
    computed = derive(fact)
    quality["doi_chieu_cong_thuc"] = {}
    for col in computed:
        if col not in fact or col in base_numbers or col in TEXT_FIELDS or col in ["thang", "nam", "quy"] or col.startswith("__"):
            continue
        old, new = fact[col], computed[col]
        tolerance = 1e-8 if col.startswith("bien_") or col == "ty_trong_DT_online" else 1.0
        difference = (old - new).abs()
        changed = difference.gt(tolerance) | (old.isna() & new.notna())
        quality["doi_chieu_cong_thuc"][col] = {"sai_lech_toi_da": float(difference.max()) if difference.notna().any() else None,
                                               "so_dong_vuot_dung_sai": int(changed.sum())}
        for i in fact.index[changed]:
            record(fact, i, col, old.loc[i], new.loc[i], "TINH_LAI_TU_DU_LIEU_CO_SO")
    fact = deduplicate(computed, ["store_id", "thang"], "van_hanh_trung_hoan_toan_da_bo")
    # Dòng CSV ban đầu được giữ trong dữ liệu sạch để truy vết.
    stores = stores.drop(columns=["__file", "__raw"]).rename(columns={"__row": "nguon_dong_cua_hang"})
    fact = fact.drop(columns=["__file", "__raw"]).rename(columns={"__row": "nguon_dong_van_hanh"})
    fact["nguon_tep"] = fact_file
    quality.update(so_dong_nguon_cua_hang=raw_counts[store_file], so_dong_nguon=raw_counts[fact_file],
                   nguon_van_hanh=fact_file, so_dong_loi_cua_hang=sum(r["tep"] == store_file for r in rejected),
                   so_dong_loi_van_hanh=sum(r["tep"] == fact_file for r in rejected),
                   so_o_da_sua=sum(e["hanh_dong"] == "SUA_O" for e in events),
                   _nhat_ky=events, _dong_loai=rejected)
    return stores, fact
