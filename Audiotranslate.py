from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import soundfile as sf
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    audio_file = request.files["audio"]
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        audio_file.save(f.name)
        with open(f.name, "rb") as af:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=af,
                language="zh"
            )
        os.unlink(f.name)
    chinese = result.text.strip()
    if not chinese:
        return jsonify({"error": "没识别到"}), 400

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator. Translate the Chinese text to natural English. Output only the translation, nothing else."},
            {"role": "user", "content": chinese}
        ]
    )
    english = response.choices[0].message.content.strip()

    tts = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=english
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(tts.content)
        tmp_path = f.name

    return jsonify({
        "chinese": chinese,
        "english": english,
        "audio_path": tmp_path
    })

@app.route("/audio/<path:filename>")
def audio(filename):
    return send_file("/" + filename, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True, port=5000)