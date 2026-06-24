import streamlit as st
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime
from PIL import Image
st.set_page_config(page_title="Website Camera Face ID", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] {
        background-color: #1e2630;
        border-right: 2px solid #3d5afe;
    }
    .result-container {
        background-color: #4facca;
        padding: 20px;
        border-radius: 15px;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
    }
    .log-success {
        background-color: #2e7d32;
        padding: 10px;
        border-radius: 5px;
        color: white;
        margin-bottom: 10px;
        border-left: 10px solid #a5d6a7;
    }
    .log-fail {
        background-color: #c62828;
        padding: 10px;
        border-radius: 5px;
        color: white;
        margin-bottom: 10px;
        border-left: 10px solid #ef9a9a;
    }
    </style>
""", unsafe_allow_html=True)
if 'history' not in st.session_state:
    st.session_state.history = []
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
if menu == "Face ID":
    st.title("Website Camera Face ID")
    img_file = st.camera_input("")
    result_text = "Chờ nhận diện..."
    if img_file:
        test_img = face_recognition.load_image_file(img_file)
        test_encs = face_recognition.face_encodings(test_img)
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y vào lúc %Hh%Mp%Ss")
        success = False
        if test_encs:
            matches = face_recognition.compare_faces(known_encs, test_encs[0], tolerance=0.5)
            if any(matches):
                best_match_idx = np.argmin(face_recognition.face_distance(known_encs, test_encs[0]))
                name = known_names[best_match_idx]
                result_text = f"Kết quả: {name}"
                st.session_state.history.insert(0, {"msg": f"{timestamp} đã nhận diện thành công: {name}", "type": "success"})
                success = True
        if not success:
            result_text = "Kết quả: Thất bại"
            st.session_state.history.insert(0, {"msg": f"{timestamp} đã nhận diện thất bại", "type": "fail"})
    st.markdown(f'<div class="result-container">{result_text}</div>', unsafe_allow_html=True)
elif menu == "Danh sách nhân sự":
    st.title("Danh sách người có thể nhận diện")
    if not known_names:
        st.warning("Thư mục 'faces' đang trống.")
    else:
        for i, name in enumerate(known_names):
            st.write(f"{i+1}. {name}")
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