import streamlit as st
st.title('Điền thông tin giới thiệu bản thân em')
my_bar = st.progress(0)
quiz = ['Họ và tên:', 'Ngày tháng năm sinh:', 'Sở thích:']
answers = []
len_quiz = len(quiz)
for i in range(len_quiz):
    answer = st.text_input(quiz[i], '')
    if answer != '':
        answers.append(answer)
if st.button('Confirm'):
    if len(answers) == len_quiz:
        my_bar.progress(100)
        st.write('Bạn đã hoàn thành đầy đủ thông tin!')
        st.balloons()
    else:
        my_bar.progress(len(answers)/len_quiz)
        st.write('Bạn chưa hoàn thành đầy đủ thông tin!')
    for i in range(len(answers)):
        st.write(quiz[i], answers[i])
