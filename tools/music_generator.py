import wave
import struct
import math
import os

def generate_tone(filename, duration, freq_func):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    os.makedirs(os.path.join("assets", "audio"), exist_ok=True)
    path = os.path.join("assets", "audio", filename)
    
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            # Dynamic frequency for a "melody"
            freq = freq_func(t)
            value = int(16384 * math.sin(2 * math.pi * freq * t))
            data = struct.pack('<h', value)
            f.writeframesraw(data)
    print(f"Generated {filename}")

def title_melody(t):
    # Slow, peaceful arpeggio
    notes = [261.63, 329.63, 392.00, 523.25] # C4, E4, G4, C5
    return notes[int(t) % 4]

def world_melody(t):
    # Ambient minor drone
    notes = [220.00, 261.63, 293.66, 349.23] # A3, C4, D4, F4
    return notes[int(t/2) % 4]

if __name__ == "__main__":
    generate_tone("title_theme.wav", 10, title_melody)
    generate_tone("world_theme.wav", 20, world_melody)
