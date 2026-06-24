import streamlit as st
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime, time
from PIL import Image
st.set_page_config(page_title="Website Camera Face ID", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: rgb(0,0,0); }
    [data-testid="stSidebar"] {
        background-color: rgb(30,38,48);
        border-right: 2px solid rgb(61,90,254);
    }
    .result-container {
        background-color: rgb(79,172,202);
        padding: 20px;
        border-radius: 15px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
    }
    .log-success {
        background-color: rgb(46,125,50);
        padding: 10px;
        border-radius: 5px;
        color: white;
        margin-bottom: 10px;
        border-left: 10px solid rgb(165,214,167);
    }
    .log-fail {
        background-color: rgb(198,40,40);
        padding: 10px;
        border-radius: 5px;
        color: white;
        margin-bottom: 10px;
        border-left: 10px solid rgb(239,154,154);
    }
    </style>
""", unsafe_allow_html=True)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'attendance_db' not in st.session_state:
    st.session_state.attendance_db = {}
if 'time_hour' not in st.session_state:
    st.session_state.time_hour = 8
if 'time_minute' not in st.session_state:
    st.session_state.time_minute = 0
if 'show_setting' not in st.session_state:
    st.session_state.show_setting = False
@st.cache_data
def load_db(directory="faces"):
    known_encodings = []
    known_names = []
    if not os.path.exists(directory): os.makedirs(directory)
    for filename in os.listdir(directory):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            img = face_recognition.load_image_file(f"{directory}/{filename}")
            enc = face_recognition.face_encodings(img)
            if enc:
                known_encodings.append(enc[0])
                known_names.append(os.path.splitext(filename)[0].replace("_", " "))
    return known_encodings, known_names
known_encs, known_names = load_db()
st.sidebar.title("Mục lựa chọn :")
menu = st.sidebar.radio("", ["Face ID", "Danh sách nhân sự", "Lịch sử nhận diện"])
st.sidebar.markdown("---")
st.sidebar.subheader("Cấu hình thời gian")
if st.sidebar.button("Chỉnh giờ nhận diện"):
    st.session_state.show_setting = True
if st.session_state.show_setting:
    pwd = st.sidebar.text_input("Nhập mật khẩu:", type="password")
    if pwd == "KietCameraAI9":
        h_input = st.sidebar.number_input("Giờ giới hạn (0-23):", min_value=0, max_value=23, value=st.session_state.time_hour, step=1)
        m_input = st.sidebar.number_input("Phút giới hạn (0-59):", min_value=0, max_value=59, value=st.session_state.time_minute, step=1)
        if st.sidebar.button("Xác nhận lưu"):
            st.session_state.time_hour = int(h_input)
            st.session_state.time_minute = int(m_input)
            st.session_state.show_setting = False
            st.rerun()
    else:
        if pwd != "":
            st.sidebar.error("Sai mật khẩu!")
check_time = time(st.session_state.time_hour, st.session_state.time_minute)
st.sidebar.text(f"Giờ cài đặt hiện tại: {check_time.strftime('%H:%M')}")
if menu == "Face ID":
    st.title("Website Camera Face ID")
    img_file = st.camera_input("")
    result_text = "Chờ nhận diện..."
    if img_file:
        test_img = face_recognition.load_image_file(img_file)
        test_encs = face_recognition.face_encodings(test_img)
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y vào lúc %Hh%Mp%Ss")
        time_str = now.strftime("%H:%M - %d/%m/%Y")
        current_time = now.time()
        success = False
        if test_encs:
            matches = face_recognition.compare_faces(known_encs, test_encs[0], tolerance=0.5)
            if any(matches):
                best_match_idx = np.argmin(face_recognition.face_distance(known_encs, test_encs[0]))
                name = known_names[best_match_idx]
                if current_time <= check_time:
                    status = "Đúng giờ"
                else:
                    status = "Trễ giờ"
                result_text = f"Kết quả: {name} ({status})"
                st.session_state.attendance_db[name] = {"time": time_str, "status": status}
                st.session_state.history.insert(0, {"msg": f"{timestamp} đã nhận diện thành công: {name} -> [{status}]", "type": "success"})
                success = True
        if not success:
            result_text = "Kết quả: Thất bại"
            st.session_state.history.insert(0, {"msg": f"{timestamp} đã nhận diện thất bại", "type": "fail"})
    st.markdown(f'<div class="result-container">{result_text}</div>', unsafe_allow_html=True)
elif menu == "Danh sách nhân sự":
    st.title("Danh sách nhân sự và trạng thái nhận diện")
    if not known_names:
        st.warning("Thư mục 'faces' đang trống.")
    else:
        table_rows = ""
        for i, name in enumerate(known_names):
            att_info = st.session_state.attendance_db.get(name, {"time": "Chưa ghi nhận", "status": "Chưa điểm danh"})
            status_text = att_info["status"]
            if status_text == "Đúng giờ":
                color = "rgb(46,125,50)"
            elif status_text == "Trễ giờ":
                color = "rgb(198,40,40)"
            else:
                color = "rgb(117,117,117)"
            badge = f'<span style="background-color:{color}; padding:5px 10px; border-radius:5px; color:white; font-weight:bold;">{status_text}</span>'
            table_rows += f'<tr style="border-bottom: 1px solid rgb(51,51,51); color: white;"><td style="padding: 12px; text-align: center;">{i+1}</td><td style="padding: 12px;">{name}</td><td style="padding: 12px; text-align: center;">{att_info["time"]}</td><td style="padding: 12px; text-align: center;">{badge}</td></tr>'
        table_html = f'<table style="width:100%; border-collapse: collapse; background-color: rgb(17,17,17); margin-top: 20px;"><thead><tr style="background-color: rgb(30,38,48); color: rgb(61,90,254); border-bottom: 2px solid rgb(61,90,254);"><th style="padding: 12px; text-align: center; width: 10%;">STT</th><th style="padding: 12px; text-align: left; width: 40%;">Họ và tên</th><th style="padding: 12px; text-align: center; width: 25%;">Thời gian nhận diện</th><th style="padding: 12px; text-align: center; width: 25%;">Trạng thái</th></tr></thead><tbody>{table_rows}</tbody></table>'
        st.markdown(table_html, unsafe_allow_html=True)
else:
    st.title("Lịch sử nhận diện")
    if st.button("Xoá hết lịch sử"):
        st.session_state.history = []
        st.rerun()
    if not st.session_state.history:
        st.info("Chưa có dữ liệu lịch sử.")
    else:
        for entry in st.session_state.history:
            css_class = "log-success" if entry['type'] == "success" else "log-fail"
            st.markdown(f'<div class="{css_class}">{entry["msg"]}</div>', unsafe_allow_html=True)