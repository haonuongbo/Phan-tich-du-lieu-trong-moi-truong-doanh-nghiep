// Tạo parameter DataFolder (Text) trỏ đến đường dẫn tuyệt đối thư mục DataPhantich.
// Tạo Blank Query, mở Advanced Editor, dán mã này và đổi tên thành fnReadCSV.
(TableName as text) as table =>
let
    Source = Csv.Document(File.Contents(DataFolder & "\" & TableName & ".csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    EmptyAsNull = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    TextNames = {"store_id", "thanh_pho", "loai_du_lieu", "phien_ban", "nguon_tep", "nguon_sheet",
                 "nam_thang", "nam_quy", "kenh", "trang_thai", "ghi_chu", "menu_id", "ten_mon", "nhom_mon",
                 "khu_vuc_gia_dinh", "loai_vi_tri_gia_dinh", "co_so_vi_tri", "co_so_du_lieu"},
    DateNames = {"ngay", "ngay_mo", "thang", "ky"},
    IntegerNames = {"nam", "quy", "thang_so", "so_thang", "so_thang_ky", "CH_co_phat_sinh",
                    "cua_hang_thang", "CH_dau_ky", "CH_cuoi_ky", "so_CH_tuong_duong", "nam_dau", "nam_cuoi",
                    "don_tai_quan", "don_nen_tang", "don_online_rieng", "tong_don", "so_don", "don_co_so", "so_luong_uoc_tinh"},
    Types = List.Transform(Table.ColumnNames(EmptyAsNull), (ColumnName) =>
        {ColumnName, if List.Contains(TextNames, ColumnName) then type text
                     else if List.Contains(DateNames, ColumnName) then type date
                     else if ColumnName = "du_ky" then type logical
                     else if List.Contains(IntegerNames, ColumnName) then Int64.Type
                     else type number}),
    Typed = Table.TransformColumnTypes(EmptyAsNull, Types, "en-US")
in
    Typed
