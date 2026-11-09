# Bộ dữ liệu CSV kiểm thử 2018–2020

`CSV_mau_2018_2020.csv` có 432 dòng tháng–cửa hàng cho 12 mã cửa hàng, từ 01/2018 đến 12/2020. Đây là dữ liệu tổng hợp để kiểm tra khả năng nạp CSV của dashboard, không phải số liệu kinh doanh KFC.

## Nạp vào dashboard

Mở `BaoCao/dashboard.html`, bấm **Nạp CSV**, rồi chọn tệp mẫu. Dashboard nhận các trường thời gian, cửa hàng, doanh thu, số đơn bắt buộc; khu vực, loại vị trí và lợi nhuận vận hành tùy chọn. Hỗ trợ tên cột tiếng Việt hoặc tiếng Anh thông dụng. Nếu không có lợi nhuận vận hành, dashboard tạm ước tính bằng 12% doanh thu để vẫn hiển thị biểu đồ; hãy đưa trường lợi nhuận thực vào tệp khi muốn phân tích khoản này.

Dữ liệu nhập chỉ tồn tại trong phiên dashboard vừa nạp. Quay lại trang dashboard ban đầu để trở về dữ liệu đang đóng gói trong dự án.
