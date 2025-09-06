import numpy as np
import wave
import struct
import os

def create_audio_file(filename, duration, frequency, sample_rate=44100):
    """إنشاء ملف صوتي بسيط"""
    frames = int(duration * sample_rate)
    
    # إنشاء موجة جيبية
    wav_data = []
    for i in range(frames):
        # موجة جيبية بتردد معين
        sample = int(32767 * np.sin(2 * np.pi * frequency * i / sample_rate))
        wav_data.append([sample, sample])  # قناتين (ستيريو)
    
    # كتابة الملف
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)  # ستيريو
        wav_file.setsampwidth(2)  # 16 بت
        wav_file.setframerate(sample_rate)
        for sample in wav_data:
            wav_file.writeframes(struct.pack('<hh', sample[0], sample[1]))

def create_notification_sound(filename, duration):
    """إنشاء صوت تنبيه قصير"""
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    wav_data = []
    for i in range(frames):
        # نغمة قصيرة متزايدة التردد
        freq = 800 + (i / frames) * 400  # من 800 إلى 1200 هرتز
        sample = int(16383 * np.sin(2 * np.pi * freq * i / sample_rate))
        wav_data.append([sample, sample])
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wav_data:
            wav_file.writeframes(struct.pack('<hh', sample[0], sample[1]))

def create_welcome_sound(filename, duration):
    """إنشاء صوت ترحيب"""
    sample_rate = 44100
    frames = int(duration * sample_rate)
    
    wav_data = []
    for i in range(frames):
        # نغمة ناعمة متنوعة
        freq1 = 440 * np.sin(2 * np.pi * 0.5 * i / sample_rate)  # تغيير بطيء
        freq2 = 330 + freq1
        sample = int(16383 * np.sin(2 * np.pi * freq2 * i / sample_rate))
        wav_data.append([sample, sample])
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in wav_data:
            wav_file.writeframes(struct.pack('<hh', sample[0], sample[1]))

# مسار المجلد
audio_dir = r"c:\Users\aliar\OneDrive\Documents\GitHub\aisearch-openai-rag-audio\app\backend\static\audio"

print("🎵 إنشاء الملفات الصوتية...")

# 1. Ran.mp3 - رنة البداية (3 ثوانٍ)
print("🔔 إنشاء Ran.mp3...")
create_audio_file(os.path.join(audio_dir, "Ran.wav"), 3.0, 880)  # A5 نوتة

# 2. between.wav - صوت انتقال (1 ثانية)
print("⚡ إنشاء between.wav...")
create_notification_sound(os.path.join(audio_dir, "between.wav"), 1.0)

# 3. Nancy.wav - ترحيب (2 ثانية)
print("🎤 إنشاء Nancy.wav...")
create_welcome_sound(os.path.join(audio_dir, "Nancy.wav"), 2.0)

print("✅ تم إنشاء جميع الملفات الصوتية بنجاح!")
print(f"📁 الملفات في: {audio_dir}")
