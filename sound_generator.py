# sound_generator.py - Generate 8-bit style movement sounds
import numpy as np
import wave
import os
import math

class ChiptuneSoundGenerator:
    """Generates 8-bit style sound effects for the game."""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.sounds_dir = "sounds"
        
        # Create sounds directory if it doesn't exist
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)
    
    def generate_wave(self, frequency, duration, wave_type='square', amplitude=0.3):
        """Generate a basic waveform."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        if wave_type == 'square':
            wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'sine':
            wave = amplitude * np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'triangle':
            wave = amplitude * 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        elif wave_type == 'sawtooth':
            wave = amplitude * 2 * (t * frequency - np.floor(t * frequency + 0.5))
        elif wave_type == 'noise':
            wave = amplitude * (2 * np.random.random(samples) - 1)
        else:
            wave = amplitude * np.sin(2 * np.pi * frequency * t)
        
        return wave
    
    def apply_envelope(self, wave, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
        """Apply ADSR envelope to a waveform."""
        total_samples = len(wave)
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        envelope = np.ones(total_samples)
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = attack_samples + decay_samples
            envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)
        
        # Sustain
        if sustain_samples > 0:
            start_idx = attack_samples + decay_samples
            end_idx = start_idx + sustain_samples
            envelope[start_idx:end_idx] = sustain
        
        # Release
        if release_samples > 0:
            start_idx = total_samples - release_samples
            envelope[start_idx:] = np.linspace(sustain, 0, release_samples)
        
        return wave * envelope
    
    def mix_waves(self, *waves):
        """Mix multiple waveforms together."""
        max_length = max(len(wave) for wave in waves)
        mixed = np.zeros(max_length)
        
        for wave in waves:
            # Pad shorter waves with zeros
            padded = np.pad(wave, (0, max_length - len(wave)), 'constant')
            mixed += padded
        
        # Normalize to prevent clipping
        if np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.8
        
        return mixed
    
    def save_wave(self, wave, filename):
        """Save waveform as WAV file."""
        # Convert to 16-bit integers
        wave_int = (wave * 32767).astype(np.int16)
        
        filepath = os.path.join(self.sounds_dir, filename)
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(wave_int.tobytes())
        
        print(f"[SOUND] Generated {filename}")
        return filepath
    
    def generate_warrior_footstep(self):
        """Generate heavy, armor-clanking footstep for Warrior."""
        # Base thump (low frequency)
        thump = self.generate_wave(80, 0.15, 'square', 0.6)
        thump = self.apply_envelope(thump, attack=0.001, decay=0.03, sustain=0.4, release=0.12)
        
        # Metal clank (higher frequency, short)
        clank = self.generate_wave(1200, 0.08, 'square', 0.3)
        clank = self.apply_envelope(clank, attack=0.001, decay=0.02, sustain=0.2, release=0.06)
        
        # Chain mail jingle (very short, high pitched)
        jingle = self.generate_wave(2400, 0.05, 'triangle', 0.15)
        jingle = self.apply_envelope(jingle, attack=0.001, decay=0.01, sustain=0.1, release=0.04)
        
        # Mix all components
        footstep = self.mix_waves(thump, clank, jingle)
        return self.save_wave(footstep, "heavy_footsteps.wav")
    
    def generate_expert_footstep(self):
        """Generate soft, sneaky footstep for Expert."""
        # Soft pad (muffled sound)
        pad = self.generate_wave(200, 0.1, 'triangle', 0.3)
        pad = self.apply_envelope(pad, attack=0.01, decay=0.02, sustain=0.6, release=0.07)
        
        # Leather creak (mid frequency)
        creak = self.generate_wave(400, 0.08, 'sawtooth', 0.2)
        creak = self.apply_envelope(creak, attack=0.005, decay=0.015, sustain=0.3, release=0.06)
        
        # Slight cloth rustle (high frequency, very quiet)
        rustle = self.generate_wave(1800, 0.06, 'noise', 0.1)
        rustle = self.apply_envelope(rustle, attack=0.002, decay=0.01, sustain=0.2, release=0.05)
        
        # Mix components
        footstep = self.mix_waves(pad, creak, rustle)
        return self.save_wave(footstep, "soft_footsteps.wav")
    
    def generate_mage_footstep(self):
        """Generate magical staff tap for Mage."""
        # Staff tap (sharp, wooden sound)
        tap = self.generate_wave(800, 0.12, 'square', 0.4)
        tap = self.apply_envelope(tap, attack=0.001, decay=0.02, sustain=0.3, release=0.1)
        
        # Magical chime (crystal-like overtone)
        chime = self.generate_wave(1600, 0.15, 'sine', 0.25)
        chime = self.apply_envelope(chime, attack=0.002, decay=0.03, sustain=0.5, release=0.12)
        
        # Mystical shimmer (very high, ethereal)
        shimmer = self.generate_wave(3200, 0.1, 'triangle', 0.15)
        shimmer = self.apply_envelope(shimmer, attack=0.005, decay=0.02, sustain=0.3, release=0.08)
        
        # Robe swish (low frequency, soft)
        swish = self.generate_wave(150, 0.09, 'noise', 0.1)
        swish = self.apply_envelope(swish, attack=0.01, decay=0.02, sustain=0.4, release=0.06)
        
        # Mix all components
        footstep = self.mix_waves(tap, chime, shimmer, swish)
        return self.save_wave(footstep, "staff_taps.wav")
    
    def generate_all_movement_sounds(self):
        """Generate all movement sounds for the game."""
        print("[SOUND GENERATOR] Creating archetype movement sounds...")
        
        sounds = {
            "Warrior": self.generate_warrior_footstep(),
            "Expert": self.generate_expert_footstep(), 
            "Mage": self.generate_mage_footstep()
        }
        
        print("[SOUND GENERATOR] All movement sounds generated successfully!")
        return sounds

def create_movement_sounds():
    """Convenience function to generate all movement sounds."""
    generator = ChiptuneSoundGenerator()
    return generator.generate_all_movement_sounds()

if __name__ == "__main__":
    # Test the sound generator
    print("=== 8-BIT MOVEMENT SOUND GENERATOR ===")
    print("Generating original chiptune-style movement sounds...")
    
    generator = ChiptuneSoundGenerator()
    sounds = generator.generate_all_movement_sounds()
    
    print("\nGenerated sounds:")
    for archetype, filepath in sounds.items():
        print(f"  {archetype}: {filepath}")
    
    print("\nSounds saved in 'sounds/' directory")
    print("These are completely original 8-bit style sounds!")
    print("=== GENERATION COMPLETE ===")