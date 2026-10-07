"""Kiểm tra phục hồi dữ liệu thô, loại lỗi và tính KPI không đếm trùng."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Script"))
from pipeline import CSV_PRIMARY, STORE_FILE, DataQualityError, aggregate, build_tables, load_clean, run, safe_div
from cleaning import parse_date, parse_number


class CleaningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quality = {}
        cls.stores, cls.fact = load_clean(ROOT / "DataGoc", cls.quality)
        cls.tables = build_tables(cls.stores, cls.fact)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.raw = self.project / "DataGoc"
        self.raw.mkdir()
        (self.project / 'Script').mkdir()
        shutil.copy2(ROOT / 'Script/gia_dinh_menu_khu_vuc.json', self.project / 'Script/gia_dinh_menu_khu_vuc.json')
        # Các kiểm thử lỗi bổ sung bắt đầu từ nguồn hợp lệ độc lập với lỗi mô phỏng.
        for name, frame in [(STORE_FILE, self.stores), (CSV_PRIMARY, self.fact)]:
            frame = frame[[c for c in frame if not c.startswith("nguon_")]]
            frame.to_csv(self.raw / name, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")

    def edit(self, operation):
        path = self.raw / CSV_PRIMARY
        frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        operation(frame).to_csv(path, index=False, encoding="utf-8-sig")

    def test_dirty_sources_clean_back_to_business_controls(self):
        self.assertEqual(len(self.stores), 20)
        self.assertEqual(len(self.fact), 576)
        expected = {2023: 78631832128, 2024: 116703907795, 2025: 146385764418}
        self.assertEqual(self.fact.groupby("nam").DT_tong.sum().to_dict(), expected)
        self.assertEqual(self.fact.tong_don.sum(), 2875801)
        self.assertEqual(self.quality["so_dong_nguon_cua_hang"], 29)
        self.assertEqual(self.quality["so_dong_nguon"], 597)
        self.assertEqual(self.quality["cua_hang_trung_hoan_toan_da_bo"], 4)
        self.assertEqual(self.quality["van_hanh_trung_hoan_toan_da_bo"], 12)
        self.assertEqual(self.quality["so_dong_loi_cua_hang"], 5)
        self.assertEqual(self.quality["so_dong_loi_van_hanh"], 9)
        self.assertFalse(self.fact.duplicated(["store_id", "thang"]).any())

    def test_raw_sources_unchanged_and_one_clean_file(self):
        for name in (STORE_FILE, CSV_PRIMARY):
            shutil.copy2(ROOT / "DataGoc" / name, self.raw / name)
        before = {name: hashlib.sha256((self.raw / name).read_bytes()).hexdigest() for name in (STORE_FILE, CSV_PRIMARY)}
        (self.raw / "DULIEUTHO.xlsx").write_text("not a workbook")
        run(self.project)
        self.assertEqual([p.name for p in (self.project / "DataSach").iterdir()], ["DULIEUSACH.csv"])
        unified = pd.read_csv(self.project / "DataSach/DULIEUSACH.csv", encoding="utf-8-sig")
        self.assertEqual(len(unified), 576)
        self.assertTrue({"ngay_mo", "DT_tong", "AOV_co_so_VND", "ty_le_gia_von_co_so"} <= set(unified))
        for name, digest in before.items():
            self.assertEqual(hashlib.sha256((self.raw / name).read_bytes()).hexdigest(), digest)

    def test_audit_preserves_original_error_and_line_numbers(self):
        logs = pd.DataFrame(self.quality["_nhat_ky"])
        recovery = logs[logs.quy_tac.eq("PHUC_HOI_TU_DT_DON")]
        self.assertIn("ERROR", recovery.gia_tri_cu.tolist())
        self.assertTrue(logs.dong_csv.ge(2).all())
        self.assertEqual(len(self.quality["_dong_loai"]), 14)
        self.assertIn("ERROR", pd.DataFrame(self.quality["_dong_loai"]).luong_VND.tolist())

    def test_financial_total_independent_decimal(self):
        frame = pd.read_csv(self.raw / CSV_PRIMARY, dtype=str, encoding="utf-8-sig")
        profit = Decimal(0)
        for row in frame.to_dict("records"):
            revenues = {c: Decimal(row[f"don_{c}"]) * Decimal(row[f"AOV_{c}"])
                        for c in ["tai_quan", "nen_tang", "online_rieng"]}
            revenue = sum(revenues.values())
            profit += revenue * (1 - Decimal(row["ty_le_gia_von"]) - Decimal(row["ty_le_nhuong_quyen"]))
            profit -= revenues["nen_tang"] * Decimal(row["ty_le_phi_nen_tang"])
            profit -= sum(Decimal(row[c]) for c in ["luong_VND", "thue_VND", "khac_VND", "khau_hao_VND"])
        self.assertAlmostEqual(self.fact.LN_van_hanh_mo_hinh.sum(), float(profit), places=3)

    def test_locale_dates_money_percent_and_real_zero(self):
        self.assertEqual(parse_date("12/1/2025"), pd.Timestamp("2025-12-01"))
        self.assertEqual(parse_date("2023/01/01"), pd.Timestamp("2023-01-01"))
        self.assertTrue(pd.isna(parse_date("31/31/2025")))
        self.assertEqual(parse_number("120,932 VND"), 120932)
        self.assertEqual(parse_number("120.932 đ"), 120932)
        self.assertAlmostEqual(parse_number("43,5%"), .435)
        self.assertAlmostEqual(parse_number("0,435"), .435)
        self.assertEqual(parse_number("0"), 0)
        self.assertTrue(pd.isna(parse_number("ERROR")))
        self.assertTrue(pd.isna(safe_div(12, 0)))

    def test_yearly_growth_and_cagr_now_available(self):
        annual = self.tables["KPI_Nam"].set_index("nam")
        self.assertTrue(pd.isna(annual.loc[2023, "YoY_doanh_thu"]))
        self.assertAlmostEqual(annual.loc[2024, "YoY_doanh_thu"], 116703907795 / 78631832128 - 1)
        self.assertAlmostEqual(annual.loc[2025, "YoY_doanh_thu"], 146385764418 / 116703907795 - 1)
        self.assertAlmostEqual(self.tables["KPI_TongQuan"].iloc[0].CAGR_doanh_thu,
                               (146385764418 / 78631832128) ** .5 - 1)
        self.assertEqual(annual.loc[2024, "so_CH_tuong_duong"], 12)
        self.assertEqual(annual.loc[2025, "so_CH_tuong_duong"], 16)

    def test_aggregation_and_weighted_ratios(self):
        for name in ["KPI_Thang", "KPI_Quy", "KPI_Nam", "KPI_CuaHang_Nam"]:
            self.assertEqual(self.tables[name].DT_tong.sum(), 341721504341)
        self.assertEqual(self.tables["Fact_Channel"].doanh_thu.sum(), 341721504341)
        self.assertEqual(len(self.tables["Dim_Date"]), 1096)
        frame = self.fact.iloc[:2].copy()
        frame["DT_tong"], frame["tong_don"], frame["LN_van_hanh_mo_hinh"] = [100,900], [10,30], [50,90]
        result = aggregate(frame, ["nam"]).iloc[0]
        self.assertEqual(result.AOV_tong, 25)
        self.assertAlmostEqual(result.bien_LN_van_hanh, .14)

    def test_identical_duplicate_does_not_change_revenue(self):
        self.edit(lambda frame: pd.concat([frame, frame.iloc[:1]], ignore_index=True))
        quality = {}
        _, frame = load_clean(self.raw, quality)
        self.assertEqual(quality["van_hanh_trung_hoan_toan_da_bo"], 1)
        self.assertEqual(frame.DT_tong.sum(), 341721504341)

    def test_conflicting_business_duplicate_rejected(self):
        def edit(frame):
            copy = frame.iloc[:1].copy()
            copy["AOV_tai_quan"] = "123456"
            return pd.concat([frame, copy], ignore_index=True)
        self.edit(edit)
        with self.assertRaisesRegex(DataQualityError, "mâu thuẫn"):
            load_clean(self.raw, {})

    def test_missing_unique_month_prevents_outputs(self):
        self.edit(lambda frame: frame.drop(index=25))
        with self.assertRaises(DataQualityError):
            run(self.project)
        self.assertFalse((self.project / "DataSach").exists())
        report = json.loads((self.project / "BaoCao/chat_luong_du_lieu.json").read_text(encoding="utf-8"))
        self.assertEqual(report["trang_thai"], "LOI")

    def test_derived_errors_recomputed_without_changing_business_total(self):
        def edit(frame):
            frame.loc[0, ["DT_tong", "bien_LN_van_hanh", "nam", "quy"]] = ["ERROR", "ERROR", "2099", "9"]
            return frame
        self.edit(edit)
        quality = {}
        _, fact = load_clean(self.raw, quality)
        self.assertEqual(fact.DT_tong.sum(), 341721504341)
        self.assertEqual(fact.iloc[0].nam, 2023)
        self.assertGreater(quality["doi_chieu_cong_thuc"]["DT_tong"]["so_dong_vuot_dung_sai"], 0)

    def test_only_infer_missing_aov_or_orders_when_other_components_exist(self):
        def edit(frame):
            frame.loc[0, "AOV_tai_quan"] = "ERROR"
            frame.loc[1, "don_nen_tang"] = ""
            return frame
        self.edit(edit)
        _, fact = load_clean(self.raw, {})
        self.assertEqual(fact.DT_tong.sum(), 341721504341)
        def missing_both(frame):
            frame.loc[0, ["DT_tai_quan", "AOV_tai_quan"]] = ["ERROR", "ERROR"]
            return frame
        self.edit(missing_both)
        with self.assertRaises(DataQualityError):
            load_clean(self.raw, {})

    def test_invalid_unique_row_is_not_replaced_with_zero(self):
        def edit(frame):
            frame.loc[0, "luong_VND"] = "ERROR"
            return frame
        self.edit(edit)
        with self.assertRaises(DataQualityError):
            load_clean(self.raw, {})


if __name__ == "__main__":
    unittest.main()
