import streamlit as st
import random

st.set_page_config(page_title="KatYapPT", page_icon="🤫", layout="centered")

st.title("KatYapPT")
st.caption("The ultimate Sigma chatbot.")

def generate_1000_responses():
    subjects = ["im", "you", "bro is", "blud is", "the chat thinks he is", "thanhhoanian is", "ohio resident is"]
    sigmas = ["sigma", "not sigma", "bum", "thanhhoanian", "gigachad", "skibidi", "alpha", "beta", "NPC"]
    numbers = ["36", "67", "69", "99", "0 aura", "+1000 aura", "-500 aura", "4k", "100"]
    actions = ["mewing", "yapping", "cooking", "crying", "grinding", "maxing", "glazing", "taxing"]
    slangs = ["womp womp", "sheesh", "bruh", "skibidi toilet", "rizzler", "erm what the sigma", "holy moly", "💀", "🤫🧏‍♂️", "bye bye"]
    responses = set()
    exact_samples = ["im sigma", "you not sigma", "you bum", "67", "36", "im thanhhoanian", "womp womp"]
    for sample in exact_samples:
        responses.add(sample)
    while len(responses) < 1000:
        style = random.randint(1, 5)
        if style == 1:
            sub = random.choice(subjects[:2])
            sig = random.choice(sigmas)
            responses.add(f"{sub} {sig}")
        elif style == 2:
            responses.add(random.choice(numbers))
        elif style == 3:
            sub = random.choice(subjects[2:])
            act = random.choice(actions)
            responses.add(f"{sub} {act}")
        elif style == 4:
            num = random.choice(numbers)
            sig = random.choice(sigmas)
            responses.add(f"{num} {sig}")
            responses.add(f"you {sig} {num}")
        elif style == 5:
            slg = random.choice(slangs)
            sub = random.choice(subjects)
            act = random.choice(actions)
            responses.add(f"{slg} {sub} {act}")
            responses.add(f"{sub} {act} {slg}")

    return list(responses)

BOT_RESPONSES = generate_1000_responses()

with st.sidebar:
    st.header("Bot Stats")
    st.success(f"Loaded {len(BOT_RESPONSES)} answer successfully!")
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        col1, col2 = st.columns([1, 4])
        with col2:
            with st.chat_message("user"):
                st.write(message["content"])
    else:
        col1, col2 = st.columns([4, 1])
        with col1:
            with st.chat_message("assistant"):
                st.write(message["content"])

if user_input := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    random_reply = random.choice(BOT_RESPONSES)
    st.session_state.messages.append({"role": "assistant", "content": random_reply})
    st.rerun()