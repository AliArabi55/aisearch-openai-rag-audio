import numpy as np
import wave
import tempfile
import os
from gtts import gTTS

def generate_ring_tone():
    # Generate ring tone - 3 seconds
    duration = 3.0  # seconds
    sample_rate = 44100
    
    # Generate ring pattern: 2 frequencies mixed
    t = np.linspace(0, duration, int(sample_rate * duration))
    freq1 = 440  # A note
    freq2 = 880  # Higher A note
    
    # Create ring pattern (on-off-on-off)
    ring_pattern = np.sin(2 * np.pi * freq1 * t) * 0.3 + np.sin(2 * np.pi * freq2 * t) * 0.3
    
    # Apply envelope for ring pattern (fade in/out every 0.5 seconds)
    envelope = np.ones_like(t)
    for i in range(len(t)):
        time_pos = t[i]
        # Create ring pattern: ring for 0.4s, silence for 0.1s, repeat
        cycle_time = time_pos % 0.5
        if cycle_time > 0.4:
            envelope[i] = 0
    
    audio_data = ring_pattern * envelope
    
    # Normalize and convert to 16-bit integers
    audio_data = np.clip(audio_data, -1, 1)
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Save as WAV file
    output_path = os.path.join(os.path.dirname(__file__), "static", "audio", "ring.wav")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"Ring tone saved to: {output_path}")
    return output_path

def generate_arabic_message():
    # Updated Arabic text with restaurant context
    arabic_text = "الآن يمكنك التحدث لأحد وكلاء الذكاء الإصطناعي في مطعم سيركلز"
    
    # Create TTS
    tts = gTTS(text=arabic_text, lang='ar', slow=False)
    
    # Save to temporary file first
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tts.save(tmp_file.name)
        temp_path = tmp_file.name
    
    # Move to static audio directory
    output_path = os.path.join(os.path.dirname(__file__), "static", "audio", "arabic_message.mp3")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Copy from temp to final location
    import shutil
    shutil.move(temp_path, output_path)
    
    print(f"Arabic message saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    # Generate both audio files
    ring_path = generate_ring_tone()
    arabic_path = generate_arabic_message()
    print("Audio files generated successfully!")
