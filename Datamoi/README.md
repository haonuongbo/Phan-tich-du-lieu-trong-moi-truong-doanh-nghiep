# Dataset bán hàng mô phỏng và thực đơn công khai

Dataset này phục vụ thực hành làm sạch, phân tích xu hướng và trực quan hóa bán hàng. Phần bán hàng và danh mục cửa hàng kế thừa mô phỏng trong DataGoc; phần thực đơn có nguồn công khai. Không có dữ liệu nội bộ thật của KFC về số đơn, doanh thu hoặc chi phí trong bộ này.

## Bắt đầu với tệp nào?

| Tệp | Số dòng | Dùng để làm gì? |
|---|---:|---|
| DULIEUTHO.csv | 597 | Bản thô bán hàng, giữ các giá trị và lỗi gốc của những cột được chọn |
| DULIEUSACH.csv | 576 | Bản sạch chính: mỗi dòng là một cửa hàng mô phỏng trong một tháng |
| CUAHANG_THO.csv | 29 | Danh mục cửa hàng nguồn, chưa chuẩn hóa |
| CUAHANG_SACH.csv | 20 | Danh mục 20 cửa hàng mô phỏng; mã SIM không phải mã cửa hàng KFC thật |
| MENU_CONGKHAI_THO.csv | 8 | Mẫu thực đơn công khai; giá còn ở dạng chuỗi như 37.000₫ |
| MENU_CONGKHAI_SACH.csv | 8 | Cùng mẫu thực đơn, chuyển giá sang số VND |
| NHATKY_LAMSACH.csv | 1.861 | Các sự kiện chuẩn hóa, phục hồi, tính lại và loại dòng; số sự kiện không phải số lỗi |
| TUDIEN_DULIEU.csv | 82 | Ý nghĩa, kiểu dữ liệu và nguồn gốc của từng cột theo từng tệp |
| manifest.json | — | Phạm vi, nguồn, số dòng, kiểm tra và mã băm tệp |

Tất cả CSV dùng UTF-8 có BOM, dấu phẩy phân cột, dấu chấm thập phân. Khi nhập vào Power BI/Excel, chọn đúng kiểu ngày và số theo từ điển. Bản thô chủ ý giữ định dạng không đồng nhất; không tính tổng trực tiếp trước khi xử lý. Giá trị trong CSV là ảnh chụp kết quả, không có công thức tự tính lại khi sửa đầu vào.

## Dữ liệu có nguồn và dữ liệu mô phỏng

