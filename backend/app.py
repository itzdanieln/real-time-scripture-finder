from flask import Flask, request, jsonify
from ai_engine import match_bible_verse
from stt import transcribe_audio, transcribe_with_trigger
import os

app = Flask(__name__)

@app.route("/text", methods=["POST"])
def handle_text():
    input_text = request.json.get("text", "")
    verse = match_bible_verse(input_text)
    return jsonify({"verse": verse})

@app.route("/voice", methods=["POST"])
def handle_voice():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files['audio']
    if audio.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_path = f"./temp_{audio.filename}"
    audio.save(file_path)

    try:
        transcribed = transcribe_audio(file_path)
        verse = match_bible_verse(transcribed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)

    return jsonify({"text": transcribed, "verse": verse})

@app.route("/stream", methods=["POST"])
def handle_stream_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files['audio']
    if audio.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_path = f"./temp_stream_{audio.filename}"
    audio.save(file_path)

    try:
        # Transcribe and check if it contains a trigger word
        trigger_segments = transcribe_with_trigger(file_path)
        if trigger_segments:
            verse = match_bible_verse(trigger_segments[-1])  # Use latest trigger segment
            return jsonify({"verse": verse})
        else:
            return jsonify({"verse": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)


if __name__ == "__main__":
    app.run(debug=True)
