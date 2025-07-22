# dungeon_music_generator.py - Creates atmospheric 8-bit dungeon themes
import wave
import math
import struct
import os
import random

class DungeonComposer:
    """8-bit composer specialized in dark, atmospheric dungeon music."""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.sounds_dir = "sounds"
        
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)
        
        # Slower, more ominous tempo for dungeons
        self.BPM = 95
        self.beat_duration = 60.0 / self.BPM
        self.measure_duration = self.beat_duration * 4
        
        # Note frequencies - emphasizing lower, darker registers
        self.notes = {
            'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89, 'E1': 41.20,
            'F1': 43.65, 'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00,
            'A#1': 58.27, 'B1': 61.74,
            
            'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41,
            'F2': 87.31, 'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00,
            'A#2': 116.54, 'B2': 123.47,
            
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81,
            'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00,
            'A#3': 233.08, 'B3': 246.94,
            
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63,
            'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
            'A#4': 466.16, 'B4': 493.88,
            
            'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
            
            'REST': 0
        }
    
    def generate_wave(self, frequency, duration, wave_type='dark_square', amplitude=0.3, envelope='haunting'):
        """Generate darker, more atmospheric waveforms for dungeon music."""
        if frequency == 0:
            return [0] * int(duration * self.sample_rate)
        
        samples = int(duration * self.sample_rate)
        wave_data = []
        
        for i in range(samples):
            t = i / self.sample_rate
            
            if wave_type == 'dark_square':
                # Square wave with harmonic distortion for dark feel
                base = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
                # Add dissonant harmonic
                harmonic = 0.3 * (1 if math.sin(2 * math.pi * frequency * 1.5 * t) > 0 else -1)
                value = amplitude * (base + harmonic) * 0.7
            elif wave_type == 'ominous_triangle':
                # Triangle wave with slight detuning for unsettling feel
                detune = 1.003  # Slight detuning
                value = amplitude * (2 / math.pi) * math.asin(math.sin(2 * math.pi * frequency * detune * t))
            elif wave_type == 'deep_pulse':
                # Very deep pulse wave for bass
                cycle_pos = (t * frequency) % 1
                value = amplitude * (1 if cycle_pos < 0.2 else -1)
            elif wave_type == 'tremolo':
                # Sine wave with tremolo effect
                tremolo_freq = 4  # 4 Hz tremolo
                tremolo = 0.5 + 0.5 * math.sin(2 * math.pi * tremolo_freq * t)
                value = amplitude * math.sin(2 * math.pi * frequency * t) * tremolo
            elif wave_type == 'noise':
                # Filtered noise for atmospheric effects
                value = amplitude * (random.random() * 2 - 1) * 0.3
            else:
                value = amplitude * math.sin(2 * math.pi * frequency * t)
            
            wave_data.append(value)
        
        # Apply envelope
        if envelope == 'haunting':
            wave_data = self.apply_haunting_envelope(wave_data)
        elif envelope == 'fade':
            wave_data = self.apply_fade_envelope(wave_data)
        elif envelope == 'drone':
            wave_data = self.apply_drone_envelope(wave_data)
        
        return wave_data
    
    def apply_haunting_envelope(self, wave_data, attack_ratio=0.25, release_ratio=0.3):
        """Apply slow, mysterious envelope."""
        total_samples = len(wave_data)
        attack_samples = int(total_samples * attack_ratio)
        release_samples = int(total_samples * release_ratio)
        
        for i in range(total_samples):
            if i < attack_samples:
                # Slow, creeping attack
                progress = i / attack_samples
                envelope = progress * progress * progress  # Cubic ease-in
            elif i >= total_samples - release_samples:
                # Mysterious fade
                progress = (i - (total_samples - release_samples)) / release_samples
                envelope = (1.0 - progress) ** 1.5
            else:
                envelope = 1.0
            
            wave_data[i] *= envelope
        
        return wave_data
    
    def apply_fade_envelope(self, wave_data, fade_ratio=0.2):
        """Apply gradual fade for atmospheric pads."""
        total_samples = len(wave_data)
        fade_samples = int(total_samples * fade_ratio)
        
        for i in range(total_samples):
            if i < fade_samples:
                envelope = i / fade_samples
            elif i >= total_samples - fade_samples:
                progress = (i - (total_samples - fade_samples)) / fade_samples
                envelope = 1.0 - progress
            else:
                envelope = 1.0
            
            wave_data[i] *= envelope
        
        return wave_data
    
    def apply_drone_envelope(self, wave_data):
        """Apply minimal envelope for drone/ambient elements."""
        total_samples = len(wave_data)
        fade_samples = min(1000, total_samples // 10)
        
        for i in range(total_samples):
            if i < fade_samples:
                envelope = i / fade_samples
            elif i >= total_samples - fade_samples:
                progress = (i - (total_samples - fade_samples)) / fade_samples
                envelope = 1.0 - progress
            else:
                envelope = 1.0
            
            wave_data[i] *= envelope
        
        return wave_data
    
    def create_dungeon_melody(self):
        """Create a sparse, haunting melody - echoes in the darkness."""
        # Melody in D minor (dark, mysterious key)
        melody_a = [
            ('D4', 3), ('REST', 1), ('F4', 2), ('G4', 2),
            ('A4', 4), ('REST', 2), ('G4', 1), ('F4', 1),
            ('E4', 3), ('REST', 1), ('D4', 4),
            ('REST', 8),
            
            ('A4', 2), ('REST', 1), ('G4', 1), ('F4', 2), ('E4', 2),
            ('D4', 3), ('REST', 1), ('F4', 2), ('A4', 2),
            ('G4', 4), ('F4', 2), ('E4', 2),
            ('D4', 6), ('REST', 2)
        ]
        
        melody_b = [
            ('A#4', 2), ('REST', 1), ('A4', 1), ('G4', 2), ('F4', 2),
            ('E4', 3), ('REST', 1), ('D4', 4),
            ('REST', 4), ('F4', 2), ('G4', 2),
            ('A4', 6), ('REST', 2),
            
            ('C5', 2), ('REST', 1), ('A#4', 1), ('A4', 2), ('G4', 2),
            ('F4', 3), ('REST', 1), ('E4', 2), ('D4', 2),
            ('C4', 2), ('D4', 2), ('E4', 2), ('F4', 2),
            ('D4', 8)
        ]
        
        return melody_a + melody_b
    
    def create_dungeon_atmosphere(self):
        """Create atmospheric pad - like wind through stone corridors."""
        atmosphere = [
            ('D2', 8), ('REST', 2), ('F2', 6),
            ('REST', 4), ('G2', 8),
            ('E2', 6), ('REST', 2), ('D2', 8),
            ('REST', 8),
            
            ('A2', 8), ('REST', 2), ('G2', 6),
            ('F2', 8), ('E2', 8),
            ('D2', 6), ('REST', 2), ('F2', 8),
            ('D2', 16)
        ]
        
        return atmosphere
    
    def create_dungeon_bass(self):
        """Create ominous, droning bassline."""
        bass_pattern = [
            ('D1', 4), ('REST', 2), ('D1', 2),
            ('A1', 4), ('REST', 2), ('A1', 2),
            ('F1', 4), ('REST', 2), ('F1', 2),
            ('G1', 4), ('D1', 4),
            
            ('D1', 6), ('REST', 2),
            ('A#1', 4), ('REST', 2), ('A#1', 2),
            ('A1', 4), ('REST', 2), ('A1', 2),
            ('D1', 8)
        ]
        
        return bass_pattern * 2
    
    def create_dungeon_percussion(self):
        """Create subtle, echoing percussion - like dripping water."""
        percussion = []
        beats_per_measure = 4
        total_measures = 16
        
        for measure in range(total_measures):
            for beat in range(beats_per_measure):
                if measure % 4 == 0 and beat == 0:  # Occasional deep thud
                    percussion.append(('THUD', 0.5))
                    percussion.append(('REST', 3.5))
                elif random.random() < 0.15:  # Random drips
                    percussion.append(('DRIP', 0.125))
                    percussion.append(('REST', 3.875))
                else:
                    percussion.append(('REST', 4))
        
        return percussion
    
    def create_dungeon_ambience(self):
        """Create subtle ambient sounds - mysterious echoes."""
        ambience = []
        
        # Sparse, mysterious sounds at irregular intervals
        for i in range(64):  # 64 beats total
            if random.random() < 0.08:  # 8% chance of ambient sound
                sound_type = random.choice(['ECHO', 'WHISPER', 'CLANK'])
                ambience.append((sound_type, 0.5))
                ambience.append(('REST', 3.5))
            else:
                ambience.append(('REST', 4))
        
        return ambience
    
    def sequence_to_audio(self, sequence, wave_type='dark_square', amplitude=0.3, envelope='haunting'):
        """Convert note sequence to audio with dungeon-appropriate settings."""
        audio_data = []
        
        for note, duration_beats in sequence:
            duration_seconds = duration_beats * self.beat_duration
            
            if note == 'THUD':
                # Deep thud: very low frequency pulse
                wave_data = self.generate_wave(40, duration_seconds, 'deep_pulse', amplitude * 1.2, 'fade')
            elif note == 'DRIP':
                # Water drip: high frequency click with quick decay
                wave_data = self.generate_wave(2000, duration_seconds, 'dark_square', amplitude * 0.4, 'fade')
            elif note == 'ECHO':
                # Mysterious echo: detuned tone
                wave_data = self.generate_wave(150, duration_seconds, 'ominous_triangle', amplitude * 0.3, 'haunting')
            elif note == 'WHISPER':
                # Whisper: filtered noise
                wave_data = self.generate_wave(0, duration_seconds, 'noise', amplitude * 0.2, 'fade')
            elif note == 'CLANK':
                # Distant clank: metallic sound
                wave_data = self.generate_wave(800, duration_seconds, 'dark_square', amplitude * 0.3, 'fade')
            else:
                frequency = self.notes.get(note, 0)
                wave_data = self.generate_wave(frequency, duration_seconds, wave_type, amplitude, envelope)
            
            audio_data.extend(wave_data)
        
        return audio_data
    
    def mix_tracks(self, *tracks):
        """Mix multiple tracks with dungeon-appropriate levels."""
        max_length = max(len(track) for track in tracks)
        
        padded_tracks = []
        for track in tracks:
            padded = track + [0] * (max_length - len(track))
            padded_tracks.append(padded)
        
        mixed = []
        for i in range(max_length):
            sample = sum(track[i] for track in padded_tracks)
            sample = max(-1.0, min(1.0, sample))
            mixed.append(sample)
        
        return mixed
    
    def add_echo_reverb(self, audio_data, decay=0.4, delay_samples=2000):
        """Add deep, cavernous reverb for dungeon atmosphere."""
        reverb_audio = audio_data[:]
        
        # Multiple echo delays for cavernous feel
        delays = [delay_samples, int(delay_samples * 1.5), int(delay_samples * 2.2)]
        decays = [decay, decay * 0.6, decay * 0.3]
        
        for delay, decay_factor in zip(delays, decays):
            for i in range(delay, len(audio_data)):
                reverb_audio[i] += audio_data[i - delay] * decay_factor
        
        return reverb_audio
    
    def add_low_pass_filter(self, audio_data, cutoff_freq=2000):
        """Add low-pass filter for muffled, underground feel."""
        # Simple first-order low-pass filter
        rc = 1.0 / (cutoff_freq * 2 * math.pi)
        dt = 1.0 / self.sample_rate
        alpha = dt / (rc + dt)
        
        filtered_audio = [audio_data[0]]
        for i in range(1, len(audio_data)):
            filtered_sample = filtered_audio[i-1] + alpha * (audio_data[i] - filtered_audio[i-1])
            filtered_audio.append(filtered_sample)
        
        return filtered_audio
    
    def normalize_audio(self, audio_data, target_amplitude=0.5):
        """Normalize at lower level for atmospheric dungeon mood."""
        max_amplitude = max(abs(sample) for sample in audio_data)
        if max_amplitude > 0:
            scale_factor = target_amplitude / max_amplitude
            return [sample * scale_factor for sample in audio_data]
        return audio_data
    
    def save_audio(self, audio_data, filename):
        """Save dungeon music to file."""
        filepath = os.path.join(self.sounds_dir, filename)
        audio_int16 = [int(sample * 32767) for sample in audio_data]
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            
            frames = []
            for sample in audio_int16:
                frames.append(struct.pack('<h', sample))
            
            wav_file.writeframes(b''.join(frames))
        
        return filepath
    
    def create_dungeon_theme(self):
        """Create the complete atmospheric dungeon theme."""
        print("🏰 Composing Atmospheric Dungeon Theme 🏰")
        print("=" * 50)
        
        # Create all musical layers
        print("🎼 Creating haunting melody...")
        melody_sequence = self.create_dungeon_melody()
        melody_audio = self.sequence_to_audio(melody_sequence, 'ominous_triangle', 0.35, 'haunting')
        
        print("🎼 Creating atmospheric pad...")
        atmosphere_sequence = self.create_dungeon_atmosphere()
        atmosphere_audio = self.sequence_to_audio(atmosphere_sequence, 'tremolo', 0.2, 'fade')
        
        print("🎼 Creating ominous bassline...")
        bass_sequence = self.create_dungeon_bass()
        bass_audio = self.sequence_to_audio(bass_sequence, 'deep_pulse', 0.4, 'drone')
        
        print("🥁 Creating subtle percussion...")
        percussion_sequence = self.create_dungeon_percussion()
        percussion_audio = self.sequence_to_audio(percussion_sequence, 'dark_square', 0.3, 'fade')
        
        print("🌫️  Creating ambient sounds...")
        ambience_sequence = self.create_dungeon_ambience()
        ambience_audio = self.sequence_to_audio(ambience_sequence, 'noise', 0.15, 'fade')
        
        # Mix all tracks
        print("🎛️  Mixing dungeon atmosphere...")
        mixed_audio = self.mix_tracks(melody_audio, atmosphere_audio, bass_audio, percussion_audio, ambience_audio)
        
        # Add atmospheric effects
        print("🔊 Adding cavernous reverb...")
        mixed_audio = self.add_echo_reverb(mixed_audio, decay=0.3, delay_samples=1500)
        
        print("🎚️  Applying atmospheric filter...")
        mixed_audio = self.add_low_pass_filter(mixed_audio, cutoff_freq=3000)
        
        # Normalize for atmospheric listening
        print("🔊 Normalizing for atmosphere...")
        mixed_audio = self.normalize_audio(mixed_audio, 0.45)
        
        # Save the dungeon theme
        print("💾 Saving dungeon theme...")
        filepath = self.save_audio(mixed_audio, "dungeon_theme.wav")
        
        # Stats
        duration = len(mixed_audio) / self.sample_rate
        file_size = os.path.getsize(filepath)
        
        print(f"\n⚔️  DUNGEON THEME COMPLETE! ⚔️")
        print("=" * 50)
        print(f"📁 File: {filepath}")
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"🎵 BPM: {self.BPM} (ominous tempo)")
        print(f"🎼 Key: D Minor (dark and mysterious)")
        print(f"🎨 Style: Atmospheric, haunting, sparse")
        print(f"🔄 Perfect for: Dungeon exploration, tension, mystery")
        
        return filepath
    
    def create_dungeon_loop(self):
        """Create a shorter dungeon loop for continuous exploration."""
        print("\n🔄 Creating dungeon loop version...")
        
        # Simpler, more atmospheric loop
        loop_melody = [
            ('D4', 4), ('REST', 2), ('F4', 2),
            ('E4', 3), ('REST', 1), ('D4', 4),
            ('REST', 8),
            ('A4', 2), ('G4', 2), ('F4', 2), ('E4', 2),
            ('D4', 8)
        ]
        
        loop_atmosphere = [
            ('D2', 8), ('F2', 8),
            ('E2', 8), ('D2', 8)
        ]
        
        loop_bass = [
            ('D1', 8), ('A1', 8),
            ('F1', 8), ('D1', 8)
        ]
        
        # Generate audio
        melody_audio = self.sequence_to_audio(loop_melody, 'ominous_triangle', 0.35, 'haunting')
        atmosphere_audio = self.sequence_to_audio(loop_atmosphere, 'tremolo', 0.2, 'fade')
        bass_audio = self.sequence_to_audio(loop_bass, 'deep_pulse', 0.4, 'drone')
        
        # Mix and process
        mixed_audio = self.mix_tracks(melody_audio, atmosphere_audio, bass_audio)
        mixed_audio = self.add_echo_reverb(mixed_audio, decay=0.25, delay_samples=1000)
        mixed_audio = self.add_low_pass_filter(mixed_audio, cutoff_freq=2500)
        mixed_audio = self.normalize_audio(mixed_audio, 0.45)
        
        # Save loop version
        loop_filepath = self.save_audio(mixed_audio, "dungeon_theme_loop.wav")
        
        duration = len(mixed_audio) / self.sample_rate
        print(f"🔄 Dungeon loop created: {duration:.1f} seconds")
        
        return loop_filepath
    
    def create_dungeon_ambient(self):
        """Create pure ambient version for very quiet exploration."""
        print("\n🌫️  Creating dungeon ambient version...")
        
        # Just atmosphere and bass, no melody
        ambient_atmosphere = [
            ('D2', 16), ('F2', 16),
            ('E2', 16), ('A2', 16),
            ('G2', 16), ('D2', 16)
        ]
        
        ambient_bass = [
            ('D1', 32), ('A1', 32), ('D1', 32)
        ]
        
        # Very quiet ambience
        ambient_sounds = []
        for _ in range(24):  # 24 measures of sparse ambience
            if random.random() < 0.1:
                ambient_sounds.append(('ECHO', 1))
                ambient_sounds.append(('REST', 15))
            else:
                ambient_sounds.append(('REST', 16))
        
        # Generate audio at lower volumes
        atmosphere_audio = self.sequence_to_audio(ambient_atmosphere, 'tremolo', 0.15, 'fade')
        bass_audio = self.sequence_to_audio(ambient_bass, 'deep_pulse', 0.25, 'drone')
        ambience_audio = self.sequence_to_audio(ambient_sounds, 'ominous_triangle', 0.1, 'fade')
        
        # Mix and process
        mixed_audio = self.mix_tracks(atmosphere_audio, bass_audio, ambience_audio)
        mixed_audio = self.add_echo_reverb(mixed_audio, decay=0.4, delay_samples=2000)
        mixed_audio = self.add_low_pass_filter(mixed_audio, cutoff_freq=1500)
        mixed_audio = self.normalize_audio(mixed_audio, 0.3)
        
        # Save ambient version
        ambient_filepath = self.save_audio(mixed_audio, "dungeon_ambient.wav")
        
        duration = len(mixed_audio) / self.sample_rate
        print(f"🌫️  Dungeon ambient created: {duration:.1f} seconds")
        
        return ambient_filepath

def create_dungeon_music():
    """Main function to create dungeon music."""
    composer = DungeonComposer()
    
    full_theme = composer.create_dungeon_theme()
    loop_theme = composer.create_dungeon_loop()
    ambient_theme = composer.create_dungeon_ambient()
    
    return {
        'dungeon_full': full_theme,
        'dungeon_loop': loop_theme,
        'dungeon_ambient': ambient_theme
    }

if __name__ == "__main__":
    try:
        print("🏰 8-BIT DUNGEON MUSIC COMPOSER 🏰")
        print("Creating dark, atmospheric dungeon music...")
        print()
        
        music_files = create_dungeon_music()
        
        print(f"\n✅ Dungeon music generation complete!")
        print("🎵 Files created:")
        for name, filepath in music_files.items():
            size = os.path.getsize(filepath)
            print(f"   ⚔️  {name}: {os.path.basename(filepath)} ({size/1024:.1f} KB)")
        
        print("\n🏰 Perfect for mysterious dungeon exploration!")
        print("💡 Use ambient version for stealth, loop for general exploration")
        
    except Exception as e:
        print(f"❌ Error creating dungeon music: {e}")
        import traceback
        traceback.print_exc()