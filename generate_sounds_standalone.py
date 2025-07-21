# generate_sounds_standalone.py - Simple standalone sound generator
import numpy as np
import wave
import os
import math

def create_8bit_movement_sounds():
    """
    Standalone function to create 8-bit style movement sounds.
    No external dependencies except numpy and wave (built-in).
    """
    
    print("🎵 Generating 8-bit Movement Sounds 🎵")
    print("=" * 40)
    
    # Create sounds directory
    sounds_dir = "sounds"
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        print(f"📁 Created {sounds_dir} directory")
    
    sample_rate = 22050
    
    def generate_wave(frequency, duration, wave_type='square', amplitude=0.3):
        """Generate basic waveform."""
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        if wave_type == 'square':
            wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'triangle':
            wave = amplitude * 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        elif wave_type == 'noise':
            wave = amplitude * (2 * np.random.random(samples) - 1)
        else:  # sine
            wave = amplitude * np.sin(2 * np.pi * frequency * t)
        
        return wave
    
    def apply_envelope(wave, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
        """Apply ADSR envelope."""
        total_samples = len(wave)
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)
        sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)
        
        envelope = np.ones(total_samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0:
            start = attack_samples
            end = attack_samples + decay_samples
            envelope[start:end] = np.linspace(1, sustain, decay_samples)
        
        # Sustain
        if sustain_samples > 0:
            start = attack_samples + decay_samples
            end = start + sustain_samples
            envelope[start:end] = sustain
        
        # Release
        if release_samples > 0:
            start = total_samples - release_samples
            envelope[start:] = np.linspace(sustain, 0, release_samples)
        
        return wave * envelope
    
    def save_wave(wave, filename):
        """Save waveform as WAV file."""
        # Normalize and convert to 16-bit
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.8
        wave_int = (wave * 32767).astype(np.int16)
        
        filepath = os.path.join(sounds_dir, filename)
        
        # Use the correct wave module syntax
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample  
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(wave_int.tobytes())
        
        return filepath
    
    # Generate Warrior footsteps (heavy, armored)
    print("⚔️  Generating Warrior footsteps...")
    thump = generate_wave(80, 0.15, 'square', 0.6)
    thump = apply_envelope(thump, 0.001, 0.03, 0.4, 0.12)
    
    clank = generate_wave(1200, 0.08, 'square', 0.3)  
    clank = apply_envelope(clank, 0.001, 0.02, 0.2, 0.06)
    
    # Mix thump and clank
    max_len = max(len(thump), len(clank))
    warrior_sound = np.zeros(max_len)
    warrior_sound[:len(thump)] += thump
    warrior_sound[:len(clank)] += clank
    
    warrior_path = save_wave(warrior_sound, "heavy_footsteps.wav")
    print(f"   ✅ Saved: {warrior_path}")
    
    # Generate Expert footsteps (soft, stealthy)
    print("🗡️  Generating Expert footsteps...")
    pad = generate_wave(200, 0.1, 'triangle', 0.3)
    pad = apply_envelope(pad, 0.01, 0.02, 0.6, 0.07)
    
    creak = generate_wave(400, 0.08, 'triangle', 0.2)
    creak = apply_envelope(creak, 0.005, 0.015, 0.3, 0.06)
    
    # Mix pad and creak
    max_len = max(len(pad), len(creak))
    expert_sound = np.zeros(max_len)
    expert_sound[:len(pad)] += pad
    expert_sound[:len(creak)] += creak
    
    expert_path = save_wave(expert_sound, "soft_footsteps.wav")
    print(f"   ✅ Saved: {expert_path}")
    
    # Generate Mage staff taps (magical, crystalline)
    print("🔮 Generating Mage staff taps...")
    tap = generate_wave(800, 0.12, 'square', 0.4)
    tap = apply_envelope(tap, 0.001, 0.02, 0.3, 0.1)
    
    chime = generate_wave(1600, 0.15, 'sine', 0.25)
    chime = apply_envelope(chime, 0.002, 0.03, 0.5, 0.12)
    
    shimmer = generate_wave(3200, 0.1, 'triangle', 0.15)
    shimmer = apply_envelope(shimmer, 0.005, 0.02, 0.3, 0.08)
    
    # Mix all mage components
    max_len = max(len(tap), len(chime), len(shimmer))
    mage_sound = np.zeros(max_len)
    mage_sound[:len(tap)] += tap
    mage_sound[:len(chime)] += chime  
    mage_sound[:len(shimmer)] += shimmer
    
    mage_path = save_wave(mage_sound, "staff_taps.wav")
    print(f"   ✅ Saved: {mage_path}")
    
    print("\n🎉 Generation Complete!")
    print("=" * 40)
    print("📂 Files created in 'sounds/' directory:")
    print(f"   🛡️  heavy_footsteps.wav - Warrior (armored clanking)")
    print(f"   🏃 soft_footsteps.wav - Expert (stealthy padding)")
    print(f"   ✨ staff_taps.wav - Mage (magical staff taps)")
    print("\n🎵 These are completely original 8-bit style sounds!")
    print("🔊 Ready to use in your game!")
    
    return {
        "Warrior": warrior_path,
        "Expert": expert_path, 
        "Mage": mage_path
    }

if __name__ == "__main__":
    # Just run the generator
    try:
        sounds = create_8bit_movement_sounds()
        print(f"\n✅ Successfully generated {len(sounds)} movement sounds!")
    except ImportError:
        print("❌ Error: This script requires numpy")
        print("Install with: pip install numpy")
    except Exception as e:
        print(f"❌ Error generating sounds: {e}")