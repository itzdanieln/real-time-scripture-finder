from faster_whisper import WhisperModel

# Load the model once globally
model = WhisperModel("base")  # You can use "small", "medium", etc. depending on your resources

# ✅ Standard transcription function
def transcribe_audio(audio_path):
    segments, _ = model.transcribe(audio_path)
    return " ".join([segment.text for segment in segments])















































# ✅ Transcription with trigger word detection
def transcribe_with_trigger(audio_path, trigger_words=None):
    if trigger_words is None:
        trigger_words = [
            "the word of God says",
            "the Bible says",
            "it is written",
            "according to",
            "Genesis",
            "Exodus",
            "Matthew",
            "Revelation",
            "Corinthians",
        ]

    segments, _ = model.transcribe(audio_path)
    full_text = " ".join([segment.text for segment in segments])
    full_text_lower = full_text.lower()

    for word in trigger_words:
        if word.lower() in full_text_lower:
            return full_text  # Trigger word found

    return None  # No trigger words found
