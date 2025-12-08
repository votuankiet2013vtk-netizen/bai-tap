import streamlit as st

# ====== CẤU HÌNH TRANG ======
st.set_page_config(page_title="Giới thiệu thành viên", layout="wide")

st.title("👥 Giới thiệu Nhóm")
st.write("Dưới đây là thông tin của 5 thành viên trong nhóm:")

# ====== DỮ LIỆU THÀNH VIÊN ======
members = [
    {
        "name": "Võ Tuấn Kiệt",
        "role": "Trưởng nhóm",
        "description": "Phụ trách quản lý chung và điều phối công việc, thiết kế website giới thiệu.",
        "photo": "img1.jpg"
    },
    {
        "name": "Nguyễn Lê Ngọc Minh",
        "role": "Video Editor",
        "description": "Tạo video giới thiệu thành viên và video kết thúc",
        "photo": "img2.jpg"
    },
    {
        "name": "Nguyễn Thị Trúc Linh",
        "role": "Designer",
        "description": "Thiết kế giao diện bài thuyết trình",
        "photo": "img4.jpg"
    },
    {
        "name": "Lê Văn Hiếu Minh",
        "role": "Information Finder",
        "description": "Tìm kiếm thông tin",
        "photo": "img3.jpg"
    },
    {
        "name": "Hồ Vĩnh Thanh Lâm",
        "role": "Information Finder",
        "description": "Tìm kiếm thông tin.",
        "photo": "img5.jpg"
    }
]

# ====== HIỂN THỊ DẠNG LƯỚI ======
cols = st.columns(5)

for i, member in enumerate(members):
    with cols[i]:
        st.image(member["photo"], width=150)
        st.subheader(member["name"])
        st.text(member["role"])
        st.write(member["description"])
