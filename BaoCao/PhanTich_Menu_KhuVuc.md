# Phân tích menu và khu vực — năm 2025

**KỊCH BẢN GIẢ ĐỊNH, KHÔNG PHẢI SỐ BÁN THEO MÓN HOẶC VỊ TRÍ THỰC TẾ.**

Nguồn 02 và DULIEUTHO không chứa giao dịch POS theo món, khách hàng định danh hoặc địa chỉ. Phần bổ sung minh họa cách phân tích khi có những trường này. Tổng doanh thu vận hành giữ nguyên; không coi phân bổ là dữ liệu thu thập được.

## Doanh thu các món trong menu học tập

| Món giả định | Nhóm | Doanh thu phân bổ (tỷ VND) | Tỷ trọng DT | Số lượng ước tính |
|---|---|---:|---:|---:|
| Combo nhóm | Combo | 24,28 | 16,59% | 110,377 |
| Combo một người | Combo | 24,28 | 16,59% | 269,814 |
| Gà rán truyền thống (1 phần) | Gà | 19,75 | 13,49% | 438,808 |
| Gà sốt cay (1 phần) | Gà | 19,75 | 13,49% | 394,923 |
| Cơm gà | Burger và cơm | 17,75 | 12,12% | 354,957 |
| Burger gà | Burger và cơm | 17,75 | 12,12% | 394,393 |
| Nước giải khát | Món phụ và đồ uống | 11,42 | 7,80% | 761,046 |
| Khoai tây chiên | Món phụ và đồ uống | 11,42 | 7,80% | 456,637 |

## Khách hàng có thể ưu ái loại hình nào?

Chưa kết luận được từ nguồn hiện có. Tỷ trọng doanh thu phụ thuộc giá, số lượng và trọng số được đặt trước; tỷ trọng số lượng ở đây cũng là ước tính, không phải khảo sát sở thích. Combo được tính nguyên gói, không đếm lại thành phần. Không dùng số lượng món để suy ra số khách hoặc số đơn.

Giả thuyết để thử: combo nhóm ở điểm thương mại; cơm/burger hoặc combo một người ở văn phòng và gần trường học; gói mang về ở khu dân cư. Thu thập POS gồm mã đơn, mã món, số lượng, giá, chiết khấu, doanh thu thuần, cửa hàng, thời gian và kênh để kiểm chứng. Xem số đơn có món / tổng số đơn và số lượng bán song song với doanh thu; bổ sung khảo sát nếu muốn đo sở thích.

## Khu vực và doanh thu

| Khu vực giả định | DT (tỷ) | CH bình quân | DT/CH/năm (tỷ) | LN vận hành (tỷ) | Biên LN |
|---|---:|---:|---:|---:|---:|
| Khu vực Quận 1 | 18,44 | 2,00 | 9,22 | 4,02 | 21,78% |
| Khu vực Quận 10 | 17,95 | 2,00 | 8,98 | 3,99 | 22,23% |
| Khu vực Quận 3 | 16,92 | 2,00 | 8,46 | 2,92 | 17,27% |
| Khu vực Thủ Đức | 22,27 | 3,00 | 7,42 | 2,84 | 12,78% |
| Khu vực Gò Vấp | 22,13 | 3,00 | 7,38 | 2,17 | 9,81% |
| Khu vực Bình Thạnh | 13,45 | 2,00 | 6,72 | 1,88 | 13,97% |
| Khu vực Tân Bình | 19,53 | 3,00 | 6,51 | 1,20 | 6,14% |
| Khu vực Quận 5 | 5,79 | 1,00 | 5,79 | 0,38 | 6,64% |
| Khu vực Quận 7 | 9,91 | 2,00 | 4,96 | -0,80 | -8,09% |

Danh sách cửa hàng–khu vực–loại vị trí nằm trong Dim_Store.csv và trang Khu vực giả định của dashboard. Tên địa bàn là nhãn mô tả quen thuộc, không phải bảng địa giới hiện hành. Doanh thu không được thay đổi dựa vào vị trí. Vì vị trí được gán chủ quan, bảng này không chứng minh khu vực nào thực tế kinh doanh tốt hơn.

## Hành động để tăng doanh thu có kiểm chứng

1. Thu thập giao dịch theo món và địa chỉ thực; thêm giá vốn món, khuyến mại, phí giao hàng để tính lãi đóng góp.
2. Thử gói món phù hợp từng loại điểm trong 4–8 tuần, có nhóm cửa hàng đối chứng cùng tuổi cửa hàng và cùng mùa. So doanh thu/CH/ngày hoạt động, số đơn, giá trị đơn và lãi đóng góp.
3. Nhân rộng khi doanh thu và lãi đóng góp cùng tăng. Với cửa hàng lỗ, rà soát mặt bằng, giá vốn, nhân sự trước khi tăng ngân sách quảng cáo hoặc mở thêm điểm.

## Quy tắc và khả năng truy vết

Giả định duy nhất: Script/gia_dinh_menu_khu_vuc.json. Mỗi nhóm có trọng số riêng theo loại vị trí; chia đều trong nhóm, tăng trọng số combo ×1,2 cho giao hàng rồi chuẩn hóa tổng bằng 1. Phân bổ theo từng cửa hàng–tháng–kênh, số lượng = làm tròn doanh thu phân bổ / giá tham chiếu. Giá bình quân ước tính = doanh thu phân bổ / số lượng; giá tham chiếu không phải giá niêm yết thật.

Fact_Menu có độ hạt tháng–cửa hàng–kênh–món. Không nối trực tiếp hai fact và không cộng doanh thu món với doanh thu vận hành. DULIEUSACH vẫn là một tệp cửa hàng–tháng; giữ nguyên nguồn thô bẩn. Word/PowerPoint cũ trình bày phân tích vận hành; phụ lục này và dashboard là phần bổ sung menu/khu vực hiện hành.
