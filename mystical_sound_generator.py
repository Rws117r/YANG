# mystical_sound_generator.py - Generate magical spell preparation sounds
import numpy as np
import wave
import os
import math

def create_mystical_sound(filename, duration=1.2, sample_rate=22050, base_frequency=220):
    """
    Generate a mystical, otherworldly sound for spell preparation.
    
    Args:
        filename: Output filename
        duration: Length of sound in seconds
        sample_rate: Audio sample rate
        base_frequency: Base frequency for the mystical tone
    """
    
    # Calculate number of samples
    num_samples = int(duration * sample_rate)
    
    # Time array
    t = np.linspace(0, duration, num_samples, False)
    
    # Create base mystical drone
    # Use multiple harmonics for richness
    wave_data = np.zeros(num_samples)
    
    # Fundamental frequency with slow vibrato
    vibrato = 0.05 * np.sin(2 * np.pi * 4 * t)  # 4 Hz vibrato
    fundamental = np.sin(2 * np.pi * base_frequency * (1 + vibrato) * t)
    
    # Add harmonics for mystical timbre
    harmonics = [
        (0.8, 1.0),    # Fundamental
        (0.3, 1.5),    # Perfect fifth
        (0.2, 2.0),    # Octave
        (0.15, 2.5),   # Major third above octave
        (0.1, 3.0),    # Perfect fifth above octave
        (0.05, 4.0),   # Two octaves
    ]
    
    for amplitude, frequency_mult in harmonics:
        harmonic_freq = base_frequency * frequency_mult
        harmonic_vibrato = 0.03 * np.sin(2 * np.pi * (4 + frequency_mult) * t)
        harmonic = amplitude * np.sin(2 * np.pi * harmonic_freq * (1 + harmonic_vibrato) * t)
        wave_data += harmonic
    
    # Add mystical "shimmer" effect with high frequency sparkles
    shimmer_freq = base_frequency * 8
    shimmer_amplitude = 0.1 * np.sin(2 * np.pi * 0.5 * t)  # Slow amplitude modulation
    shimmer = shimmer_amplitude * np.sin(2 * np.pi * shimmer_freq * t)
    wave_data += shimmer
    
    # Add magical "power buildup" effect
    buildup_envelope = np.power(t / duration, 0.7)  # Gradual power increase
    magical_noise = 0.05 * np.random.normal(0, 1, num_samples)
    filtered_noise = np.convolve(magical_noise, np.ones(100)/100, mode='same')  # Smooth the noise
    wave_data += buildup_envelope * filtered_noise
    
    # Apply overall envelope (fade in, sustain, fade out)
    envelope = np.ones(num_samples)
    fade_samples = int(0.1 * sample_rate)  # 100ms fade
    
    # Fade in
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    # Fade out
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    # Apply envelope
    wave_data *= envelope
    
    # Normalize to prevent clipping
    max_amplitude = np.max(np.abs(wave_data))
    if max_amplitude > 0:
        wave_data = wave_data / max_amplitude * 0.8  # Leave headroom
    
    # Convert to 16-bit integers
    wave_data = (wave_data * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"Generated mystical sound: {filename}")

def create_level_specific_sounds():
    """Generate spell preparation sounds for different level ranges."""
    
    # Ensure sounds directory exists
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    
    # Define level ranges and their characteristics
    level_ranges = [
        {
            "name": "novice_prep",
            "levels": "1-2",
            "duration": 1.0,
            "base_freq": 220,  # A3
            "description": "Gentle, learning magic"
        },
        {
            "name": "adept_prep", 
            "levels": "3-4",
            "duration": 1.1,
            "base_freq": 196,  # G3
            "description": "More confident, deeper tones"
        },
        {
            "name": "expert_prep",
            "levels": "5-6", 
            "duration": 1.2,
            "base_freq": 174.6,  # F3
            "description": "Powerful, resonant magic"
        },
        {
            "name": "master_prep",
            "levels": "7+",
            "duration": 1.3,
            "base_freq": 146.8,  # D3
            "description": "Ancient, otherworldly power"
        }
    ]
    
    for level_range in level_ranges:
        filename = os.path.join("sounds", f"{level_range['name']}.wav")
        
        print(f"Generating {level_range['description']} (Levels {level_range['levels']})...")
        
        # Adjust characteristics based on level
        duration = level_range['duration']
        base_freq = level_range['base_freq']
        
        # Higher level sounds get more complex harmonics
        if "master" in level_range['name']:
            # Master level: Add ethereal high frequencies and deeper bass
            create_mystical_sound(
                filename, 
                duration=duration, 
                base_frequency=base_freq
            )
            
            # Post-process for master level: add extra mystical elements
            add_master_level_effects(filename)
            
        elif "expert" in level_range['name']:
            # Expert level: Rich harmonics, more power
            create_mystical_sound(
                filename,
                duration=duration,
                base_frequency=base_freq
            )
            
        elif "adept" in level_range['name']:
            # Adept level: Moderate complexity
            create_mystical_sound(
                filename,
                duration=duration, 
                base_frequency=base_freq
            )
            
        else:
            # Novice level: Simple, clean tones
            create_mystical_sound(
                filename,
                duration=duration,
                base_frequency=base_freq
            )

