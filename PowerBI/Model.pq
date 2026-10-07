// Tạo query tên Model, bỏ Enable load. Sau đó tạo từng query = Model[Dim_Store], ...
let
    Tables = [
        Dim_Store = fnReadCSV("Dim_Store"),
        Dim_Date = fnReadCSV("Dim_Date"),
        Fact_Operation = fnReadCSV("Fact_Operation"),
        Fact_Channel = fnReadCSV("Fact_Channel"),
        Dim_Menu = fnReadCSV("Dim_Menu"),
        Fact_Menu = fnReadCSV("Fact_Menu"),
        KPI_Mon_Nam = fnReadCSV("KPI_Mon_Nam"),
        KPI_NhomMon_Nam = fnReadCSV("KPI_NhomMon_Nam"),
        KPI_KhuVuc_Nam = fnReadCSV("KPI_KhuVuc_Nam"),
        KPI_LoaiViTri_Nam = fnReadCSV("KPI_LoaiViTri_Nam"),
        KPI_Thang = fnReadCSV("KPI_Thang"),
        KPI_Quy = fnReadCSV("KPI_Quy"),
        KPI_Nam = fnReadCSV("KPI_Nam"),
        KPI_CuaHang_Nam = fnReadCSV("KPI_CuaHang_Nam"),
        KPI_TongQuan = fnReadCSV("KPI_TongQuan")
    ]
in
    Tables
