import streamlit as st
col1, col2, col3, col4, col5 = st.columns(5)
col6, col7 = st.columns([2,1])
with col1:
    b1 = st.button('Con mèo')
with col2:
    b2 = st.button('Con chó')
with col3:
    b3 = st.button('Con khỉ')
with col4:
    b4 = st.button('Đại bàng')
with col5:
    b5 = st.button('Con gà')
if b1:
    with col6:
        st.write('Âm thanh')
        audio = open('catsound.mp3', 'rb')
        st.audio(audio, format='audio/mp3')
        st.write('Video')
        video = 'https://www.youtube.com/watch?v=NiqRt5mKzJ8'
        st.video(video, format='video/mp4')
    with col7:
        image = 'cat.jpg'
        st.image(image, caption='Con mèo')
if b2:
    with col6:
        st.write('Âm thanh')
        audio = open('dogsound.mp3', 'rb')
        st.audio(audio, format='audio/mp3')
        st.write('Video')
        video = 'https://www.youtube.com/watch?v=IdFyg0AXfb0'
        st.video(video, format='video/mp4')
    with col7:
        image = 'dog.jpg'
        st.image(image, caption='Con chó')
if b3:
    with col6:
        st.write('Âm thanh')
        audio = open('monkeysound.mp3', 'rb')
        st.audio(audio, format='audio/mp3')
        st.write('Video')
        video = 'https://www.youtube.com/watch?v=UIfOA-h56-w'
        st.video(video, format='video/mp4')
    with col7:
        image = 'monkey.jpg'
        st.image(image, caption='Con khỉ')
if b4:
    with col6:
        st.write('Âm thanh')
        audio = open('eaglesound.mp3', 'rb')
        st.audio(audio, format='audio/mp3')
        st.write('Video')
        video = 'https://www.youtube.com/watch?v=NWKSck16Cgc'
        st.video(video, format='video/mp4')
    with col7:
        image = 'eagle.jpg'
        st.image(image, caption='Đại bàng')
if b5:
    with col6:
        st.write('Âm thanh')
        audio = open('chickensound.mp3', 'rb')
        st.audio(audio, format='audio/mp3')
        st.write('Video')
        video = 'https://www.youtube.com/watch?v=-WqroQP-ASM'
        st.video(video, format='video/mp4')
    with col7:
        image = 'chicken.jpg'
        st.image(image, caption='Con gà')