def add_master_level_effects(filename):
    """Add extra mystical effects to master level sounds."""
    
    # Read the existing file
    with wave.open(filename, 'r') as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
        sample_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
    
    # Convert to numpy array
    if sample_width == 2:
        audio_data = np.frombuffer(frames, dtype=np.int16)
    else:
        audio_data = np.frombuffer(frames, dtype=np.int8)
    
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32) / 32767.0
    
    # Add ethereal echo effect
    delay_samples = int(0.3 * sample_rate)  # 300ms delay
    echo_strength = 0.3
    
    if len(audio_float) > delay_samples:
        echo = np.zeros_like(audio_float)
        echo[delay_samples:] = audio_float[:-delay_samples] * echo_strength
        audio_float += echo
    
    # Add subtle reverb-like effect
    reverb_length = int(0.1 * sample_rate)
    reverb_kernel = np.exp(-np.linspace(0, 5, reverb_length))
    reverb_kernel /= np.sum(reverb_kernel)
    
    audio_with_reverb = np.convolve(audio_float, reverb_kernel, mode='same')
    audio_float = 0.7 * audio_float + 0.3 * audio_with_reverb
    
    # Normalize and convert back
    max_amplitude = np.max(np.abs(audio_float))
    if max_amplitude > 0:
        audio_float = audio_float / max_amplitude * 0.8
    
    audio_data = (audio_float * 32767).astype(np.int16)
    
    # Save the enhanced version
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"Enhanced master level sound: {filename}")

def create_glyph_progression_sounds():
    """Create subtle sounds for each glyph transition in the animation."""
    
    glyph_sounds = [
        ("glyph_dot", 0.1, 440),      # Quick, high ping for dot appearance
        ("glyph_target", 0.15, 523),  # Target lock sound
        ("glyph_circle", 0.1, 659),   # Circle completion
        ("glyph_empty_star", 0.15, 784),  # Star formation
        ("glyph_filled_star", 0.2, 880)   # Star completion
    ]
    
    for name, duration, frequency in glyph_sounds:
        filename = os.path.join("sounds", f"{name}.wav")
        create_simple_magical_ping(filename, duration, frequency)

def create_simple_magical_ping(filename, duration=0.1, frequency=440):
    """Create a simple magical ping sound for glyph transitions."""
    
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, False)
    
    # Create a bell-like tone with harmonics
    wave_data = np.zeros(num_samples)
    
    # Fundamental with sharp attack and quick decay
    envelope = np.exp(-5 * t)  # Quick decay
    fundamental = envelope * np.sin(2 * np.pi * frequency * t)
    
    # Add some harmonics for magical quality
    harmonic2 = 0.3 * envelope * np.sin(2 * np.pi * frequency * 2 * t)
    harmonic3 = 0.1 * envelope * np.sin(2 * np.pi * frequency * 3 * t)
    
    wave_data = fundamental + harmonic2 + harmonic3
    
    # Add slight pitch bend for magical effect
    pitch_bend = 1 + 0.1 * np.exp(-10 * t) * np.sin(2 * np.pi * 20 * t)
    wave_data *= pitch_bend
    
    # Normalize
    max_amplitude = np.max(np.abs(wave_data))
    if max_amplitude > 0:
        wave_data = wave_data / max_amplitude * 0.6
    
    # Convert to 16-bit
    wave_data = (wave_data * 32767).astype(np.int16)
    
    # Save
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"Generated glyph sound: {filename}")

if __name__ == "__main__":
    print("Generating mystical spell preparation sounds...")
    
    # Generate level-specific preparation sounds
    create_level_specific_sounds()
    
    # Generate glyph progression sounds
    print("\nGenerating glyph transition sounds...")
    create_glyph_progression_sounds()
    
    print("\nMystical sound generation complete!")
    print("Generated sounds:")
    print("- novice_prep.wav (Levels 1-2)")
    print("- adept_prep.wav (Levels 3-4)")
    print("- expert_prep.wav (Levels 5-6)")
    print("- master_prep.wav (Levels 7+)")
    print("- glyph_*.wav (Glyph transition sounds)")