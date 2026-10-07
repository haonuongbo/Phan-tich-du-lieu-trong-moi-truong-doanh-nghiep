# HỆ THỐNG PHÂN TÍCH DOANH THU KFC TP.HCM

MÔ PHỎNG — Không phản ánh kết quả kinh doanh thực tế của KFC.

## 1. Mục tiêu và phạm vi

Thiết kế hệ thống phân tích doanh thu KFC tại TP.HCM theo tài liệu THIẾT KẾ HỆ THỐNG.docx: quản lý nguồn → làm sạch bằng Pandas → tính KPI → cung cấp dữ liệu Power BI → báo cáo và đề xuất.

Nguồn cửa hàng: 02_KFC_TPHCM_cua_hang_mo_phong.csv. Nguồn vận hành: DULIEUTHO.csv. Phạm vi 2023-01-01 đến 2025-12-01; 576 bản ghi cửa hàng–tháng, 20 cửa hàng hư cấu.

Nguồn vận hành DULIEUTHO.csv là CSV UTF-8 đúng định dạng, chuyển từ dữ liệu Excel được cung cấp. Hai nguồn thô có lỗi mô phỏng để thực hành làm sạch; không lấy KPI có sẵn làm nguồn.

## 2. Kiến trúc và xử lý dữ liệu

Pipeline đọc hai nguồn thô trong DataGoc. DataSach/DULIEUSACH.csv là một tệp sạch duy nhất, gộp vận hành và thuộc tính cửa hàng. DataPhantich chứa mô hình sao và bảng KPI dùng cho dashboard.

Mỗi dòng Fact_Operation là một cửa hàng trong một tháng; khóa ghép store_id + thang. Fact_Channel có thêm khóa kenh. Chiều thời gian liên tục theo ngày, quan hệ một–nhiều, lọc một chiều từ dimension sang fact.

Nguồn có 29 dòng cửa hàng và 597 dòng vận hành. Loại 4 + 12 dòng trùng và 5 + 9 dòng lỗi không thể phục hồi. Xem nhat_ky_lam_sach.csv và dong_bi_loai.csv.

CSV ngày nguồn dùng tháng/ngày/năm, chuẩn hóa thành YYYY-MM-DD. Tiền là VND; tỷ lệ lưu 0–1. Tính lại doanh thu = số đơn × AOV từng kênh; đối chiếu với cột có sẵn, dung sai 1 VND và 1e-8 cho tỷ lệ do làm tròn nguồn.

Chất lượng sau làm sạch: DAT. Đối chiếu 576 dòng sạch; cột dẫn xuất sai hoặc thiếu được tính lại từ số đơn, AOV và chi phí. Có 661 lượt sửa/chuẩn hóa ô có nhật ký; không điền số 0 thay cho dữ liệu thiếu.

## 3. Định nghĩa KPI

Doanh thu = tổng doanh thu ba kênh. Tăng trưởng kỳ = doanh thu kỳ này / kỳ trước − 1, chỉ tính khi hai kỳ đủ tháng. YoY so cùng kỳ năm trước. CAGR = (tổng doanh thu năm cuối / năm đầu)^(1 / khoảng cách năm) − 1; chỉ dùng năm đủ 12 tháng.

Cửa hàng bình quân = số bản ghi cửa hàng–tháng / số tháng trong kỳ. Doanh thu/cửa hàng = tổng doanh thu / cửa hàng bình quân. Đồng thời xuất số cửa hàng đầu kỳ, cuối kỳ và trung bình hai mốc để đối chiếu; không cộng số cửa hàng qua các tháng.

Lợi nhuận gộp = doanh thu − giá vốn. Lợi nhuận vận hành mô hình = lợi nhuận gộp − phí nền tảng − phí nhượng quyền − lương − thuê − chi phí khác − khấu hao. Biên vận hành = tổng lợi nhuận vận hành / tổng doanh thu.

AOV = tổng doanh thu / tổng đơn. Tỷ trọng online = (doanh thu nền tảng + online riêng) / tổng doanh thu. Không lấy trung bình cộng AOV hoặc biên lợi nhuận của các dòng.

