"""Chạy: python Script/Main.py (đường dẫn không phụ thuộc thư mục hiện tại)."""
from pipeline import run
from presentation import generate


if __name__ == "__main__":
    tables, quality = run()
    generate(tables, quality)
    print("HOÀN TẤT — DỮ LIỆU MÔ PHỎNG")
    print(f"{quality['so_dong_sach']} dòng, {quality['so_cua_hang']} cửa hàng, {quality['so_thang']} tháng.")
    print("Tệp sạch: DataSach/DULIEUSACH.csv; nhật ký: BaoCao/nhat_ky_lam_sach.csv")
    print(tables['KPI_Nam'][['nam', 'DT_tong', 'YoY_doanh_thu', 'CH_binh_quan', 'bien_LN_van_hanh']].to_string(index=False))
    print("Kết quả: DataSach, DataPhantich, BaoCao. Dashboard: BaoCao/dashboard.html")
