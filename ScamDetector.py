import streamlit as st
import time
st.set_page_config(
    page_title="Web Chống Scam",
    layout="centered"
)


title_placeholder = st.empty()
progress_placeholder = st.empty()

title_placeholder.markdown(
    "<h1 style='text-align: center; font-size: 50px;'>Web Chống Scam</h1>",
    unsafe_allow_html=True
)
st.markdown("<h4 style='text-align: center; color: gray;'>Loading...</h4>", unsafe_allow_html=True)
progress_bar = progress_placeholder.progress(0)
for i in range(101):
    time.sleep(0.05)
    progress_bar.progress(i)
title_placeholder.empty()
progress_placeholder.empty()
st.empty()


st.markdown(
    "<h1 style='text-align: center; color: red; font-size: 60px;'>🚨 HÃY CẨN THẬN! 🚨</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='font-size:22px; text-align:center;'>
    Nếu như không phải là mình gửi cho bạn link này thì rất có thể bạn đã bị một trang web giả mạo lừa rồi!
    Hiện nay có rất nhiều chiêu trò đánh cắp thông tin, chiếm đoạt tài khoản, lấy mật khẩu hoặc lừa tiền.
    <b>Vì vậy hãy luôn kiểm tra kỹ đường link và không nhập mật khẩu hay thông tin cá nhân vào web lạ nhé!</b>
    Hãy cảnh giác với mọi link trên mạng!
    </div>
    """,
    unsafe_allow_html=True
)