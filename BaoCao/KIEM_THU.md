# Kết quả kiểm tra

Kiểm tra ngày 03/10/2026 trên Windows, Python 3.14.2, Pandas 3.0.6. Nguồn thô mô phỏng: CSV 02 và DULIEUTHO.csv; phạm vi 2023–2025.

| Nội dung | Kết quả |
|---|---|
| Chạy Script/Main.py | Thành công, 576 dòng, 20 cửa hàng, 36 tháng; một tệp sạch DULIEUSACH.csv |
| Python unittest | 13 kiểm thử đạt, gồm đối chiếu độc lập bằng Decimal và các trường hợp dữ liệu lỗi |
| Logic bộ lọc dashboard | 315 tổ hợp năm/quý/cửa hàng và đặt lại bộ lọc đạt, không có NaN/Infinity |
| Notebook | Chạy thành công toàn bộ 6 ô mã bằng Python; chưa kiểm tra giao diện kernel Jupyter |
| Dashboard trong Chrome | Dựng thành công ở 1440 × 1100, kiểm tra ảnh dashboard_preview.png |
| Word / PowerPoint | Mở lại bằng python-docx/python-pptx; cấu trúc ZIP hợp lệ, PowerPoint có 7 slide |
| Power BI | Đã chuẩn bị mô hình CSV, M, DAX, theme và hướng dẫn; chưa chạy kiểm tra bằng Power BI Desktop hoặc tạo PBIX |

Tổng doanh thu ba năm: **341.721.504.341 VND**, **2.875.801 đơn**. Tổng theo tháng, quý, năm, cửa hàng và kênh đều khớp với dữ liệu trước khi thêm lỗi. Riêng 2025: **146.385.764.418 VND**, **1.210.478 đơn**. YoY có từ 2024; CAGR/SSSG đã có đủ năm so sánh.

Nguồn cửa hàng: 29 dòng → 20 dòng sạch, bỏ 4 trùng và 5 lỗi. Nguồn vận hành: 597 dòng → 576 dòng sạch, bỏ 12 trùng và 9 lỗi. Tệp sạch có **47 cột**, **0 khóa trùng**, **0 ô thiếu**. Các tệp nguồn vẫn có lỗi mô phỏng sau chạy pipeline; hash nguồn không thay đổi.

Chi tiết sửa ô và bỏ trùng nằm trong `nhat_ky_lam_sach.csv`; nội dung gốc các dòng không thể phục hồi ở `dong_bi_loai.csv`. `doi_chieu_cong_thuc.csv` ghi chênh lệch cột tính sẵn trước khi tính lại, gồm lỗi ERROR và sai tổng được thêm có chủ đích. Trạng thái sau làm sạch nằm trong `chat_luong_du_lieu.json`, hash nguồn tại `../DataPhantich/manifest.json`.

Chạy lại từ thư mục dự án:

```powershell
& '..\.venv\Scripts\python.exe' -X utf8 -m unittest discover -s Tests -v
node Tests/test_dashboard.cjs
```

## Bổ sung menu và khu vực (06/10/2026)

### Kiểm tra bộ lọc bổ sung

Dashboard đạt 315 tổ hợp lọc cũ và 150 tổ hợp năm/khu vực/loại vị trí. Kiểm tra tìm kiếm không dấu, nhóm món kết hợp kênh bán, trạng thái lỗ và sắp lợi nhuận, thứ tự số lượng/tên/doanh thu, tìm khu vực, kết quả rỗng, reset toàn bộ và xuất CSV đúng phạm vi. Kiểm tra trên trình duyệt: tìm `ga ran` + kênh nền tảng trả đúng một món và giữ KPI vận hành theo bộ lọc chung. Không thay đổi dữ liệu nguồn hoặc công thức pipeline.

- 16 kiểm thử Python đạt, gồm đối chiếu doanh thu món với từng cửa hàng–tháng–kênh (dung sai 0,01 VND), kiểm tra khóa món, số lượng ước tính và tổng doanh thu/lợi nhuận/cửa hàng bình quân theo khu vực.
- 315 tổ hợp năm/quý/cửa hàng của dashboard đạt; tổng món khớp tổng vận hành cùng bộ lọc, kể cả cửa hàng chưa mở. Kiểm tra xuất CSV trang món giữ nhãn giả định, trang khu vực có thuộc tính vị trí.
- Mở dashboard trong trình duyệt, chuyển hai trang mới và kiểm tra bảng/nội dung cảnh báo. Tổng vận hành 2025 vẫn 146,39 tỷ VND. Nguồn DataGoc giữ nguyên.
- Chưa xác minh dữ liệu POS/địa chỉ thực; chưa chạy mô hình bổ sung trong Power BI Desktop. Word/slide cũ vẫn trình bày phạm vi vận hành; phụ lục mới là PhanTich_Menu_KhuVuc.md.
