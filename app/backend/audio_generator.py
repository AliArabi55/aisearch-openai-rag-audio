import numpy as np
import wave
import os
from gtts import gTTS
import tempfile

def generate_ring_tone(duration=3.0, frequency=800, sample_rate=44100):
    """
    إنشاء صوت رنين لمدة محددة
    """
    # حساب عدد العينات
    num_samples = int(duration * sample_rate)
    
    # إنشاء موجة جيبية للرنين
    t = np.linspace(0, duration, num_samples, False)
    
    # إنشاء نغمة مركبة للرنين (تكرار كل 0.5 ثانية)
    ring_pattern = np.sin(2 * np.pi * frequency * t) * np.sin(2 * np.pi * 2 * t)
    
    # تطبيق التلاشي في البداية والنهاية
    fade_samples = int(0.1 * sample_rate)  # 0.1 ثانية للتلاشي
    ring_pattern[:fade_samples] *= np.linspace(0, 1, fade_samples)
    ring_pattern[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    # تحويل إلى 16-bit
    audio_data = (ring_pattern * 32767).astype(np.int16)
    
    return audio_data, sample_rate

def generate_arabic_message(text="الآن يمكنك التحدث باللغة العربية"):
    """
    إنشاء رسالة صوتية باللغة العربية
    """
    try:
        # إنشاء ملف مؤقت
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        # إنشاء الصوت باستخدام gTTS
        tts = gTTS(text=text, lang='ar', slow=False)
        tts.save(temp_path)
        
        return temp_path
    except Exception as e:
        print(f"Error generating Arabic message: {e}")
        return None

def save_ring_tone():
    """
    حفظ صوت الرنين كملف WAV
    """
    audio_data, sample_rate = generate_ring_tone()
    
    # إنشاء مجلد الأصوات إذا لم يكن موجوداً
    audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    
    # حفظ الملف
    output_path = os.path.join(audio_dir, 'ring.wav')
    
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # أحادي القناة
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"Ring tone saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    # إنشاء ملف الرنين
    save_ring_tone()
    
    # إنشاء الرسالة العربية
    arabic_msg_path = generate_arabic_message()
    if arabic_msg_path:
        print(f"Arabic message saved to: {arabic_msg_path}")
