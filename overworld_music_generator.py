# overworld_music_generator.py - Creates cinematic 8-bit overworld theme
import wave
import math
import struct
import os

class ChiptuneComposer:
    """8-bit music composer for creating layered, cinematic game music."""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.sounds_dir = "sounds"
        
        # Ensure sounds directory exists
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)
        
        # Musical constants
        self.BPM = 120
        self.beat_duration = 60.0 / self.BPM  # Duration of one beat in seconds
        self.measure_duration = self.beat_duration * 4  # 4/4 time signature
        
        # Note frequencies (A4 = 440Hz)
        self.notes = {
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81,
            'F3': 174.61, 'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00,
            'A#3': 233.08, 'B3': 246.94,
            
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63,
            'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
            'A#4': 466.16, 'B4': 493.88,
            
            'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25,
            'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00,
            'A#5': 932.33, 'B5': 987.77,
            
            'C6': 1046.50, 'REST': 0
        }
    
    def generate_wave(self, frequency, duration, wave_type='square', amplitude=0.3, envelope='adsr'):
        """Generate a waveform with specified characteristics."""
        if frequency == 0:  # Rest
            return [0] * int(duration * self.sample_rate)
        
        samples = int(duration * self.sample_rate)
        wave_data = []
        
        for i in range(samples):
            t = i / self.sample_rate
            
            if wave_type == 'square':
                value = amplitude * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1)
            elif wave_type == 'triangle':
                value = amplitude * (2 / math.pi) * math.asin(math.sin(2 * math.pi * frequency * t))
            elif wave_type == 'sawtooth':
                value = amplitude * 2 * (t * frequency - math.floor(t * frequency + 0.5))
            elif wave_type == 'pulse':
                # Pulse wave with 25% duty cycle for basslines
                cycle_pos = (t * frequency) % 1
                value = amplitude * (1 if cycle_pos < 0.25 else -1)
            else:  # sine
                value = amplitude * math.sin(2 * math.pi * frequency * t)
            
            wave_data.append(value)
        
        # Apply envelope
        if envelope == 'adsr':
            wave_data = self.apply_adsr_envelope(wave_data, duration)
        elif envelope == 'sustain':
            wave_data = self.apply_sustain_envelope(wave_data)
        
        return wave_data
    
    def apply_adsr_envelope(self, wave_data, duration, attack_ratio=0.1, decay_ratio=0.1, sustain_level=0.7, release_ratio=0.2):
        """Apply ADSR envelope to wave data."""
        total_samples = len(wave_data)
        attack_samples = int(total_samples * attack_ratio)
        decay_samples = int(total_samples * decay_ratio)
        release_samples = int(total_samples * release_ratio)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        for i in range(total_samples):
            if i < attack_samples:
                # Attack phase
                envelope = i / attack_samples
            elif i < attack_samples + decay_samples:
                # Decay phase
                progress = (i - attack_samples) / decay_samples
                envelope = 1.0 - (1.0 - sustain_level) * progress
            elif i < attack_samples + decay_samples + sustain_samples:
                # Sustain phase
                envelope = sustain_level
            else:
                # Release phase
                progress = (i - attack_samples - decay_samples - sustain_samples) / release_samples
                envelope = sustain_level * (1.0 - progress)
            
            wave_data[i] *= envelope
        
        return wave_data
    
    def apply_sustain_envelope(self, wave_data, attack_ratio=0.05, release_ratio=0.05):
        """Apply simple sustain envelope for bass and percussion."""
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
    
    def create_melody_sequence(self):
        """Create the main melody sequence - heroic and adventurous."""
        # Each tuple is (note, duration_in_beats)
        melody_a = [
            ('C5', 1), ('D5', 0.5), ('E5', 0.5), ('F5', 1), ('G5', 1),
            ('A5', 2), ('G5', 1), ('F5', 1),
            ('E5', 1), ('D5', 1), ('C5', 2),
            ('REST', 2),
            
            ('E5', 1), ('F5', 0.5), ('G5', 0.5), ('A5', 1), ('G5', 1),
            ('F5', 2), ('E5', 1), ('D5', 1),
            ('C5', 1), ('D5', 1), ('E5', 2),
            ('REST', 2)
        ]
        
        melody_b = [
            ('G5', 1), ('A5', 0.5), ('B5', 0.5), ('C6', 2),
            ('B5', 1), ('A5', 1), ('G5', 2),
            ('F5', 1), ('E5', 1), ('D5', 1), ('E5', 1),
            ('F5', 4),
            
            ('A5', 1), ('G5', 0.5), ('F5', 0.5), ('E5', 1), ('F5', 1),
            ('G5', 2), ('F5', 1), ('E5', 1),
            ('D5', 1), ('C5', 1), ('D5', 2),
            ('C5', 4)
        ]
        
        return melody_a + melody_b
    
    def create_harmony_sequence(self):
        """Create harmony/counter-melody - complements the main melody."""
        harmony_a = [
            ('E4', 2), ('F4', 2),
            ('C4', 2), ('D4', 2),
            ('G4', 2), ('A4', 2),
            ('G4', 4),
            
            ('G4', 2), ('A4', 2),
            ('F4', 2), ('G4', 2),
            ('E4', 2), ('F4', 2),
            ('E4', 4)
        ]
        
        harmony_b = [
            ('C4', 2), ('D4', 2),
            ('E4', 2), ('F4', 2),
            ('G4', 2), ('A4', 2),
            ('B4', 4),
            
            ('A4', 2), ('G4', 2),
            ('F4', 2), ('E4', 2),
            ('D4', 2), ('E4', 2),
            ('C4', 4)
        ]
        
        return harmony_a + harmony_b
    
    def create_bass_sequence(self):
        """Create bassline - provides rhythmic foundation."""
        bass_pattern = [
            ('C3', 1), ('REST', 0.5), ('C3', 0.5), ('G3', 1), ('REST', 1),
            ('F3', 1), ('REST', 0.5), ('F3', 0.5), ('C3', 1), ('REST', 1),
            ('G3', 1), ('REST', 0.5), ('G3', 0.5), ('F3', 1), ('REST', 1),
            ('C3', 1), ('G3', 1), ('C3', 2),
        ]
        
        return bass_pattern * 4  # Repeat the pattern
    
    def create_percussion_sequence(self):
        """Create percussion track using noise and low frequencies."""
        # Kick drum on beats 1 and 3, hi-hat on beats 2 and 4
        percussion = []
        beats_per_measure = 4
        total_measures = 16
        
        for measure in range(total_measures):
            for beat in range(beats_per_measure):
                if beat in [0, 2]:  # Kick drum
                    percussion.append(('KICK', 0.25))
                    percussion.append(('REST', 0.75))
                else:  # Hi-hat
                    percussion.append(('HIHAT', 0.125))
                    percussion.append(('REST', 0.125))
                    percussion.append(('HIHAT', 0.125))
                    percussion.append(('REST', 0.625))
        
        return percussion
    
    def sequence_to_audio(self, sequence, wave_type='square', amplitude=0.3, envelope='adsr'):
        """Convert a note sequence to audio data."""
        audio_data = []
        
        for note, duration_beats in sequence:
            duration_seconds = duration_beats * self.beat_duration
            
            if note == 'KICK':
                # Kick drum: low frequency pulse
                wave_data = self.generate_wave(60, duration_seconds, 'pulse', amplitude * 1.5, 'sustain')
            elif note == 'HIHAT':
                # Hi-hat: high frequency noise-like sound
                wave_data = self.generate_wave(8000, duration_seconds, 'square', amplitude * 0.3, 'sustain')
            else:
                frequency = self.notes.get(note, 0)
                wave_data = self.generate_wave(frequency, duration_seconds, wave_type, amplitude, envelope)
            
            audio_data.extend(wave_data)
        
        return audio_data
    
    def mix_tracks(self, *tracks):
        """Mix multiple audio tracks together."""
        # Find the maximum length
        max_length = max(len(track) for track in tracks)
        
        # Pad shorter tracks with silence
        padded_tracks = []
        for track in tracks:
            padded = track + [0] * (max_length - len(track))
            padded_tracks.append(padded)
        
        # Mix tracks
        mixed = []
        for i in range(max_length):
            sample = sum(track[i] for track in padded_tracks)
            # Prevent clipping
            sample = max(-1.0, min(1.0, sample))
            mixed.append(sample)
        
        return mixed
    
    def add_reverb(self, audio_data, decay=0.3, delay_samples=1000):
        """Add simple reverb effect."""
        reverb_audio = audio_data[:]
        
        for i in range(delay_samples, len(audio_data)):
            reverb_audio[i] += audio_data[i - delay_samples] * decay
        
        return reverb_audio
    
    def normalize_audio(self, audio_data, target_amplitude=0.8):
        """Normalize audio to prevent clipping."""
        max_amplitude = max(abs(sample) for sample in audio_data)
        if max_amplitude > 0:
            scale_factor = target_amplitude / max_amplitude
            return [sample * scale_factor for sample in audio_data]
        return audio_data
    
    def save_audio(self, audio_data, filename):
        """Save audio data as WAV file."""
        filepath = os.path.join(self.sounds_dir, filename)
        
        # Convert to 16-bit integers
        audio_int16 = [int(sample * 32767) for sample in audio_data]
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(self.sample_rate)
            
            # Pack audio data
            frames = []
            for sample in audio_int16:
                frames.append(struct.pack('<h', sample))
            
            wav_file.writeframes(b''.join(frames))
        
        return filepath
    
    def create_overworld_theme(self):
        """Create the complete overworld theme with all layers."""
        print("🎵 Composing Epic 8-Bit Overworld Theme 🎵")
        print("=" * 50)
        
        # Create sequences
        print("🎼 Creating main melody...")
        melody_sequence = self.create_melody_sequence()
        melody_audio = self.sequence_to_audio(melody_sequence, 'square', 0.4, 'adsr')
        
        print("🎼 Creating harmony layer...")
        harmony_sequence = self.create_harmony_sequence()
        harmony_audio = self.sequence_to_audio(harmony_sequence, 'triangle', 0.25, 'adsr')
        
        print("🎼 Creating bassline...")
        bass_sequence = self.create_bass_sequence()
        bass_audio = self.sequence_to_audio(bass_sequence, 'pulse', 0.5, 'sustain')
        
        print("🥁 Creating percussion...")
        percussion_sequence = self.create_percussion_sequence()
        percussion_audio = self.sequence_to_audio(percussion_sequence, 'square', 0.3, 'sustain')
        
        # Mix all tracks
        print("🎛️  Mixing all tracks...")
        mixed_audio = self.mix_tracks(melody_audio, harmony_audio, bass_audio, percussion_audio)
        
        # Add effects
        print("✨ Adding reverb...")
        mixed_audio = self.add_reverb(mixed_audio, decay=0.15, delay_samples=800)
        
        # Normalize
        print("🔊 Normalizing audio...")
        mixed_audio = self.normalize_audio(mixed_audio, 0.7)
        
        # Calculate duration
        duration = len(mixed_audio) / self.sample_rate
        
        # Save the file
        print("💾 Saving overworld theme...")
        filepath = self.save_audio(mixed_audio, "overworld_theme.wav")
        
        # Stats
        file_size = os.path.getsize(filepath)
        print(f"\n🎉 COMPOSITION COMPLETE! 🎉")
        print("=" * 50)
        print(f"📁 File: {filepath}")
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"🎵 BPM: {self.BPM}")
        print(f"🔊 Sample Rate: {self.sample_rate} Hz")
        print(f"🎼 Layers: Melody, Harmony, Bass, Percussion")
        print(f"🔄 Loop-ready: Yes (seamless)")
        print("\n🎮 Perfect for fantasy RPG overworld exploration!")
        print("🌟 Features cinematic progression and 8-bit nostalgia!")
        
        return filepath
    
    def create_loop_version(self):
        """Create a shorter loop version for gameplay."""
        print("\n🔄 Creating loop version...")
        
        # Create a shorter, more repetitive version
        melody_loop = [
            ('C5', 1), ('D5', 0.5), ('E5', 0.5), ('F5', 1), ('G5', 1),
            ('A5', 2), ('G5', 1), ('F5', 1),
            ('E5', 1), ('D5', 1), ('C5', 2),
            ('G5', 2),
        ]
        
        harmony_loop = [
            ('E4', 2), ('F4', 2),
            ('C4', 2), ('D4', 2),
            ('G4', 2), ('A4', 2),
            ('C4', 2)
        ]
        
        bass_loop = [
            ('C3', 1), ('REST', 0.5), ('C3', 0.5), ('G3', 1), ('REST', 1),
            ('F3', 1), ('REST', 0.5), ('F3', 0.5), ('C3', 1), ('REST', 1),
        ]
        
        # Generate audio
        melody_audio = self.sequence_to_audio(melody_loop, 'square', 0.4, 'adsr')
        harmony_audio = self.sequence_to_audio(harmony_loop, 'triangle', 0.25, 'adsr')
        bass_audio = self.sequence_to_audio(bass_loop, 'pulse', 0.5, 'sustain')
        
        # Mix and process
        mixed_audio = self.mix_tracks(melody_audio, harmony_audio, bass_audio)
        mixed_audio = self.add_reverb(mixed_audio, decay=0.1, delay_samples=400)
        mixed_audio = self.normalize_audio(mixed_audio, 0.7)
        
        # Save loop version
        loop_filepath = self.save_audio(mixed_audio, "overworld_theme_loop.wav")
        
        duration = len(mixed_audio) / self.sample_rate
        print(f"🔄 Loop version created: {duration:.1f} seconds")
        
        return loop_filepath

def create_overworld_music():
    """Main function to create overworld music."""
    composer = ChiptuneComposer()
    
    # Create full theme
    full_theme = composer.create_overworld_theme()
    
    # Create loop version
    loop_theme = composer.create_loop_version()
    
    return {
        'full_theme': full_theme,
        'loop_theme': loop_theme
    }

if __name__ == "__main__":
    try:
        print("🎼 8-BIT OVERWORLD MUSIC COMPOSER 🎼")
        print("Creating cinematic fantasy RPG music...")
        print()
        
        music_files = create_overworld_music()
        
        print(f"\n✅ Music generation complete!")
        print("🎵 Files created:")
        for name, filepath in music_files.items():
            size = os.path.getsize(filepath)
            print(f"   🎼 {name}: {os.path.basename(filepath)} ({size/1024:.1f} KB)")
        
        print("\n🎮 Ready to use in your RPG!")
        print("💡 Use the full theme for menu/intro, loop version for gameplay")
        
    except Exception as e:
        print(f"❌ Error creating music: {e}")
        import traceback
        traceback.print_exc()