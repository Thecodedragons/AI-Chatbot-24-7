import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS
import os
import requests
import tempfile

# ── Load API Key ──────────────────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="AI Studio 24/7",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Studio 24/7")
st.caption("All-in-One AI powered by Groq API")

# ── Tabs ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 AI Chatbot",
    "🗣️ Text to Speech",
    "💻 Code Assistant",
    "🎨 Image Generator"
])

# ══════════════════════════════════════════════════════
# TAB 1 — AI CHATBOT
# ══════════════════════════════════════════════════════
with tab1:
    st.header("💬 AI Chatbot")
    st.caption("Ask me anything!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages,
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ══════════════════════════════════════════════════════
# TAB 2 — TEXT TO SPEECH
# ══════════════════════════════════════════════════════
with tab2:
    st.header("🗣️ Text to Speech")
    st.caption("Convert any text to audio!")

    tts_text = st.text_area("Enter text to convert to speech:", height=150,
                             placeholder="Type anything here...")
    language = st.selectbox("Select Language:", [
        "en - English",
        "hi - Hindi",
        "kn - Kannada",
        "te - Telugu",
        "ta - Tamil",
        "fr - French",
        "de - German",
        "es - Spanish",
    ])
    lang_code = language.split(" - ")[0]

    if st.button("🎙️ Generate Audio"):
        if tts_text.strip():
            with st.spinner("Generating audio..."):
                tts = gTTS(text=tts_text, lang=lang_code)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    tts.save(f.name)
                    st.audio(f.name, format="audio/mp3")
                    st.success("✅ Audio generated! Press play above.")
        else:
            st.warning("⚠️ Please enter some text first!")

# ══════════════════════════════════════════════════════
# TAB 3 — CODE ASSISTANT
# ══════════════════════════════════════════════════════
with tab3:
    st.header("💻 AI Code Assistant")
    st.caption("Generate, explain or fix code!")

    code_action = st.selectbox("What do you want to do?", [
        "Generate Code",
        "Explain Code",
        "Fix/Debug Code",
        "Convert Code to Another Language",
    ])

    user_input = st.text_area("Enter your request or paste your code:",
                               height=200,
                               placeholder="e.g. Write a Python function to sort a list...")

    language_choice = st.selectbox("Programming Language:", [
        "Python", "JavaScript", "Java", "C++", "C",
        "HTML/CSS", "SQL", "React", "Node.js"
    ])

    if st.button("⚡ Generate"):
        if user_input.strip():
            with st.spinner("AI is thinking..."):
                system_prompt = f"You are an expert {language_choice} developer. {code_action} as requested. Always provide clean, well-commented code."
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                )
                result = response.choices[0].message.content
                st.code(result, language=language_choice.lower())
                st.success("✅ Done!")
        else:
            st.warning("⚠️ Please enter your request first!")

# ══════════════════════════════════════════════════════
# TAB 4 — IMAGE GENERATOR
# ══════════════════════════════════════════════════════
with tab4:
    st.header("🎨 AI Image Generator")
    st.caption("Generate images using Hugging Face (Free!)")

    hf_token = st.text_input("Enter your Hugging Face API Token:",
                               type="password",
                               placeholder="hf_xxxxxxxxxxxxxxxx")
    st.markdown("Get free token at 👉 **https://huggingface.co/settings/tokens**")

    img_prompt = st.text_area("Describe the image you want:",
                               height=100,
                               placeholder="e.g. A beautiful sunset over mountains...")

    if st.button("🎨 Generate Image"):
        if img_prompt.strip() and hf_token.strip():
            with st.spinner("Generating image... this may take 20-30 seconds..."):
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
                headers = {"Authorization": f"Bearer {hf_token}"}
                response = requests.post(API_URL,
                                          headers=headers,
                                          json={"inputs": img_prompt})
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                        f.write(response.content)
                        st.image(f.name, caption=img_prompt)
                        st.success("✅ Image generated!")
                else:
                    st.error(f"❌ Error: {response.text}")
        else:
            st.warning("⚠️ Please enter both HuggingFace token and image description!")



