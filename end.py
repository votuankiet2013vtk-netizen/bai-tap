import streamlit as st

st.set_page_config(layout="wide")

# ---- CSS ----
st.markdown("""
    <style>
    .credit-container {
        position: relative;
        height: 650px;
        overflow: hidden;
        background-color: black;
        color: white;
        font-size: 28px;
        text-align: center;
    }

    .credits {
        position: absolute;
        width: 100%;
        animation: scroll-up 15s linear forwards;
    }

    @keyframes scroll-up {
        0%   { top: 100%; }
        100% { top: -120%; }
    }

    .title {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ------ DANH SÁCH TÊN ------
names = [
    "Võ Tuấn Kiệt - Nhóm trưởng",
    "Nguyễn Lê Ngọc Minh - Editor",
    "Nguyễn Thị Trúc Linh - Thiết kế Slide",
    "Lê Văn Hiếu Minh - Tìm kiếm thông tin",
    "Hồ Vĩnh Thanh Lâm - Tìm kiếm thông tin"
]

# HTML danh sách tên
name_html = "<br>".join([f"<p>{n}</p>" for n in names])

credits_html = f"""
<div class="credit-container">
    <div class="credits">
        <p class="title">Directed By</p>
        {name_html}
    </div>
</div>
"""

st.markdown(credits_html, unsafe_allow_html=True)