- Các bảng bán hàng/cửa hàng (nhãn nguồn `loai_du_lieu=MO_PHONG` ở bản sạch): toàn bộ doanh thu, số đơn, AOV, mã cửa hàng, ngày mở và phạm vi địa lý trong các bảng bán hàng/cửa hàng. Ngày mở là giả định của nguồn, không xác nhận ngày khai trương ngoài thực tế.
- Các bảng `MENU_CONGKHAI_*`: tên món, nhóm món và giá hiển thị được tra cứu từ [trang đặt hàng KFC Việt Nam](https://kfcvietnam.com.vn/order/delivery), ngày 11/10/2026. Nội dung được đọc qua chỉ mục tìm kiếm của trang chính thức, không phải ảnh chụp giá tại bước thanh toán. Mẫu chỉ gồm 8 món, không phải toàn bộ thực đơn; chưa chọn nhà hàng cụ thể.
- `ma_mau_thu_thap` là mã WEB do người xây dựng bộ dữ liệu đặt để truy vết, không phải mã sản phẩm KFC.
- `ngay_tra_cuu` là ngày kiểm tra nguồn, không xác nhận ngày bắt đầu hiệu lực của giá. Dữ liệu công khai có thể thay đổi hoặc chỉ mục có độ trễ.

Hai phần có giai đoạn khác nhau. Không nối thực đơn 2026 vào số bán mô phỏng 2023–2025 để tuyên bố doanh thu lịch sử hay số lượng món thực tế. Không có khóa để gán doanh số cho từng món vì nguồn DataGoc không cung cấp điều đó.

## Những gì đã giữ và đã bỏ

Giữ tháng/năm/quý, mã cửa hàng mô phỏng, thành phố, số đơn ba kênh, AOV ba kênh, doanh thu ba kênh, tổng đơn, tổng doanh thu, AOV tổng và tỷ trọng doanh thu online. Giữ nhãn mô phỏng, phiên bản và dòng nguồn để kiểm tra.

Bỏ giá vốn, tỷ lệ giá vốn, phí nền tảng, phí nhượng quyền, lương, thuê, chi phí khác, khấu hao, lợi nhuận gộp, lợi nhuận vận hành và biên lợi nhuận. Bỏ các tham số cơ sở không cần cho danh mục cửa hàng. Không đưa thông tin vị trí giả định hoặc phân bổ món từ DataPhantich sang bộ mới.

Tên các cột bị loại chỉ được liệt kê trong manifest để mô tả thay đổi; không còn giá trị chi phí hay lợi nhuận trong các CSV mới.

## Cách tạo bản thô và bản sạch

1. Đọc trực tiếp hai tệp `02_KFC_TPHCM_cua_hang_mo_phong.csv` và `DULIEUTHO.csv` trong DataGoc. Bản thô mới là bản chọn cột, không phải bản sao nguyên tệp. Giữ nguyên nội dung ô được chọn, thứ tự dòng, lỗi và bản ghi trùng; chỉ bổ sung thông tin truy vết.
2. Chuẩn hóa khoảng trắng, mã cửa hàng và tên thành phố. Chuẩn hóa ngày theo quy ước hiện có của dự án: ngày có dấu `/` kiểu tháng/ngày/năm, hoặc năm/tháng/ngày; xuất ISO `YYYY-MM-DD`. Đây là quy ước của bộ nguồn, không phải suy đoán áp dụng cho mọi tệp Việt Nam.
3. Chuyển số có ký hiệu tiền, khoảng trắng hoặc dấu phân cách sang số. Phục hồi số đơn hoặc AOV còn thiếu chỉ khi có đủ hai thành phần còn lại cùng dòng để suy ra; không tự điền doanh số ngẫu nhiên.
4. Loại dòng rỗng, mã/ngày/phạm vi sai, số đơn âm hoặc không nguyên, AOV không hợp lệ, mã không thuộc danh mục hoặc hoạt động trước tháng mở giả định.
5. Tính lại năm/quý từ tháng; doanh thu kênh = số đơn × AOV; tổng đơn và doanh thu = tổng ba kênh; AOV tổng = doanh thu / số đơn; tỷ trọng online = (doanh thu nền tảng + online riêng) / tổng doanh thu.
6. Bỏ dòng trùng sau chuẩn hóa, phục hồi và tính lại trên các cột được giữ; nếu cùng khóa còn giá trị mâu thuẫn thì dừng để kiểm tra, không chọn tùy ý.
7. Ghi nhật ký thay đổi và kiểm tra số tháng hoạt động dự kiến. Không thêm lỗi giả vào thực đơn: bản thô chỉ giữ biểu diễn nguồn và bản sạch chuyển kiểu dữ liệu.

## Kết quả làm sạch và kiểm tra

- Bán hàng: 597 dòng = 576 dòng sạch + 14 dòng trùng sau xử lý + 7 dòng loại vì không hợp lệ.
- Danh mục: 29 dòng = 20 dòng sạch + 6 dòng trùng sau chọn cột/chuẩn hóa + 3 dòng không hợp lệ. Số này không nhất thiết giống nhật ký của quy trình cũ vì phạm vi cột đã thay đổi.
- Bản sạch có 36 tháng, từ 01/2023 đến 12/2025; lần lượt 12, 16 và 20 cửa hàng hoạt động trong các năm. 576 khóa tháng–cửa hàng duy nhất và đủ theo ngày mở mô phỏng.
- Không có ô thiếu ở các bảng sạch; số đơn là số nguyên không âm; AOV dương; doanh thu bằng tổng ba kênh; tỷ trọng online nằm trong [0,1].
- Tổng doanh thu mô phỏng theo năm: 78.631.832.128 đồng (2023), 116.703.907.795 đồng (2024), 146.385.764.418 đồng (2025). Đây là kiểm soát bảo toàn dữ liệu nguồn sau làm sạch, không phải số liệu KFC thực tế.

## Phân tích phù hợp

Có thể phân tích tăng trưởng doanh thu mô phỏng, số đơn, AOV, cơ cấu kênh, khác biệt cửa hàng và mùa vụ trong kịch bản. Có thể phân tích riêng giá và nhóm món của mẫu thực đơn công khai. Không dùng bộ này để kết luận lợi nhuận, hợp đồng thuê, hiệu quả tài chính thực tế của KFC hoặc món bán chạy ngoài thực tế.

Khi tổng hợp AOV hoặc tỷ trọng, tính từ tổng doanh thu và tổng số đơn tương ứng; không cộng tỷ lệ hoặc lấy trung bình đơn giản các AOV. Nối DULIEUSACH với CUAHANG_SACH bằng `store_id`, quan hệ nhiều–một. Không cộng bản thô với bản sạch, không cộng lại doanh thu tổng cùng doanh thu thành phần.


Cập nhật 11/10/2026: bỏ cột phân loại trùng lặp `ban_chat` khỏi sáu bảng dữ liệu; giữ nguyên các giá trị khác, nhãn nguồn và mô tả nguồn gốc.
