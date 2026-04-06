import wave
import math
import struct

def generate_tone(filename, frequency, duration_ms, volume=0.5, wave_type='sine', fade_out=True):
    sample_rate = 44100
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            if wave_type == 'sine':
                val = math.sin(2.0 * math.pi * frequency * t)
            elif wave_type == 'square':
                val = 1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0
            
            if fade_out:
                fade_factor = 1.0 - (i / float(num_samples))
                val *= fade_factor
                
            val *= volume
            
            sample = max(-32768, min(32767, int(val * 32767.0)))
            wav_file.writeframes(struct.pack('<h', sample))

def generate_sequence(filename, notes, wave_type='sine'):
    sample_rate = 44100
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for freq, dur, vol in notes:
            num_samples = int(sample_rate * (dur / 1000.0))
            for i in range(num_samples):
                t = float(i) / sample_rate
                if wave_type == 'sine':
                    val = math.sin(2.0 * math.pi * freq * t)
                elif wave_type == 'square':
                    val = 1.0 if math.sin(2.0 * math.pi * freq * t) > 0 else -1.0
                
                fade_factor = 1.0 - (i / float(num_samples))
                val = val * vol * fade_factor
                sample = max(-32768, min(32767, int(val * 32767.0)))
                wav_file.writeframes(struct.pack('<h', sample))

if __name__ == '__main__':
    generate_tone('move.wav', 600, 50, 0.1, 'square')
    generate_tone('rotate.wav', 800, 80, 0.1, 'sine')
    generate_tone('drop.wav', 150, 150, 0.2, 'square')
    
    generate_sequence('clear.wav', [(523.25, 100, 0.2), (659.25, 100, 0.2), (783.99, 100, 0.2), (1046.50, 400, 0.2)], 'sine')
    
    generate_sequence('gameover.wav', [(300, 300, 0.2), (250, 300, 0.2), (200, 300, 0.2), (150, 800, 0.2)], 'square')
    print("Sounds generated successfully!")
