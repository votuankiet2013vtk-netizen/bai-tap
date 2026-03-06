import streamlit as st
import time
import random

st.set_page_config(
    page_title="Web Chống Scam",
    page_icon="",
    layout="centered"
)

# ----- Loading -----
st.markdown("<h1 style='text-align:center;'>Web Chống Scam</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:gray;'>Loading...</h4>", unsafe_allow_html=True)

progress = st.progress(0)
percent = st.empty()

for i in range(101):
    time.sleep(0.05)
    progress.progress(i)
    percent.markdown(f"<p style='text-align:center'>{i}%</p>", unsafe_allow_html=True)

st.markdown("---")

names = ["Minh", "Tuấn", "Anh", "Huy", "Long"]

st.markdown(
f"""
<div style="
position:fixed;
bottom:20px;
right:20px;
background:white;
padding:15px;
border-radius:10px;
box-shadow:0 0 10px rgba(0,0,0,0.3);
font-size:16px;">
🟢 <b>{random.choice(names)}</b> vừa tải file thành công!
</div>
""",
unsafe_allow_html=True
)

# ----- Số người đang tải tăng dần -----
if "users" not in st.session_state:
    st.session_state.users = random.randint(250, 300)

stats = st.empty()

st.session_state.users += random.randint(1,3)

stats.markdown(
f"""
<div style='text-align:center;font-size:20px'>
⭐ <b>4.9 / 5</b> (12,483 reviews)<br>
⬇ <b>8,412 downloads today</b><br>
🟢 <b>{st.session_state.users} users đang tải</b>
</div>
""",
unsafe_allow_html=True
)

st.markdown("---")

# ----- Fake captcha -----
st.markdown("### Xác minh bạn không phải robot")

captcha = st.checkbox("I am not a robot")
if captcha:

    clicked = st.button("⬇ Bấm để cài đặt file .exe")

    if clicked:

        st.markdown("### Scanning file...")

        scan = st.progress(0)

        for i in range(101):
            time.sleep(0.02)
            scan.progress(i)

        st.error("Haha bị lừa rồi")

        time.sleep(1)

        st.markdown(
        """
        <h1 style='text-align:center;color:red;font-size:60px;'>⚠ CẢNH BÁO</h1>
        <p style='text-align:center;font-size:22px;'>
        Đừng bao giờ tin người :D.<br>
        Đây cũng là 1 lời cảnh báo từ nhóm mình đến các bạn.<br>
        Hãy cẩn thận khi bấm vào bất cứ đường link hay nút download nào nhé :D
        </p>
        """,
        unsafe_allow_html=True
        )

st.markdown("---")

# ----- Reviews -----
st.markdown("### ⭐ Đánh giá người dùng")

st.markdown(
"""
<div style='font-size:18px'>

⭐️⭐️⭐️⭐️⭐️ <b>Nhiên V.</b><br>
Tải nhanh, cài đặt dễ. Dùng ổn <br><br>

⭐️⭐️⭐️⭐️⭐️ <b>Thành Lê</b><br>
App chạy tốt, không lỗi gì cả.<br><br>

⭐️⭐️⭐️⭐️⭐️ <b>Lâm Hồ Vĩnh</b><br>
Dung lượng nhỏ, tải nhanh. Khá ổn.<br>

</div>
""",
unsafe_allow_html=True
)