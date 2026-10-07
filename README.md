# Hệ thống phân tích doanh thu KFC TP.HCM

Hệ thống thực hành dữ liệu mô phỏng: **nguồn thô → làm sạch → KPI → dashboard và Power BI**.

## Hai tệp nguồn thô

| Nguồn trong DataGoc | Dòng thô | Dòng hợp lệ sau làm sạch | Bỏ trùng | Loại lỗi |
|---|---:|---:|---:|---:|
| 02_KFC_TPHCM_cua_hang_mo_phong.csv | 29 | 20 cửa hàng | 4 | 5 |
| DULIEUTHO.csv | 597 | 576 cửa hàng–tháng | 12 | 9 |

DULIEUTHO.csv là **CSV UTF-8 thực sự**, chuyển từ dữ liệu Excel người dùng cung cấp, gồm 2023–2025. Các lỗi được thêm có chủ đích để minh họa làm sạch: dòng trùng, ERROR/#VALUE!, ô thiếu, số âm, tỷ lệ >100%, sai mã cửa hàng, ngày không hợp lệ, năm/quý sai, số có dấu phân cách hoặc đơn vị và cách viết không đồng nhất.

Sau lần chuẩn bị nguồn này, pipeline chỉ đọc DataGoc, không sửa nguồn khi chạy. Dữ liệu hoàn toàn mô phỏng, không phản ánh kết quả thực tế của KFC.

## Một tệp sạch duy nhất

**DataSach/DULIEUSACH.csv** có 576 dòng, khóa `store_id + thang`, nối thuộc tính cửa hàng vào dữ liệu vận hành. Không còn bản ghi trùng, lỗi ERROR hoặc ô bắt buộc thiếu. Ngày chuẩn YYYY-MM-DD, tiền VND, tỷ lệ 0–1. Giữ `nguon_dong_van_hanh`, `nguon_dong_cua_hang` để đối chiếu nguồn.

`ty_le_gia_von_co_so` và `khau_hao_co_so_VND` là thuộc tính cơ sở từ bảng cửa hàng; `ty_le_gia_von` và `khau_hao_VND` là số liệu vận hành tháng. Không thay số vận hành bằng tham số cơ sở.

## Quy tắc làm sạch

1. Bỏ dòng rỗng; chuẩn hóa khoảng trắng, mã SIM, tên TP.HCM, nhãn mô phỏng và phiên bản.
2. Chuẩn hóa ngày: dấu `/` theo tháng/ngày/năm, ISO YYYY-MM-DD hoặc YYYY/MM/DD, dấu `-` DD-MM-YYYY. Không đoán ngày sai như 31/31/2025.
3. Đổi số có phân cách hàng nghìn, đơn vị VND/đ và tỷ lệ phần trăm thành số. Phân biệt `0,435` là 0.435 và `120,932 VND` là 120932.
4. Nếu AOV thiếu/sai kiểu nhưng có doanh thu kênh và số đơn hợp lệ, phục hồi AOV = DT/đơn. Nếu số đơn thiếu nhưng có DT và AOV, chỉ phục hồi khi kết quả là số nguyên. Không suy đoán lương, thuê, chi phí hoặc tỷ lệ thiếu.
5. Năm/quý suy ra từ tháng; doanh thu, giá vốn, phí, lợi nhuận và các tỷ lệ dẫn xuất tính lại từ dữ liệu cơ sở.
6. Loại dòng lỗi không thể phục hồi; giữ giá trị gốc và lý do trong `BaoCao/dong_bi_loai.csv`. Bỏ trùng sau chuẩn hóa và tính lại. Khóa trùng có số liệu cơ sở mâu thuẫn thì dừng, không tự chọn dòng.
7. Kiểm tra đủ cửa hàng–tháng từ tháng mở trong khoảng nguồn. Nếu loại một dòng duy nhất dẫn đến thiếu tháng, dừng xuất kết quả thay vì điền 0.

Mọi thay đổi có nhật ký tại **BaoCao/nhat_ky_lam_sach.csv**. Số lượt sửa gồm chuẩn hóa định dạng ngày, không chỉ lỗi nghiệp vụ. `chat_luong_du_lieu.json` có trạng thái DAT sau làm sạch; `manifest.json` ghi SHA-256 nguồn. Nếu lần chạy thất bại, trạng thái LOI và không có đầu ra mới; cần xem trạng thái trước khi Refresh.

## Chạy và kiểm thử

Từ thư mục dự án có Script và DataGoc:

