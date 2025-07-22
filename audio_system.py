# audio_system.py - Fixed comprehensive game audio system with spell preparation
import pygame
import os
import random

class AudioManager:
    """Manages all game audio: combat, UI, contextual sounds, and spell preparation."""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        self.sounds = {}
        self.movement_sounds = {}
        self.enabled = True
        self.volume = 0.7
        
        # Timing controls to prevent audio spam
        self.last_sound_time = {}
        self.last_movement_time = {}  # Track last sound time per archetype
        self.sound_delays = {
            'combat': 100,      # Combat sounds can repeat quickly
            'ui': 50,          # UI sounds are brief
            'contextual': 500  # Contextual sounds need longer gaps
        }
        self.movement_delay = 300  # Minimum ms between movement sounds
        
        print("[AUDIO] Audio system initialized")
        self.load_all_sounds()
    
    def load_all_sounds(self):
        """Load or generate all game sounds."""
        sounds_dir = "sounds"
        
        # Define all expected sound files
        sound_files = {
            # Combat sounds
            'warrior_attack': 'warrior_attack.wav',
            'expert_attack': 'expert_attack.wav', 
            'mage_spell': 'mage_spell.wav',
            
            # Contextual movement
            'area_transition': 'area_transition.wav',
            'water_splash': 'water_splash.wav',
            
            # UI sounds
            'panel_switch': 'panel_switch.wav',
            'item_pickup': 'item_pickup.wav',
            'level_up': 'level_up.wav',
            'spell_prepare': 'spell_prepare.wav',
            'error': 'error.wav',
            'success': 'success.wav',
            
            # Movement sounds
            'heavy_footsteps': 'heavy_footsteps.wav',
            'soft_footsteps': 'soft_footsteps.wav',
            'staff_taps': 'staff_taps.wav'
        }
        
        # Check if sounds exist, generate if needed
        missing_sounds = []
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            if not os.path.exists(filepath):
                missing_sounds.append(sound_name)
        
        if missing_sounds:
            print(f"[AUDIO] Generating missing sounds: {missing_sounds}")
            self.generate_missing_sounds()
        
        # Load all sounds
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            try:
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.volume)
                self.sounds[sound_name] = sound
                self.last_sound_time[sound_name] = 0
                print(f"[AUDIO] Loaded {sound_name}: {filename}")
            except pygame.error as e:
                print(f"[AUDIO ERROR] Could not load {filepath}: {e}")
                self.sounds[sound_name] = None
        
        # Set up movement sounds mapping
        self.movement_sounds = {
            "Warrior": self.sounds.get('heavy_footsteps'),
            "Expert": self.sounds.get('soft_footsteps'),
            "Mage": self.sounds.get('staff_taps')
        }
        
        # Initialize movement timing
        for archetype in self.movement_sounds:
            self.last_movement_time[archetype] = 0
        
        # Load spell preparation sounds
        self.load_spell_preparation_sounds()
    
    def load_spell_preparation_sounds(self):
        """Load spell preparation sound effects."""
        prep_sounds = {
            'novice_prep': 'novice_prep.wav',    # Levels 1-2
            'adept_prep': 'adept_prep.wav',      # Levels 3-4  
            'expert_prep': 'expert_prep.wav',    # Levels 5-6
            'master_prep': 'master_prep.wav',    # Levels 7+
            
            # Glyph progression sounds
            'glyph_dot': 'glyph_dot.wav',
            'glyph_target': 'glyph_target.wav',
            'glyph_circle': 'glyph_circle.wav',
            'glyph_empty_star': 'glyph_empty_star.wav',
            'glyph_filled_star': 'glyph_filled_star.wav'
        }
        
        for sound_name, filename in prep_sounds.items():
            filepath = os.path.join("sounds", filename)
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    self.last_sound_time[sound_name] = 0
                    print(f"[AUDIO] Loaded spell prep sound: {sound_name}")
                else:
                    print(f"[AUDIO] Missing spell prep sound: {filepath}")
                    self.sounds[sound_name] = None
            except pygame.error as e:
                print(f"[AUDIO ERROR] Could not load {filepath}: {e}")
                self.sounds[sound_name] = None
    
    def play_spell_preparation_sound(self, player_level):
        """Play appropriate spell preparation sound based on player level."""
        if player_level <= 2:
            sound_name = 'novice_prep'
        elif player_level <= 4:
            sound_name = 'adept_prep'
        elif player_level <= 6:
            sound_name = 'expert_prep'
        else:
            sound_name = 'master_prep'
        
        self.play_sound(sound_name, 'contextual', force=True)
    
    def play_glyph_progression_sound(self, glyph_type):
        """Play sound for glyph progression during spell preparation."""
        glyph_sound_map = {
            '\uf444': 'glyph_dot',        # Dot (0xf444)
            '\uf192': 'glyph_target',     # Target (0xf192)  
            'O': 'glyph_circle',          # Circle
            '\uea6a': 'glyph_empty_star', # Empty star (0xea6a)
            '\uf04ce': 'glyph_filled_star' # Filled star (0xf04ce)
        }
        
        sound_name = glyph_sound_map.get(glyph_type)
        if sound_name:
            self.play_sound(sound_name, 'ui', volume=0.3)  # Quieter than main prep sound
    
    def generate_missing_sounds(self):
        """Generate missing sound files."""
        try:
            # Import and run the comprehensive sound generator
            import subprocess
            import sys
            
            # Try to run the sound generator
            result = subprocess.run([sys.executable, 'simple_sound_generator.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("[AUDIO] Successfully generated missing sounds")
            else:
                print(f"[AUDIO ERROR] Sound generation failed: {result.stderr}")
        except Exception as e:
            print(f"[AUDIO ERROR] Could not generate sounds: {e}")
    
    def can_play_sound(self, sound_name, sound_category='ui'):
        """Check if enough time has passed to play a sound."""
        if not self.enabled:
            return False
        
        current_time = pygame.time.get_ticks()
        last_time = self.last_sound_time.get(sound_name, 0)
        delay = self.sound_delays.get(sound_category, 100)
        
        return current_time - last_time >= delay
    
    def play_sound(self, sound_name, sound_category='ui', volume=None, force=False):
        """Play a game sound with timing control."""
        if not force and not self.can_play_sound(sound_name, sound_category):
            return
        
        if sound_name not in self.sounds or not self.sounds[sound_name]:
            return
        
        sound = self.sounds[sound_name]
        if volume is not None:
            sound.set_volume(volume * self.volume)
        
        sound.play()
        self.last_sound_time[sound_name] = pygame.time.get_ticks()
        print(f"[AUDIO] Playing {sound_name}")
    
    # ============================================
    # COMBAT AUDIO METHODS
    # ============================================
    
    def play_attack_sound(self, archetype):
        """Play attack sound based on archetype."""
        sound_map = {
            'Warrior': 'warrior_attack',
            'Expert': 'expert_attack',
            'Mage': 'mage_spell'
        }
        
        sound_name = sound_map.get(archetype)
        if sound_name:
            self.play_sound(sound_name, 'combat')
    
    def play_spell_sound(self, spell_name=None):
        """Play spell casting sound."""
        # For now, all spells use the mage_spell sound
        # Later could be customized per spell
        self.play_sound('mage_spell', 'combat')
    
    def play_hit_sound(self, archetype, is_critical=False):
        """Play hit confirmation sound."""
        # Use the attack sound as hit confirmation for now
        self.play_attack_sound(archetype)
    
    # ============================================
    # MOVEMENT AUDIO METHODS
    # ============================================
    
    def play_movement_sound(self, archetype, force=False):
        """Play movement sound for the specified archetype."""
        if not self.enabled or archetype not in self.movement_sounds:
            return
        
        current_time = pygame.time.get_ticks()
        last_time = self.last_movement_time.get(archetype, 0)
        
        # Check timing to prevent sound spam
        if not force and current_time - last_time < self.movement_delay:
            return
        
        sound = self.movement_sounds.get(archetype)
        if sound:
            sound.play()
            self.last_movement_time[archetype] = current_time
            print(f"[AUDIO] Playing {archetype} movement sound")
    
    # ============================================
    # CONTEXTUAL MOVEMENT AUDIO METHODS
    # ============================================
    
    def play_area_transition(self):
        """Play sound when transitioning between areas."""
        self.play_sound('area_transition', 'contextual')
    
    def play_water_splash(self):
        """Play sound when walking on water tiles."""
        self.play_sound('water_splash', 'contextual')
    
    def play_contextual_movement(self, terrain_type):
        """Play contextual movement sound based on terrain."""
        if terrain_type == 'water':
            self.play_water_splash()
        # Add more terrain types as needed
    
    # ============================================
    # UI AUDIO METHODS
    # ============================================
    
    def play_panel_switch(self):
        """Play sound when switching UI panels."""
        self.play_sound('panel_switch', 'ui')
    
    def play_item_pickup(self):
        """Play sound when picking up items."""
        self.play_sound('item_pickup', 'ui')
    
    def play_level_up(self):
        """Play triumphant level up sound."""
        self.play_sound('level_up', 'ui', force=True)  # Always play level up
    
    def play_spell_prepare(self):
        """Play sound when preparing spells."""
        self.play_sound('spell_prepare', 'ui')
    
    def play_error(self):
        """Play error/invalid action sound."""
        self.play_sound('error', 'ui')
    
    def play_success(self):
        """Play success/confirmation sound."""
        self.play_sound('success', 'ui')
    
    # ============================================
    # UTILITY METHODS
    # ============================================
    
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        
        # Update all loaded sounds
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
    
    def toggle_audio(self):
        """Toggle audio on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            pygame.mixer.stop()  # Stop all sounds
        return self.enabled
    
    def get_audio_info(self):
        """Get info about loaded sounds for debugging."""
        info = {
            'enabled': self.enabled,
            'volume': self.volume,
            'loaded_sounds': len([s for s in self.sounds.values() if s is not None]),
            'total_sounds': len(self.sounds)
        }
        return info
    
    def get_movement_sound_info(self):
        """Get info about loaded movement sounds for debugging."""
        info = {}
        for archetype, sound in self.movement_sounds.items():
            info[archetype] = {
                "loaded": sound is not None,
                "last_played": self.last_movement_time.get(archetype, 0)
            }
        return info

class MovementAudioMixin:
    """Mixin to add movement audio to game entities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_manager = None  # Will be set by the game engine
    
    def play_movement_audio(self):
        """Play movement sound based on archetype."""
        if hasattr(self, 'archetype') and self.audio_manager:
            self.audio_manager.play_movement_sound(self.archetype)
    
    def set_audio_manager(self, audio_manager):
        """Set the audio manager reference."""
        self.audio_manager = audio_manager

# Integration functions for the main game
def initialize_game_audio():
    """Initialize the comprehensive game audio system."""
    try:
        audio_manager = AudioManager()
        return audio_manager
    except Exception as e:
        print(f"[AUDIO ERROR] Failed to initialize audio: {e}")
        return None

def test_all_sounds():
    """Test function to play all game sounds."""
    print("=== TESTING ALL GAME SOUNDS ===")
    
    audio_manager = AudioManager()
    
    # Test combat sounds
    print("\n⚔️  Testing Combat Sounds...")
    for archetype in ['Warrior', 'Expert', 'Mage']:
        print(f"   Playing {archetype} attack...")
        audio_manager.play_attack_sound(archetype)
        pygame.time.wait(800)
    
    # Test contextual sounds
    print("\n🚶 Testing Contextual Sounds...")
    print("   Playing area transition...")
    audio_manager.play_area_transition()
    pygame.time.wait(1000)
    
    print("   Playing water splash...")
    audio_manager.play_water_splash()
    pygame.time.wait(500)
    
    # Test UI sounds
    print("\n🖱️  Testing UI Sounds...")
    ui_tests = [
        ('panel_switch', 'Panel Switch'),
        ('item_pickup', 'Item Pickup'),
        ('spell_prepare', 'Spell Prepare'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('level_up', 'Level Up')
    ]
    
    for sound_key, description in ui_tests:
        print(f"   Playing {description}...")
        getattr(audio_manager, f'play_{sound_key}')()
        pygame.time.wait(600)
    
    # Test movement sounds
    print("\n🚶 Testing Movement Sounds...")
    for archetype in ['Warrior', 'Expert', 'Mage']:
        print(f"   Playing {archetype} movement...")
        audio_manager.play_movement_sound(archetype, force=True)
        pygame.time.wait(800)
    
    # Test spell preparation sounds
    print("\n🔮 Testing Spell Preparation Sounds...")
    for level in [1, 3, 5, 8]:
        print(f"   Playing level {level} preparation...")
        audio_manager.play_spell_preparation_sound(level)
        pygame.time.wait(1500)
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    # Test the audio system
    pygame.init()
    test_all_sounds()
    pygame.quit()