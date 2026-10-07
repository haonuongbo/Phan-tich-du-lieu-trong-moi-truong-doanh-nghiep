# Kết nối và thiết kế Power BI

Gói này cung cấp dữ liệu, Power Query, DAX và bố cục để tạo báo cáo trong Power BI Desktop. **Chưa có tệp PBIX đã dựng và chưa kiểm tra thực thi M/DAX trong Power BI Desktop.** Bản xem tương tác chạy ngay nằm ở `../BaoCao/dashboard.html`.

## Nạp dữ liệu

1. Chạy `Script/Main.py`; kiểm tra `BaoCao/chat_luong_du_lieu.json` có `trang_thai = DAT`.
2. Trong Power BI Desktop, chọn **Transform data → Manage Parameters → New Parameter**. Tạo `DataFolder`, kiểu Text, giá trị là đường dẫn tuyệt đối tới **DataPhantich** của dự án này.
3. Tạo Blank Query → Advanced Editor, dán `fnReadCSV.pq`, đặt tên query `fnReadCSV`.
4. Tạo Blank Query khác tên `Model`, dán `Model.pq`; bỏ Enable load cho query này.
5. Tạo bốn query: `Dim_Store` với công thức `= Model[Dim_Store]`, `Dim_Date = Model[Dim_Date]`, `Fact_Operation = Model[Fact_Operation]`, `Fact_Channel = Model[Fact_Channel]`.
6. Close & Apply. Bỏ các quan hệ tự nhận diện không đúng trước khi tạo quan hệ bên dưới. Không dùng Folder import gộp tất cả CSV: các bảng khác độ hạt, gộp sẽ đếm trùng.
7. Nếu cần đối chiếu các bảng KPI đã tổng hợp, tạo query riêng `= Model[KPI_Nam]` v.v. Giữ chúng **không có quan hệ** với mô hình chính; không dùng chúng cho visual cần lọc cửa hàng/thời gian động.

## Quan hệ

| Phía một | Phía nhiều | Hướng lọc |
|---|---|---|
| Dim_Store[store_id] | Fact_Operation[store_id] | Single |
| Dim_Date[ngay] | Fact_Operation[thang] | Single |
| Dim_Store[store_id] | Fact_Channel[store_id] | Single |
| Dim_Date[ngay] | Fact_Channel[thang] | Single |

Không nối hai bảng fact trực tiếp. Chọn Dim_Date → Mark as date table → cột `ngay`; tắt Auto date/time cho file này. Các cột ngày phải là Date. Fact chứa ngày đầu tháng, vì vậy chỉ cho phép lọc ở cấp **tháng/quý/năm**, tránh slicer ngày giữa tháng.

Tạo từng measure trong `Measures.dax` bằng New measure. File này chứa nhiều định nghĩa, không dán toàn bộ vào một measure. Định dạng số tiền VND, tỷ lệ dạng Percentage. Tên kỹ thuật không dấu giúp sao chép; đổi tiêu đề visual sang tiếng Việt có dấu.

## Bố cục bốn trang

Canvas 16:9, nền `#F6F4F1`, màu nhấn `#B51232`; nhập `KFC_Theme.json` qua View → Themes → Browse for themes. Trên mọi trang đặt nhãn **“DỮ LIỆU MÔ PHỎNG — Không phản ánh kết quả thực tế của KFC”**.

| Trang | Visual và trường | Bộ lọc |
|---|---|---|
| Tổng quan | Card: Doanh thu, Loi nhuan van hanh, Bien loi nhuan van hanh, AOV, Cua hang binh quan, Doanh thu moi cua hang. Donut: Fact_Channel[kenh] + Doanh thu kenh | Dim_Date[nam], Dim_Date[quy], Dim_Store[store_id] |
| Xu hướng | Line: Dim_Date[nam_thang] + Doanh thu. Line riêng: Tang truong MoM. Matrix theo tháng với doanh thu, LN, biên LN, YoY | Đồng bộ bộ lọc với trang tổng quan |
| Hiệu quả cửa hàng | Bar: Dim_Store[store_id] + Doanh thu, sắp giảm dần. Matrix: doanh thu, LN, biên LN, số đơn, AOV theo cửa hàng | Năm, quý; tô đỏ lợi nhuận âm |
| Chi phí và lợi nhuận | Card LN gộp/vận hành; stacked column từng khoản SUM giá vốn, lương, thuê, phí nền tảng, nhượng quyền, khác, khấu hao theo tháng; matrix chi phí | Năm, quý, cửa hàng |

Biểu đồ kênh chỉ thể hiện doanh thu/đơn. Không đặt slicer kênh toàn trang cho các card vận hành vì nguồn chưa phân bổ chi phí theo kênh. Có thể tắt tương tác từ donut kênh sang các card vận hành.

Nguồn sau làm sạch gồm 2023–2025. YoY có từ 2024, CAGR/SSSG có trong bảng KPI xuất sẵn để đối chiếu toàn bộ nguồn; không phải measure đáp ứng mọi bộ lọc. Năm 2023 thiếu kỳ trước thì hiển thị “Chưa đủ dữ liệu”, không thay BLANK bằng 0%. MoM chỉ tính ở hàng tháng.

## Đối chiếu trước khi lưu PBIX

Lọc năm 2025: doanh thu **146.385.764.418 VND**, **1.210.478 đơn**, **20 cửa hàng bình quân**. Không lọc năm: doanh thu toàn chuỗi **341.721.504.341 VND**, **2.875.801 đơn**. Biên vận hành xấp xỉ **12,7105%**; lợi nhuận vận hành tính lại từ tỷ lệ nguồn nên có chênh lệch làm tròn nhỏ so với cột gốc.

Thử lọc tháng 1/2025 và SIM001; đối chiếu dòng trong `DataSach/DULIEUSACH.csv`. Tổng doanh thu ba kênh phải bằng Doanh thu, AOV phải là tổng doanh thu/tổng đơn. Lưu báo cáo thành `KFC_TPHCM.pbix` sau khi kiểm tra.

Tài liệu kỹ thuật: [mô hình sao](https://learn.microsoft.com/power-bi/guidance/star-schema), [bảng ngày](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables), [DATEADD](https://learn.microsoft.com/en-us/dax/dateadd-function-dax).
