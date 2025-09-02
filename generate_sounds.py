import wave
import numpy as np

def generate_win_sound():
    sample_rate = 44100
    durations = [0.15, 0.15, 0.3]
    freqs = [660, 880, 1100]  # Happy melody
    sound = np.hstack([
        np.sin(2 * np.pi * f * np.linspace(0, d, int(sample_rate * d), False))
        for f, d in zip(freqs, durations)
    ])
    sound = (sound * 32767 / len(freqs)).astype(np.int16)
    with wave.open("win.wav", "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(sound.tobytes())

def generate_correct_sound():
    sample_rate = 44100
    t = np.linspace(0, 0.2, int(sample_rate * 0.2), False)
    tone = np.sin(2 * np.pi * ((1000 + 500 * t) * t))  # Gentle rising ping
    tone = (tone * 32767 / np.max(np.abs(tone))).astype(np.int16)
    with wave.open("correct.wav", "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(tone.tobytes())

def generate_wrong_sound():
    sample_rate = 44100
    t = np.linspace(0, 0.2, int(sample_rate * 0.2), False)
    tone = np.sin(2 * np.pi * (400 - 1000 * t) * t)  # Wah-wah
    tone *= np.exp(-3 * t)  # Quick fade out
    tone = (tone * 32767 / np.max(np.abs(tone))).astype(np.int16)
    with wave.open("wrong.wav", "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(tone.tobytes())

# Generate all sounds
generate_win_sound()
generate_correct_sound()
generate_wrong_sound()

print("🎵 New game-like sounds generated successfully!")