SSSG chỉ so cùng tập cửa hàng có đủ 12 tháng ở cả hai năm. Thiếu kỳ trước hoặc mẫu số bằng 0: để trống, không suy diễn bằng 0%. Không có lợi nhuận sau thuế, tài sản/vốn, khách hàng định danh, dữ liệu ngành nên chưa tính biên ròng, ROA/ROE, tỷ lệ quay lại hoặc thị phần.

## 4. Kết quả mô phỏng năm 2025

Doanh thu 146,39 tỷ VND; 1.210.478 đơn; cửa hàng bình quân 20; doanh thu/cửa hàng 7,32 tỷ VND/năm.

Lợi nhuận vận hành mô hình 18,61 tỷ VND; biên vận hành 12,71%; AOV 120.932 VND/đơn; tỷ trọng doanh thu online 41,96%.

YoY doanh thu: 25,43%. CAGR toàn khoảng đủ năm: 36,44%. Tăng trưởng cùng cửa hàng: 8,46%.

Tháng có doanh thu cao nhất năm: 12/2025, đạt 13,59 tỷ VND. Cửa hàng đóng góp doanh thu cao nhất: SIM005, đạt 10,71 tỷ VND.

Có 5 cửa hàng lỗ vận hành cả năm. Biên vận hành thấp nhất: SIM020 (-41,91%). Đây là tín hiệu mô tả, chưa chứng minh nguyên nhân.

## 5. Định hướng quyết định trong bài mô phỏng

Ưu tiên rà soát cơ cấu giá vốn, thuê mặt bằng và nhân sự tại SIM020; so doanh thu và từng khoản chi phí theo tháng trước khi chọn biện pháp. Theo dõi số cửa hàng lỗ và biên vận hành ở kỳ tiếp theo.

Tách nền tảng giao hàng và online riêng khi xem đóng góp doanh thu; cần phân bổ thêm chi phí theo kênh trước khi kết luận kênh nào sinh lợi cao hơn. Chưa có cơ sở nhân quả để khẳng định tăng online làm tăng lợi nhuận.

Chưa có kế hoạch KPI được phê duyệt nên trạng thái chỉ mô tả biến động, không tự gán đạt/không đạt mục tiêu. Chuỗi 2023–2025 cho phép so YoY/CAGR và quan sát mùa vụ; chưa có dữ liệu ngành cùng phạm vi để so vị thế thị trường.

## 6. Dashboard và vận hành

Gói PowerBI gồm hàm Power Query, mã DAX, theme và hướng dẫn bốn trang: tổng quan, xu hướng, hiệu quả cửa hàng, chi phí/lợi nhuận. Người dùng nhập vào Power BI Desktop và lưu PBIX; gói này chưa chứa tệp PBIX đã dựng hoặc đã kiểm tra bằng Power BI Desktop.

BaoCao/dashboard.html là bản xem tương tác độc lập có lọc năm/quý/cửa hàng và xuất CSV theo bộ lọc; mở trực tiếp trong trình duyệt, không cần mạng. Đây là bản xem bổ trợ cho việc kiểm tra và thuyết trình.

Chạy lại Script/Main.py khi cập nhật nguồn. Đọc chat_luong_du_lieu.json trước khi Refresh Power BI. Nếu trạng thái LOI, đầu ra cũ không đại diện cho lần cập nhật thất bại. Chạy bộ kiểm thử trong Tests trước khi thay đổi công thức.

## 7. Giới hạn kết luận

MÔ PHỎNG — Không phản ánh kết quả kinh doanh thực tế của KFC.

Chưa xác minh cơ sở doanh thu gộp/thuần và thuế VAT của mô hình. Không gọi lợi nhuận vận hành là lợi nhuận ròng. Không suy rộng quy mô 20 cửa hàng hư cấu thành quy mô thực tế của KFC TP.HCM.

Bộ nguồn không có ngày đóng cửa hay quận/huyện; giả định cửa hàng hoạt động liên tục từ tháng mở. Khi có đóng cửa hoặc hoạt động giữa tháng cần mở rộng mô hình và quy tắc tính cửa hàng bình quân.

Doanh thu tăng, nếu có, chưa đủ kết luận hiệu quả kinh doanh. Cần đối chiếu doanh thu/cửa hàng, biên vận hành, cùng tập cửa hàng và thị trường có phạm vi tương đương.

