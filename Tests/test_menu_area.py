import sys
import json
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Script'))
from pipeline import load_clean,build_tables
from menu_area import extend,NOTE

class MenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stores,fact = load_clean(ROOT/'DataGoc',{})
        cls.tables = extend(build_tables(stores,fact),ROOT)

    def test_reconcile_all_channels_and_years(self):
        sales = self.tables['Fact_Menu']
        summed = sales.groupby(['thang','store_id','kenh']).doanh_thu_phan_bo_VND.sum()
        expected = self.tables['Fact_Channel'].set_index(['thang','store_id','kenh']).doanh_thu
        np.testing.assert_allclose(summed.reindex(expected.index),expected,rtol=0,atol=.01)
        self.assertFalse(sales.duplicated(['thang','store_id','kenh','menu_id']).any())
        self.assertEqual(set(sales.co_so_du_lieu),{NOTE})

    def test_areas_partition_operation_without_multiplication(self):
        for year, group in self.tables['KPI_KhuVuc_Nam'].groupby('nam'):
            annual = self.tables['KPI_Nam'].set_index('nam').loc[year]
            self.assertAlmostEqual(group.DT_tong.sum(),annual.DT_tong,places=3)
            self.assertAlmostEqual(group.LN_van_hanh_mo_hinh.sum(),annual.LN_van_hanh_mo_hinh,places=3)
            self.assertAlmostEqual(group.CH_binh_quan.sum(),annual.CH_binh_quan)

    def test_quantity_is_estimate_from_reference_not_orders(self):
        merged = self.tables['Fact_Menu'].merge(self.tables['Dim_Menu'][['menu_id','gia_tham_chieu_VND']],on='menu_id',validate='many_to_one')
        expected = np.rint(merged.doanh_thu_phan_bo_VND/merged.gia_tham_chieu_VND).astype(int).clip(lower=1)
        pd.testing.assert_series_equal(merged.so_luong_uoc_tinh,expected,check_names=False)
        np.testing.assert_allclose(merged.so_luong_uoc_tinh*merged.gia_binh_quan_uoc_tinh_VND,merged.doanh_thu_phan_bo_VND,rtol=0,atol=.01)

if __name__ == '__main__': unittest.main()
