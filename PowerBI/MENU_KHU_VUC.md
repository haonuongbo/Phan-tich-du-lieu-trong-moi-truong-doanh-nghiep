# Mở rộng menu và khu vực giả định

Đọc BaoCao/PhanTich_Menu_KhuVuc.md trước khi dùng bảng mới. Đây là phân bổ theo giả định, chưa phải kết quả POS hay sở thích khách hàng quan sát được.

Model.pq đã bổ sung Dim_Menu, Fact_Menu và các KPI món/nhóm/khu vực/loại vị trí. fnReadCSV đã định kiểu cột mới. Quan hệ 1–nhiều, lọc một chiều:

- Dim_Menu[menu_id] → Fact_Menu[menu_id].
- Dim_Store[store_id] → Fact_Menu[store_id].
- Dim_Date[ngay] → Fact_Menu[thang].

Không nối Fact_Menu trực tiếp với Fact_Operation hoặc Fact_Channel. Không nối KPI tổng hợp vào fact. Dùng thuộc tính khu_vuc_gia_dinh và loai_vi_tri_gia_dinh của Dim_Store để lọc các fact. Bộ lọc món chỉ áp dụng doanh thu phân bổ món, không tự phân bổ chi phí/lợi nhuận vận hành theo món.

Measure bổ sung:

```dax
DT món phân bổ giả định = SUM(Fact_Menu[doanh_thu_phan_bo_VND])
SL món ước tính = SUM(Fact_Menu[so_luong_uoc_tinh])
Tỷ trọng DT món = DIVIDE([DT món phân bổ giả định], CALCULATE([DT món phân bổ giả định], REMOVEFILTERS(Dim_Menu)))
```

Tỷ trọng so với toàn bộ menu nhưng giữ thời gian và cửa hàng. Giá bình quân món = DT món phân bổ / SL món ước tính; không lấy trung bình cộng giá từng dòng. Gắn nhãn **GIẢ ĐỊNH — KHÔNG PHẢI POS** trên hai trang menu/khu vực. Mã Power Query/DAX bổ sung chưa được chạy trong Power BI Desktop.
