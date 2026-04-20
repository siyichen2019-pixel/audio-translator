import os
import tempfile
import sounddevice as sd
import soundfile as sf
from openai import OpenAI

client = OpenAI(api_key="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")

def record_audio(seconds=5, samplerate=16000):
    print(f"\n🎤 开始录音（{seconds}秒）...")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("✅ 录音完成")
    return audio, samplerate

def transcribe(audio, samplerate):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, samplerate, subtype='PCM_16')
        with open(f.name, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="zh"
            )
        os.unlink(f.name)
    return result.text.strip()

def translate(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a translator. Translate the Chinese text to natural English. Output only the translation, nothing else."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def speak(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(response.content)
        tmp_path = f.name
    os.system(f"ffplay -nodisp -autoexit '{tmp_path}' 2>/dev/null")
    os.unlink(tmp_path)

def main():
    print("\n=== 中文 → 英文 实时翻译 Demo ===")
    print("按 Enter 开始录音（5秒），Ctrl+C 退出\n")
    while True:
        input("按 Enter 开始...")
        audio, sr = record_audio(seconds=5)

        print("🔄 识别中文...")
        chinese = transcribe(audio, sr)
        if not chinese:
            print("❌ 没识别到，再试一次")
            continue
        print(f"📝 中文：{chinese}")

        print("🌐 翻译中...")
        english = translate(chinese)
        print(f"🇬🇧 英文：{english}")

        print("🔊 播放中...")
        speak(english)

if __name__ == "__main__":
    main()
    