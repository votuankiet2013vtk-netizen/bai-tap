import streamlit as st
appetizer = ['Grilled Bread with Cheese', 'French Onion Soup', 'Salad Caesar', 'Gỏi cuốn', 'Garlic Butter Bread', 'Italian Cold Tomato Soup']
main = ['Pizza', 'Pad Thai', 'Steak', 'Moussaka', 'Paella', 'Roast Chicken', 'Indian Meat Curry']
dessert = ['Cheesecake', 'Tiramisu', 'Crème brûlée', 'Panna cotta', 'Trifle', 'Gelato', 'Turkish Sweet']
with st.form('Thực đơn yêu thích'):
    options1 = st.multiselect('Món khai vị ưa thích của bạn?', appetizer)
    options2 = st.multiselect('Món chính ưa thích của bạn?', main)
    options3 = st.multiselect('Món tráng miệng ưa thích của bạn?', dessert)
    submitted = st.form_submit_button('Submit')
if submitted:
    st.write('Các lựa chọn của bạn là:')
    st.write('**1. Món khai vị:**')
    if len(options1) == 0:
        st.write('Bạn chưa chọn món khai vị')
    else:
        for i in range(len(options1)):
            st.write(options1[i])
    st.write('**2. Món chính:**')
    if len(options2) == 0:
        st.write('Bạn chưa chọn món chính')
    else:
        for i in range(len(options2)):
            st.write(options2[i])
    st.write('**3. Món tráng miệng:**')
    if len(options3) == 0:
        st.write('Bạn chưa chọn món tráng miệng')
    else:
        for i in range(len(options3)):
            st.write(options3[i])