```powershell
& '..\.venv\Scripts\python.exe' -X utf8 Script/Main.py
& '..\.venv\Scripts\python.exe' -X utf8 -m unittest discover -s Tests -v
node Tests/test_dashboard.cjs
```

Hoặc chạy Run.ps1. Khi mang sang máy khác, cài Python 3.11+, tạo `.venv`, cài `requirements.txt`, chạy `Script/Main.py`. Notebook `Notebooks/PhanTich_KFC.ipynb` dùng cùng Python; cài ipykernel nếu VS Code yêu cầu.

## Đầu ra cần thiết

| Thư mục | Nội dung |
|---|---|
| DataGoc | Hai CSV thô có lỗi mô phỏng |
| DataSach | DULIEUSACH.csv duy nhất |
| DataPhantich | Dimension, fact và KPI tháng/quý/năm/cửa hàng, manifest nguồn |
| BaoCao | Dashboard HTML, báo cáo Word/Markdown, slide, nhật ký làm sạch, dòng bị loại và kiểm tra chất lượng |
| PowerBI | Power Query, DAX, theme, hướng dẫn mô hình; chưa có PBIX |
| Script / Notebooks / Tests | Mã chạy, notebook từng bước và kiểm thử |

Mở `BaoCao/dashboard.html` để xem kết quả và lọc năm/quý/cửa hàng. Dashboard sử dụng dữ liệu sau làm sạch. Hướng dẫn Power BI: `PowerBI/HUONG_DAN.md`.

## Giới hạn phân tích

## Bổ sung menu và khu vực giả định

Dashboard có thêm hai trang **Menu giả định** và **Khu vực giả định**, cùng bộ lọc năm/quý/cửa hàng. Chi tiết kết quả, đề xuất tăng doanh thu và giới hạn kết luận: `BaoCao/PhanTich_Menu_KhuVuc.md`. Báo cáo Word/slide cũ là phần vận hành; Markdown này là phụ lục mới.

Nguồn hiện có không chứa POS theo món hoặc địa chỉ. `Script/gia_dinh_menu_khu_vuc.json` khai báo công khai 8 món học tập, giá tham chiếu, trọng số cơ cấu món và vị trí hư cấu. Các con số này là **phân bổ giả định**, không phải doanh thu thực tế của món hoặc sở thích khách hàng. Tổng phân bổ đối chiếu với vận hành theo cửa hàng–tháng–kênh; nguồn DataGoc không bị thay đổi. DULIEUSACH vẫn có độ hạt cửa hàng–tháng và một tệp sạch duy nhất.

Đầu ra mới: Dim_Menu, Fact_Menu, KPI_Mon_Nam, KPI_NhomMon_Nam, KPI_KhuVuc_Nam, KPI_LoaiViTri_Nam. Dim_Store và DULIEUSACH có thêm thuộc tính vị trí giả định. Không cộng doanh thu món với doanh thu vận hành. Kết nối Power BI bổ sung: `PowerBI/MENU_KHU_VUC.md`.

### Giới hạn nguồn vận hành

### Bộ lọc và tìm kiếm dashboard

- Bộ lọc chung: năm, quý, cửa hàng, khu vực giả định, loại vị trí và tìm cửa hàng/khu vực không dấu. Áp dụng nhất quán cho KPI, các bảng và kỳ so sánh MoM/YoY.
- Cửa hàng: lọc có lãi/lỗ/hòa vốn; sắp theo doanh thu, lợi nhuận, biên lợi nhuận hoặc mã.
- Menu: tìm tên/mã món không dấu, chọn nhóm món và kênh; sắp theo doanh thu, số lượng hoặc tên. Tỷ trọng tính trong menu đã lọc; lọc món không thay đổi KPI vận hành phía trên.
- Khu vực: tìm tên khu vực và sắp theo doanh thu/cửa hàng, doanh thu, lợi nhuận, biên lợi nhuận hoặc tên. Tổng quan có thêm sắp xếp bảng tháng.
- Đặt lại xóa toàn bộ bộ lọc/tìm kiếm và khôi phục thứ tự mặc định. Xuất CSV giữ bộ lọc chung và bộ lọc riêng của trang hiện tại. Lọc riêng tại bảng không thay đổi KPI phía trên, như chú thích trên trang.

Chuỗi 2023–2025 hiện tính được YoY 2024/2025, CAGR và cùng tập cửa hàng. Năm đầu không có YoY. AOV và biên lợi nhuận là tỷ số của tổng. Lợi nhuận là vận hành mô hình, chưa phải lợi nhuận ròng. Chưa có dữ liệu thị trường, khách hàng định danh hoặc ngày đóng cửa; giả định hoạt động liên tục từ tháng mở.
