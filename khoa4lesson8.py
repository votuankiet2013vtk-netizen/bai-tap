import streamlit as st
with st.sidebar:
    image = 'TheFatRat.jpg'
    st.image(image, caption='TheFatRat')
    st.write('Họ và tên: Christian Friedrich Johannes Büttner')
    st.write('Nghệ danh: TheFatRat')
    st.write('TheFatRat là một nhà sản xuất âm nhạc điện tử người Đức, nổi tiếng với phong cách âm nhạc pha trộn giữa electro, progressive house và gaming music. '
             'Anh được biết đến qua nhiều bản nhạc phổ biến trên YouTube và Spotify, đặc biệt trong cộng đồng game thủ.')
st.title('Bài hát yêu thích')
st.write('Fly Away')
audio = open('filesound.mp3', 'rb')
st.audio(audio, format='audio/mp3')
st.title('MV yêu thích')
st.write('Fly Away (feat. Anjulie)')
video = 'https://www.youtube.com/watch?v=cMg8KaMdDYo'
st.video(video, format='video/mp4')
