import streamlit as st
import requests
from PIL import Image
import tempfile
import os
from streamlit_mic_recorder import mic_recorder

API_BASE = "http://localhost:5000"

# --- Streamlit Setup ---
st.set_page_config(page_title="AI Bible Verse Finder", layout="centered")
st.image(Image.open("logo_image.png"), width=150)
st.title("📖 Babcock AI-Powered Bible Verse Finder")
st.markdown("Enter text, upload audio, or record directly to find matching Bible verses.")

if "last_result" not in st.session_state:
    st.session_state["last_result"] = None


# --- Helper function to call backend ---
def call_api(endpoint, payload=None, files=None, timeout=60):
    try:
        url = f"{API_BASE}/{endpoint}"
        if files:
            r = requests.post(url, files=files, timeout=timeout)
        else:
            r = requests.post(url, json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"❌ API Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
    return None


# --- Input Mode Selection ---
mode = st.radio("Choose input method:", [
    "Text",
    "Voice (Record on Page)",
    "Voice (Audio Upload)"
])


# --- Text Mode ---
if mode == "Text":
    user_text = st.text_area("📝 Enter your sermon excerpt:", height=200)
    if st.button("🔍 Find Verse"):
        if user_text.strip():
            with st.spinner("Matching verse..."):
                st.session_state["last_result"] = call_api("text", payload={"text": user_text})
        else:
            st.warning("Please enter some text.")


# — Voice Record on Page —
elif mode == "Voice (Record on Page)":
    st.markdown("🎤 Record your sermon excerpt below:")

    audio_file = st.audio_input("🎙️ Click to record")

    if audio_file is not None:
        st.success("🎵 Recording captured!")
        st.audio(audio_file)

        if st.button("🔄 Transcribe and Find Verses"):
            with st.spinner("Transcribing audio and finding verses..."):
                try:
                    files = {"audio": ("recording.wav", audio_file, "audio/wav")}
                    r = requests.post(
                        "http://localhost:5000/voice",
                        files=files,
                        timeout=60
                    )
                    if r.status_code == 200:
                        result = r.json()
                        st.session_state.last_result = result
                        st.success("✅ Processing completed!")
                    else:
                        st.error(f"❌ API Error: {r.status_code}")
                        st.error(f"Response: {r.text}")
                        st.session_state.last_result = None
                except Exception as e:
                    st.error(f"❌ Error processing recording: {str(e)}")
                    st.session_state.last_result = None



# --- Upload Audio Mode ---
elif mode == "Voice (Audio Upload)":
    uploaded_file = st.file_uploader("🎤 Upload an audio file (MP3 or WAV)", type=["wav", "mp3"])
    if uploaded_file and st.button("🔍 Transcribe & Match Upload"):
        with st.spinner("Processing uploaded file..."):
            files = {"audio": (uploaded_file.name, uploaded_file, "multipart/form-data")}
            st.session_state["last_result"] = call_api("voice", files=files)


# --- Results Display ---
if st.session_state.get("last_result"):
    st.markdown("---")
    result = st.session_state["last_result"]

    if result.get("text"):
        st.success("📝 Transcribed Text:")
        st.write(result["text"])

    if result.get("verse"):
        st.success("📖 Matched Verse:")
        st.write(result["verse"])
    else:
        st.warning("⚠️ No verse matched.")

    with st.expander("🔧 Debug - Full API Response"):
        st.json(result)

    if st.button("🗑️ Clear Results"):
        st.session_state["last_result"] = None
        st.rerun()
