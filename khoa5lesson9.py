import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phân Tích Giá Nhà", layout="wide")

st.title("📊 PHÂN TÍCH DỮ LIỆU GIÁ NHÀ")

uploaded_file = st.file_uploader("data.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Chuẩn hóa tên cột
    df.columns = df.columns.str.strip()
    
    # Đổi tên cột cho dễ xử lý
    df = df.rename(columns={
        "Quận/Huyện": "district",
        "Diện tích (m2)": "area",
        "Giá bán (tổng)": "price_total",
        "Loại hình nhà ở": "type",
        "Giá bán/m2": "price_per_m2"
    })

    st.subheader("📌 Dữ liệu gốc")
    st.dataframe(df)

    # ==============================
    # 1. Nhà > 100 triệu/m2
    # ==============================
    st.subheader("🏠 Nhà có giá > 100 triệu/m²")

    high_price = df[df["price_per_m2"] > 100]
    st.write(f"Số lượng: {len(high_price)} căn")
    st.dataframe(high_price)

    # ==============================
    # 2. Giá trung bình theo quận
    # ==============================
    st.subheader("🏙 Giá trung bình theo quận")

    district_avg = df.groupby("district")["price_per_m2"].mean().sort_values(ascending=False)
    st.dataframe(district_avg)

    highest_district = district_avg.idxmax()
    lowest_district = district_avg.idxmin()

    st.success(f"Quận giá cao nhất: {highest_district}")
    st.info(f"Quận giá thấp nhất: {lowest_district}")

    st.bar_chart(district_avg)

    # ==============================
    # 3. Giá theo loại hình nhà
    # ==============================
    st.subheader("🏡 Giá trung bình theo loại hình nhà")

    type_avg = df.groupby("type")["price_per_m2"].mean().sort_values(ascending=False)
    st.dataframe(type_avg)

    highest_type = type_avg.idxmax()
    lowest_type = type_avg.idxmin()

    st.success(f"Loại hình cao nhất: {highest_type}")
    st.info(f"Loại hình thấp nhất: {lowest_type}")

    st.bar_chart(type_avg)

    # ==============================
    # 4. Nhà đắt nhất / rẻ nhất
    # ==============================
    st.subheader("💰 Nhà đắt nhất & rẻ nhất")

    max_house = df.loc[df["price_total"].idxmax()]
    min_house = df.loc[df["price_total"].idxmin()]

    col1, col2 = st.columns(2)

    with col1:
        st.error("Nhà đắt nhất")
        st.write(max_house)

    with col2:
        st.success("Nhà rẻ nhất")
        st.write(min_house)

else:
    st.warning("Vui lòng tải file CSV để bắt đầu phân tích.")