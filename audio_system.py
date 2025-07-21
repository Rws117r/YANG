# audio_system.py - Comprehensive game audio system
import pygame
import os
import random

class AudioManager:
    """Manages all game audio: combat, UI, and contextual sounds."""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        self.sounds = {}
        self.enabled = True
        self.volume = 0.7
        
        # Timing controls to prevent audio spam
        self.last_sound_time = {}
        self.sound_delays = {
            'combat': 100,      # Combat sounds can repeat quickly
            'ui': 50,          # UI sounds are brief
            'contextual': 500  # Contextual sounds need longer gaps
        }
        
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
            'success': 'success.wav'
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
    
    def generate_missing_sounds(self):
        """Generate missing sound files."""
        try:
            # Import and run the comprehensive sound generator
            import subprocess
            import sys
            
            # Try to run the sound generator
            result = subprocess.run([sys.executable, 'comprehensive_sound_generator.py'], 
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
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    # Test the audio system
    pygame.init()
    test_all_sounds()
    pygame.quit()# audio_system.py - Game audio system with movement sounds
import pygame
import os
import random
from sound_generator import create_movement_sounds

class AudioManager:
    """Manages all game audio including movement sounds."""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.mixer.init()
        
        self.sounds = {}
        self.movement_sounds = {}
        self.enabled = True
        self.volume = 0.7
        
        # Movement sound timing
        self.last_movement_time = {}  # Track last sound time per archetype
        self.movement_delay = 300  # Minimum ms between movement sounds
        
        print("[AUDIO] Audio system initialized")
        self.load_movement_sounds()
    
    def load_movement_sounds(self):
        """Load or generate movement sounds for each archetype."""
        sounds_dir = "sounds"
        movement_files = {
            "Warrior": "heavy_footsteps.wav",
            "Expert": "soft_footsteps.wav", 
            "Mage": "staff_taps.wav"
        }
        
        # Check if sounds exist, generate if needed
        missing_sounds = []
        for archetype, filename in movement_files.items():
            filepath = os.path.join(sounds_dir, filename)
            if not os.path.exists(filepath):
                missing_sounds.append(archetype)
        
        if missing_sounds:
            print(f"[AUDIO] Generating missing movement sounds: {missing_sounds}")
            create_movement_sounds()
        
        # Load all movement sounds
        for archetype, filename in movement_files.items():
            filepath = os.path.join(sounds_dir, filename)
            try:
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.volume)
                self.movement_sounds[archetype] = sound
                self.last_movement_time[archetype] = 0
                print(f"[AUDIO] Loaded {archetype} movement sound: {filename}")
            except pygame.error as e:
                print(f"[AUDIO ERROR] Could not load {filepath}: {e}")
                self.movement_sounds[archetype] = None
    
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
            # Add slight pitch variation for variety
            # Note: pygame doesn't support pitch shifting easily, so we'll just play as-is
            sound.play()
            self.last_movement_time[archetype] = current_time
            print(f"[AUDIO] Playing {archetype} movement sound")
    
    def play_sound(self, sound_name, volume=None):
        """Play a general game sound."""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        sound = self.sounds[sound_name]
        if volume is not None:
            sound.set_volume(volume * self.volume)
        sound.play()
    
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        
        # Update all loaded sounds
        for sound in self.movement_sounds.values():
            if sound:
                sound.set_volume(self.volume)
        
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
    
    def toggle_audio(self):
        """Toggle audio on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            pygame.mixer.stop()  # Stop all sounds
        return self.enabled
    
    def load_additional_sound(self, sound_name, filepath):
        """Load an additional sound effect."""
        try:
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(self.volume)
            self.sounds[sound_name] = sound
            print(f"[AUDIO] Loaded {sound_name}: {filepath}")
        except pygame.error as e:
            print(f"[AUDIO ERROR] Could not load {filepath}: {e}")
    
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
    """Initialize the game audio system."""
    try:
        audio_manager = AudioManager()
        return audio_manager
    except Exception as e:
        print(f"[AUDIO ERROR] Failed to initialize audio: {e}")
        return None

def test_movement_sounds():
    """Test function to play all movement sounds."""
    print("=== TESTING MOVEMENT SOUNDS ===")
    
    audio_manager = AudioManager()
    
    archetypes = ["Warrior", "Expert", "Mage"]
    for i, archetype in enumerate(archetypes):
        print(f"Playing {archetype} movement sound...")
        audio_manager.play_movement_sound(archetype, force=True)
        
        # Wait a bit between sounds
        pygame.time.wait(1000)
    
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    # Test the audio system
    pygame.init()
    test_movement_sounds()
    pygame.quit()