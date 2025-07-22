# village_music_generator.py - Creates peaceful 8-bit village themes
import wave
import math
import struct
import os

class VillageComposer:
    """8-bit composer specialized in peaceful, cozy village music."""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.sounds_dir = "sounds"
        
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)
        
        # Slower, more relaxed tempo for village
        self.BPM = 85
        self.beat_duration = 60.0 / self.BPM
        self.measure_duration = self.beat_duration * 4
        
        # Note frequencies - focusing on warmer, lower registers
        self.notes = {
            'C2': 65.41, 'D2': 73.42, 'E2': 82.41, 'F2': 87.31, 'G2': 98.00, 'A2': 110.00, 'B2': 123.47,
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81,
            'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00,
            'A#3': 233.08, 'B3': 246.94,
            
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63,
            'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
            'A#4': 466.16, 'B4': 493.88,
            
            'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
            'A5': 880.00, 'B5': 987.77,
            
            'REST': 0
        }
    
    def generate_wave(self, frequency, duration, wave_type='triangle', amplitude=0.3, envelope='gentle'):
        """Generate warmer, softer waveforms suitable for village music."""
        if frequency == 0:
            return [0] * int(duration * self.sample_rate)
        
        samples = int(duration * self.sample_rate)
        wave_data = []
        
        for i in range(samples):
            t = i / self.sample_rate
            
            if wave_type == 'triangle':
                # Warm triangle wave - primary for village melodies
                value = amplitude * (2 / math.pi) * math.asin(math.sin(2 * math.pi * frequency * t))
            elif wave_type == 'soft_square':
                # Softer square wave with rounded edges
                base_square = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
                # Add slight harmonics for warmth
                harmonic = 0.2 * math.sin(4 * math.pi * frequency * t)
                value = amplitude * (base_square + harmonic) * 0.8
            elif wave_type == 'sine':
                # Pure sine for bass and gentle accompaniment
                value = amplitude * math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'warm_pulse':
                # Pulse with wider duty cycle for bass
                cycle_pos = (t * frequency) % 1
                value = amplitude * (1 if cycle_pos < 0.4 else -1)
            else:
                value = amplitude * math.sin(2 * math.pi * frequency * t)
            
            wave_data.append(value)
        
        # Apply envelope
        if envelope == 'gentle':
            wave_data = self.apply_gentle_envelope(wave_data)
        elif envelope == 'sustain':
            wave_data = self.apply_sustain_envelope(wave_data)
        
        return wave_data
    
    def apply_gentle_envelope(self, wave_data, attack_ratio=0.15, release_ratio=0.15):
        """Apply gentle, gradual envelope for peaceful sound."""
        total_samples = len(wave_data)
        attack_samples = int(total_samples * attack_ratio)
        release_samples = int(total_samples * release_ratio)
        sustain_samples = total_samples - attack_samples - release_samples
        
        for i in range(total_samples):
            if i < attack_samples:
                # Gentle attack
                progress = i / attack_samples
                envelope = progress * progress  # Ease-in curve
            elif i >= total_samples - release_samples:
                # Gentle release
                progress = (i - (total_samples - release_samples)) / release_samples
                envelope = (1.0 - progress) * (1.0 - progress)  # Ease-out curve
            else:
                envelope = 1.0
            
            wave_data[i] *= envelope
        
        return wave_data
    
    def apply_sustain_envelope(self, wave_data, attack_ratio=0.1, release_ratio=0.1):
        """Simple sustain for bass notes."""
        total_samples = len(wave_data)
        attack_samples = int(total_samples * attack_ratio)
        release_samples = int(total_samples * release_ratio)
        
        for i in range(total_samples):
            if i < attack_samples:
                envelope = i / attack_samples
            elif i >= total_samples - release_samples:
                progress = (i - (total_samples - release_samples)) / release_samples
                envelope = 1.0 - progress
            else:
                envelope = 1.0
            
            wave_data[i] *= envelope
        
        return wave_data
    
    def create_village_melody(self):
        """Create a peaceful, folksy melody - like a gentle breeze."""
        # Melody in F major (warm, peaceful key)
        melody_a = [
            ('F4', 2), ('G4', 1), ('A4', 1), ('A#4', 2), ('A4', 1), ('G4', 1),
            ('F4', 4), ('REST', 2), ('C4', 1), ('D4', 1),
            ('F4', 2), ('E4', 1), ('D4', 1), ('C4', 4),
            ('REST', 4),
            
            ('A4', 1), ('G4', 1), ('F4', 2), ('G4', 1), ('A4', 1), ('A#4', 2),
            ('C5', 2), ('A#4', 1), ('A4', 1), ('G4', 2), ('F4', 2),
            ('E4', 1), ('F4', 1), ('G4', 2), ('F4', 4),
            ('REST', 4)
        ]
        
        melody_b = [
            ('D4', 2), ('F4', 1), ('A4', 1), ('A#4', 2), ('A4', 1), ('G4', 1),
            ('F4', 2), ('G4', 2), ('A4', 4),
            ('REST', 2), ('C5', 1), ('A#4', 1), ('A4', 2), ('G4', 2),
            ('F4', 4), ('REST', 4),
            
            ('A#4', 1), ('A4', 1), ('G4', 1), ('F4', 1), ('G4', 2), ('A4', 2),
            ('F4', 2), ('D4', 2), ('C4', 2), ('F4', 2),
            ('G4', 1), ('F4', 1), ('E4', 1), ('F4', 1), ('F4', 4),
            ('REST', 4)
        ]
        
        return melody_a + melody_b
    
    def create_village_harmony(self):
        """Create warm harmonies - like friendly conversation."""
        harmony_a = [
            ('C4', 4), ('D4', 4),
            ('A3', 4), ('F3', 4),
            ('G3', 4), ('C4', 4),
            ('A3', 8),
            
            ('F3', 4), ('G3', 4),
            ('A3', 4), ('A#3', 4),
            ('C4', 4), ('D4', 4),
            ('C4', 8)
        ]
        
        harmony_b = [
            ('A#3', 4), ('A3', 4),
            ('G3', 4), ('F3', 4),
            ('C4', 4), ('A#3', 4),
            ('A3', 8),
            
            ('D4', 4), ('C4', 4),
            ('A#3', 4), ('A3', 4),
            ('G3', 4), ('A3', 4),
            ('F3', 8)
        ]
        
        return harmony_a + harmony_b
    
    def create_village_bass(self):
        """Create a gentle, walking bassline."""
        bass_pattern = [
            ('F2', 2), ('REST', 1), ('F2', 1), ('C3', 2), ('REST', 2),
            ('A#2', 2), ('REST', 1), ('A#2', 1), ('F2', 2), ('REST', 2),
            ('G2', 2), ('REST', 1), ('G2', 1), ('C3', 2), ('REST', 2),
            ('F2', 2), ('A2', 2), ('C3', 2), ('F2', 2),
        ]
        
        return bass_pattern * 4
    
    def create_village_accompaniment(self):
        """Create gentle arpeggiated accompaniment - like wind chimes."""
        accompaniment = []
        
        # Gentle arpeggios in F major
        arp_patterns = [
            [('F3', 0.5), ('A3', 0.5), ('C4', 0.5), ('F4', 0.5), ('C4', 0.5), ('A3', 0.5), ('F3', 0.5), ('A3', 0.5)],
            [('A#2', 0.5), ('D3', 0.5), ('F3', 0.5), ('A#3', 0.5), ('F3', 0.5), ('D3', 0.5), ('A#2', 0.5), ('D3', 0.5)],
            [('C3', 0.5), ('E3', 0.5), ('G3', 0.5), ('C4', 0.5), ('G3', 0.5), ('E3', 0.5), ('C3', 0.5), ('E3', 0.5)],
            [('F2', 0.5), ('A2', 0.5), ('C3', 0.5), ('F3', 0.5), ('C3', 0.5), ('A2', 0.5), ('F2', 0.5), ('A2', 0.5)]
        ]
        
        # Repeat pattern for full song length
        for _ in range(8):
            for pattern in arp_patterns:
                accompaniment.extend(pattern)
        
        return accompaniment
    
    def sequence_to_audio(self, sequence, wave_type='triangle', amplitude=0.3, envelope='gentle'):
        """Convert note sequence to audio with village-appropriate settings."""
        audio_data = []
        
        for note, duration_beats in sequence:
            duration_seconds = duration_beats * self.beat_duration
            frequency = self.notes.get(note, 0)
            wave_data = self.generate_wave(frequency, duration_seconds, wave_type, amplitude, envelope)
            audio_data.extend(wave_data)
        
        return audio_data
    
    def mix_tracks(self, *tracks):
        """Mix multiple tracks with village-appropriate levels."""
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
    
    def add_gentle_reverb(self, audio_data, decay=0.2, delay_samples=600):
        """Add subtle reverb for cozy indoor feeling."""
        reverb_audio = audio_data[:]
        
        for i in range(delay_samples, len(audio_data)):
            reverb_audio[i] += audio_data[i - delay_samples] * decay
        
        return reverb_audio
    
    def normalize_audio(self, audio_data, target_amplitude=0.6):
        """Normalize at lower level for peaceful village ambiance."""
        max_amplitude = max(abs(sample) for sample in audio_data)
        if max_amplitude > 0:
            scale_factor = target_amplitude / max_amplitude
            return [sample * scale_factor for sample in audio_data]
        return audio_data
    
    def save_audio(self, audio_data, filename):
        """Save village music to file."""
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
    
    def create_village_theme(self):
        """Create the complete peaceful village theme."""
        print("🏘️  Composing Peaceful Village Theme 🏘️")
        print("=" * 50)
        
        # Create all musical layers
        print("🎼 Creating gentle melody...")
        melody_sequence = self.create_village_melody()
        melody_audio = self.sequence_to_audio(melody_sequence, 'triangle', 0.4, 'gentle')
        
        print("🎼 Creating warm harmony...")
        harmony_sequence = self.create_village_harmony()
        harmony_audio = self.sequence_to_audio(harmony_sequence, 'soft_square', 0.25, 'gentle')
        
        print("🎼 Creating walking bassline...")
        bass_sequence = self.create_village_bass()
        bass_audio = self.sequence_to_audio(bass_sequence, 'warm_pulse', 0.3, 'sustain')
        
        print("🎼 Creating gentle accompaniment...")
        accompaniment_sequence = self.create_village_accompaniment()
        accompaniment_audio = self.sequence_to_audio(accompaniment_sequence, 'sine', 0.15, 'gentle')
        
        # Mix all tracks
        print("🎛️  Mixing village atmosphere...")
        mixed_audio = self.mix_tracks(melody_audio, harmony_audio, bass_audio, accompaniment_audio)
        
        # Add gentle effects
        print("✨ Adding cozy reverb...")
        mixed_audio = self.add_gentle_reverb(mixed_audio, decay=0.15, delay_samples=500)
        
        # Normalize for peaceful listening
        print("🔊 Normalizing for comfort...")
        mixed_audio = self.normalize_audio(mixed_audio, 0.55)
        
        # Save the village theme
        print("💾 Saving village theme...")
        filepath = self.save_audio(mixed_audio, "village_theme.wav")
        
        # Stats
        duration = len(mixed_audio) / self.sample_rate
        file_size = os.path.getsize(filepath)
        
        print(f"\n🏡 VILLAGE THEME COMPLETE! 🏡")
        print("=" * 50)
        print(f"📁 File: {filepath}")
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"🎵 BPM: {self.BPM} (peaceful tempo)")
        print(f"🎼 Key: F Major (warm and cozy)")
        print(f"🎨 Style: Folksy, gentle, pastoral")
        print(f"🔄 Perfect for: Village exploration, NPC conversations, rest")
        
        return filepath
    
    def create_village_loop(self):
        """Create a shorter village loop for continuous play."""
        print("\n🔄 Creating village loop version...")
        
        # Simpler, more repetitive version
        loop_melody = [
            ('F4', 2), ('G4', 1), ('A4', 1), ('A#4', 2), ('A4', 1), ('G4', 1),
            ('F4', 4), ('C4', 2), ('F4', 2),
            ('G4', 1), ('A4', 1), ('A#4', 2), ('A4', 2), ('G4', 2),
            ('F4', 6), ('REST', 2)
        ]
        
        loop_harmony = [
            ('C4', 4), ('D4', 4),
            ('A3', 4), ('F3', 4),
            ('G3', 4), ('C4', 4),
            ('F3', 8)
        ]
        
        loop_bass = [
            ('F2', 2), ('REST', 1), ('F2', 1), ('C3', 2), ('REST', 2),
            ('A#2', 2), ('REST', 1), ('A#2', 1), ('F2', 2), ('REST', 2),
        ]
        
        # Generate audio
        melody_audio = self.sequence_to_audio(loop_melody, 'triangle', 0.4, 'gentle')
        harmony_audio = self.sequence_to_audio(loop_harmony, 'soft_square', 0.25, 'gentle')
        bass_audio = self.sequence_to_audio(loop_bass, 'warm_pulse', 0.3, 'sustain')
        
        # Mix and process
        mixed_audio = self.mix_tracks(melody_audio, harmony_audio, bass_audio)
        mixed_audio = self.add_gentle_reverb(mixed_audio, decay=0.1, delay_samples=400)
        mixed_audio = self.normalize_audio(mixed_audio, 0.55)
        
        # Save loop version
        loop_filepath = self.save_audio(mixed_audio, "village_theme_loop.wav")
        
        duration = len(mixed_audio) / self.sample_rate
        print(f"🔄 Village loop created: {duration:.1f} seconds")
        
        return loop_filepath

def create_village_music():
    """Main function to create village music."""
    composer = VillageComposer()
    
    full_theme = composer.create_village_theme()
    loop_theme = composer.create_village_loop()
    
    return {
        'village_full': full_theme,
        'village_loop': loop_theme
    }

if __name__ == "__main__":
    try:
        print("🏘️  8-BIT VILLAGE MUSIC COMPOSER 🏘️")
        print("Creating peaceful, cozy village atmosphere...")
        print()
        
        music_files = create_village_music()
        
        print(f"\n✅ Village music generation complete!")
        print("🎵 Files created:")
        for name, filepath in music_files.items():
            size = os.path.getsize(filepath)
            print(f"   🏡 {name}: {os.path.basename(filepath)} ({size/1024:.1f} KB)")
        
        print("\n🏘️  Perfect for peaceful village scenes!")
        print("💡 Use loop version for continuous village ambiance")
        
    except Exception as e:
        print(f"❌ Error creating village music: {e}")
        import traceback
        traceback.print_exc()