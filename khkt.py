import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
st.set_page_config(
    page_title="Hệ thống Giám sát Điện năng Tiêu thụ",
    page_icon="",
    layout="wide"
)
st.title("Hệ thống Giám sát Điện năng Tiêu thụ")
st.sidebar.header("Cấu hình Hệ thống")
nguong_cong_suat = st.sidebar.slider("Ngưỡng cảnh báo công suất (W)", 500, 5000, 2000, step=100)
gia_dien = st.sidebar.number_input("Đơn giá điện (VNĐ/kWh)", value=3000, step=100)

if 'history_data' not in st.session_state:
    now = datetime.datetime.now()
    data = []
    for i in range(25):
        t = now - datetime.timedelta(minutes=25-i)
        v = np.random.uniform(218, 222)
        i_val = np.random.uniform(1.5, 11.5)
        p = v * i_val
        data.append({
            "Thời gian": t.strftime("%Y-%m-%d %H:%M:%S"),
            "Điện áp (V)": round(v, 2),
            "Dòng điện (A)": round(i_val, 2),
            "Công suất (W)": round(p, 2)
        })
    st.session_state['history_data'] = pd.DataFrame(data)
df = st.session_state['history_data']
latest = df.iloc[-1]
tab1, tab2, tab3, tab4 = st.tabs([
    "Giám sát & Biểu đồ", 
    "Thống kê & Chi phí", 
    "Cảnh báo", 
    "Lịch sử đo"
])
with tab1:
    st.subheader("1. Giám sát điện áp, dòng điện và công suất thời gian thực")
    col1, col2, col3 = st.columns(3)
    col1.metric("Điện áp", f"{latest['Điện áp (V)']} V")
    col2.metric("Dòng điện", f"{latest['Dòng điện (A)']} A")
    col3.metric("Công suất", f"{latest['Công suất (W)']} W",
                delta=f"{round(latest['Công suất (W)'] - nguong_cong_suat, 2)} W so với ngưỡng",
                delta_color="inverse" if latest['Công suất (W)'] > nguong_cong_suat else "normal")
    st.markdown("---")
    st.subheader("2. Biểu đồ biến động công suất")
    chart_data = df.set_index("Thời gian")[["Công suất (W)"]]
    st.line_chart(chart_data)
with tab2:
    st.subheader("3. Thống kê điện năng tiêu thụ (Ngày, Tuần, Tháng)")
    kwh_ngay = 11.2
    kwh_tuan = 78.5
    kwh_thang = 315.0
    c1, c2, c3 = st.columns(3)
    c1.metric("Hôm nay", f"{kwh_ngay} kWh")
    c2.metric("Tuần này", f"{kwh_tuan} kWh")
    c3.metric("Tháng này", f"{kwh_thang} kWh")
    st.markdown("---")
    st.subheader("4. Ước tính tiền điện")
    tien_ngay = kwh_ngay * gia_dien
    tien_tuan = kwh_tuan * gia_dien
    tien_thang = kwh_thang * gia_dien
    
    st.info(f"**Bảng dự toán chi phí điện năng:**\n\n"
            f"* Tiền điện ngày: **{tien_ngay:,.0f} VNĐ**\n"
            f"* Tiền điện tuần: **{tien_tuan:,.0f} VNĐ**\n"
            f"* Tiền điện tháng (Tạm tính): **{tien_thang:,.0f} VNĐ** (với giá {gia_dien:,.0f} VNĐ/kWh)")
with tab3:
    st.subheader("5. Cảnh báo khi tiêu thụ vượt ngưỡng")
    over_limit_df = df[df["Công suất (W)"] > nguong_cong_suat]
    if not over_limit_df.empty:
        st.error(f"**CẢNH BÁO:** Phát hiện {len(over_limit_df)} lần công suất vượt mức giới hạn an toàn ({nguong_cong_suat}W)!")
        st.dataframe(over_limit_df, use_container_width=True)
    else:
        st.success(f"Hệ thống hoạt động bình thường. Chưa có lần đo nào vượt ngưỡng {nguong_cong_suat}W.")
with tab4:
    st.subheader("6. Lưu trữ dữ liệu các lần đo (Đồng bộ từ Firebase)")
    st.dataframe(df, use_container_width=True)
    if st.button("Mô phỏng nhận dữ liệu mới từ ESP32"):
        t_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        v_new = round(np.random.uniform(218, 222), 2)
        i_new = round(np.random.uniform(1, 14), 2)
        p_new = round(v_new * i_new, 2)
        new_row = pd.DataFrame([{
            "Thời gian": t_now,
            "Điện áp (V)": v_new,
            "Dòng điện (A)": i_new,
            "Công suất (W)": p_new
        }])
        st.session_state['history_data'] = pd.concat([df, new_row], ignore_index=True)
        st.rerun()