# comprehensive_sound_generator.py - Combat, UI, and contextual audio
import numpy as np
import wave
import os
import struct

def create_game_audio():
    """Create all game audio: combat, UI, and contextual sounds."""
    
    print("🎵 Creating Comprehensive Game Audio 🎵")
    print("=" * 45)
    
    # Setup
    sample_rate = 22050
    sounds_dir = "sounds"
    
    # Create directory
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        print(f"📁 Created '{sounds_dir}' directory")
    
    def make_tone(freq, duration, volume=0.3, wave_type='square'):
        """Create different types of waveforms."""
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        if wave_type == 'square':
            wave = volume * np.sign(np.sin(2 * np.pi * freq * t))
        elif wave_type == 'sine':
            wave = volume * np.sin(2 * np.pi * freq * t)
        elif wave_type == 'sawtooth':
            wave = volume * 2 * (t * freq - np.floor(t * freq + 0.5))
        elif wave_type == 'noise':
            wave = volume * (2 * np.random.random(samples) - 1)
        else:
            wave = volume * np.sin(2 * np.pi * freq * t)
        
        # Fade out to prevent clicks
        fade_samples = min(500, samples // 10)
        if fade_samples > 0:
            wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        return wave
    
    def apply_envelope(wave, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        """Apply ADSR envelope."""
        samples = len(wave)
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)
        sustain_samples = max(0, samples - attack_samples - decay_samples - release_samples)
        
        envelope = np.ones(samples)
        
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
            start = samples - release_samples
            envelope[start:] = np.linspace(sustain, 0, release_samples)
        
        return wave * envelope
    
    def save_sound(wave_data, filename):
        """Save sound data to WAV file."""
        # Normalize
        if np.max(np.abs(wave_data)) > 0:
            wave_data = wave_data / np.max(np.abs(wave_data)) * 0.8
        
        # Convert to 16-bit integers
        wave_int16 = np.array(wave_data * 32767, dtype=np.int16)
        
        filepath = os.path.join(sounds_dir, filename)
        with wave.open(filepath, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            f.writeframes(wave_int16.tobytes())
        
        return filepath
    
    sounds_created = {}
    
    # ============================================
    # COMBAT SOUNDS (Option 1)
    # ============================================
    print("\n⚔️  Creating Combat Audio...")
    
    # WARRIOR ATTACK - Deep thunk + metal ring
    print("   🛡️  Warrior attack sound...")
    whoosh = make_tone(150, 0.15, 0.4, 'sawtooth')
    thunk = make_tone(80, 0.12, 0.6, 'square')
    ring = make_tone(1200, 0.2, 0.3, 'sine')
    ring = apply_envelope(ring, 0.001, 0.05, 0.4, 0.15)
    
    max_len = max(len(whoosh), len(thunk), len(ring))
    warrior_attack = np.zeros(max_len)
    warrior_attack[:len(whoosh)] += whoosh
    warrior_attack[:len(thunk)] += thunk  
    warrior_attack[:len(ring)] += ring
    
    sounds_created['warrior_attack'] = save_sound(warrior_attack, "warrior_attack.wav")
    
    # EXPERT ATTACK - Quick swish + precise hit
    print("   🗡️  Expert attack sound...")
    swish = make_tone(400, 0.08, 0.5, 'sawtooth')
    swish = apply_envelope(swish, 0.001, 0.02, 0.3, 0.05)
    hit = make_tone(800, 0.06, 0.4, 'square')
    hit = apply_envelope(hit, 0.001, 0.01, 0.2, 0.04)
    
    max_len = max(len(swish), len(hit))
    expert_attack = np.zeros(max_len)
    expert_attack[:len(swish)] += swish
    expert_attack[:len(hit)] += hit
    
    sounds_created['expert_attack'] = save_sound(expert_attack, "expert_attack.wav")
    
    # MAGE SPELL - Magical whoosh + crystalline impact
    print("   🔮 Mage spell sound...")
    magical_whoosh = make_tone(600, 0.2, 0.4, 'sine')
    magical_whoosh = apply_envelope(magical_whoosh, 0.02, 0.05, 0.6, 0.13)
    crystal_impact = make_tone(1600, 0.15, 0.3, 'sine')
    crystal_impact = apply_envelope(crystal_impact, 0.001, 0.03, 0.5, 0.12)
    shimmer = make_tone(3200, 0.1, 0.2, 'sine')
    shimmer = apply_envelope(shimmer, 0.01, 0.02, 0.3, 0.07)
    
    max_len = max(len(magical_whoosh), len(crystal_impact), len(shimmer))
    mage_spell = np.zeros(max_len)
    mage_spell[:len(magical_whoosh)] += magical_whoosh
    mage_spell[:len(crystal_impact)] += crystal_impact
    mage_spell[:len(shimmer)] += shimmer
    
    sounds_created['mage_spell'] = save_sound(mage_spell, "mage_spell.wav")
    
    # ============================================
    # CONTEXTUAL MOVEMENT SOUNDS (Option 3)
    # ============================================
    print("\n🚶 Creating Contextual Movement Audio...")
    
    # AREA TRANSITION - Mystical portal sound
    print("   🌟 Area transition sound...")
    portal_low = make_tone(200, 0.8, 0.3, 'sine')
    portal_low = apply_envelope(portal_low, 0.1, 0.2, 0.6, 0.5)
    portal_high = make_tone(800, 0.6, 0.2, 'sine')
    portal_high = apply_envelope(portal_high, 0.2, 0.1, 0.4, 0.3)
    
    max_len = max(len(portal_low), len(portal_high))
    transition = np.zeros(max_len)
    transition[:len(portal_low)] += portal_low
    transition[:len(portal_high)] += portal_high
    
    sounds_created['area_transition'] = save_sound(transition, "area_transition.wav")
    
    # WATER SPLASH - For walking on water
    print("   💧 Water splash sound...")
    splash = make_tone(300, 0.2, 0.4, 'noise')
    splash = apply_envelope(splash, 0.001, 0.05, 0.3, 0.14)
    water_tone = make_tone(150, 0.15, 0.2, 'sine')
    water_tone = apply_envelope(water_tone, 0.01, 0.03, 0.4, 0.11)
    
    max_len = max(len(splash), len(water_tone))
    water_splash = np.zeros(max_len)
    water_splash[:len(splash)] += splash
    water_splash[:len(water_tone)] += water_tone
    
    sounds_created['water_splash'] = save_sound(water_splash, "water_splash.wav")
    
    # ============================================
    # UI SOUNDS (Option 4)
    # ============================================
    print("\n🖱️  Creating UI Audio...")
    
    # PANEL SWITCH - Soft beep
    print("   📋 Panel switch sound...")
    beep = make_tone(800, 0.1, 0.3, 'sine')
    beep = apply_envelope(beep, 0.01, 0.02, 0.5, 0.07)
    sounds_created['panel_switch'] = save_sound(beep, "panel_switch.wav")
    
    # ITEM PICKUP - Pleasant chime
    print("   💎 Item pickup sound...")
    chime1 = make_tone(600, 0.15, 0.3, 'sine')
    chime2 = make_tone(900, 0.12, 0.2, 'sine')
    chime_combined = np.zeros(max(len(chime1), len(chime2)))
    chime_combined[:len(chime1)] += chime1
    chime_combined[:len(chime2)] += chime2
    chime_combined = apply_envelope(chime_combined, 0.01, 0.03, 0.6, 0.11)
    sounds_created['item_pickup'] = save_sound(chime_combined, "item_pickup.wav")
    
    # LEVEL UP - Triumphant fanfare
    print("   🎊 Level up sound...")
    note1 = make_tone(400, 0.2, 0.4, 'sine')
    note2 = make_tone(600, 0.2, 0.3, 'sine') 
    note3 = make_tone(800, 0.3, 0.4, 'sine')
    
    # Sequence the notes
    fanfare = np.concatenate([note1, note2, note3])
    fanfare = apply_envelope(fanfare, 0.01, 0.1, 0.8, 0.3)
    sounds_created['level_up'] = save_sound(fanfare, "level_up.wav")
    
    # SPELL PREPARE - Magical preparation
    print("   ✨ Spell prepare sound...")
    prep_tone = make_tone(1000, 0.3, 0.3, 'sine')
    prep_tone = apply_envelope(prep_tone, 0.05, 0.1, 0.7, 0.15)
    # Add some sparkle
    sparkle = make_tone(2000, 0.2, 0.15, 'sine')
    sparkle = apply_envelope(sparkle, 0.1, 0.05, 0.3, 0.05)
    
    max_len = max(len(prep_tone), len(sparkle))
    spell_prep = np.zeros(max_len)
    spell_prep[:len(prep_tone)] += prep_tone
    spell_prep[:len(sparkle)] += sparkle
    
    sounds_created['spell_prepare'] = save_sound(spell_prep, "spell_prepare.wav")
    
    # ERROR/INVALID ACTION - Negative feedback
    print("   ❌ Error sound...")
    error = make_tone(200, 0.15, 0.4, 'square')
    error = apply_envelope(error, 0.001, 0.05, 0.3, 0.09)
    sounds_created['error'] = save_sound(error, "error.wav")
    
    # SUCCESS/CONFIRMATION - Positive feedback  
    print("   ✅ Success sound...")
    success = make_tone(1200, 0.12, 0.3, 'sine')
    success = apply_envelope(success, 0.01, 0.02, 0.6, 0.09)
    sounds_created['success'] = save_sound(success, "success.wav")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n🎉 AUDIO CREATION COMPLETE!")
    print("=" * 45)
    print("📂 Created comprehensive game audio:")
    
    print("\n⚔️  COMBAT SOUNDS:")
    print(f"   🛡️  warrior_attack.wav ({os.path.getsize(sounds_created['warrior_attack'])} bytes)")
    print(f"   🗡️  expert_attack.wav ({os.path.getsize(sounds_created['expert_attack'])} bytes)")
    print(f"   🔮 mage_spell.wav ({os.path.getsize(sounds_created['mage_spell'])} bytes)")
    
    print("\n🚶 CONTEXTUAL MOVEMENT:")
    print(f"   🌟 area_transition.wav ({os.path.getsize(sounds_created['area_transition'])} bytes)")
    print(f"   💧 water_splash.wav ({os.path.getsize(sounds_created['water_splash'])} bytes)")
    
    print("\n🖱️  UI FEEDBACK:")
    print(f"   📋 panel_switch.wav ({os.path.getsize(sounds_created['panel_switch'])} bytes)")
    print(f"   💎 item_pickup.wav ({os.path.getsize(sounds_created['item_pickup'])} bytes)")
    print(f"   🎊 level_up.wav ({os.path.getsize(sounds_created['level_up'])} bytes)")
    print(f"   ✨ spell_prepare.wav ({os.path.getsize(sounds_created['spell_prepare'])} bytes)")
    print(f"   ❌ error.wav ({os.path.getsize(sounds_created['error'])} bytes)")
    print(f"   ✅ success.wav ({os.path.getsize(sounds_created['success'])} bytes)")
    
    print(f"\n🎵 Total: {len(sounds_created)} original 8-bit style sounds!")
    print("🎮 Ready for integration!")
    
    return sounds_created

if __name__ == "__main__":
    try:
        sounds = create_game_audio()
        print(f"\n✅ Generated {len(sounds)} sounds successfully!")
        
        # Verify all files
        all_good = True
        for sound_name, filepath in sounds.items():
            if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
                print(f"   ✅ {sound_name}: OK")
            else:
                print(f"   ❌ {sound_name}: Failed")
                all_good = False
        
        if all_good:
            print("\n🎊 All sounds ready for your game!")
        else:
            print("\n⚠️  Some sounds may have issues")
            
    except ImportError:
        print("❌ Error: This script requires numpy")
        print("💡 Install with: pip install numpy")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("💡 Try running as administrator or check file permissions")