# music_integration.py - Integration code for adding music to your game
import pygame
import os

class MusicManager:
    """Manages background music for the game."""
    
    def __init__(self):
        self.current_music = None
        self.music_volume = 0.5
        self.music_enabled = True
        self.music_files = {
            'overworld': 'overworld_theme_loop.wav',
            'overworld_full': 'overworld_theme.wav',
            'menu': 'overworld_theme.wav'  # Use full theme for menus
        }
        
        # Initialize pygame mixer for music
        pygame.mixer.init()
        
        print("[MUSIC] Music manager initialized")
    
    def play_music(self, track_name, loops=-1, fade_ms=1000):
        """Play background music."""
        if not self.music_enabled:
            return
        
        if track_name not in self.music_files:
            print(f"[MUSIC] Unknown track: {track_name}")
            return
        
        music_file = os.path.join("sounds", self.music_files[track_name])
        
        if not os.path.exists(music_file):
            print(f"[MUSIC] Music file not found: {music_file}")
            return
        
        # Don't restart if already playing the same track
        if self.current_music == track_name and pygame.mixer.music.get_busy():
            return
        
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self.current_music = track_name
            print(f"[MUSIC] Playing: {track_name}")
        except pygame.error as e:
            print(f"[MUSIC ERROR] Could not play {music_file}: {e}")
    
    def stop_music(self, fade_ms=1000):
        """Stop background music."""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None
        print("[MUSIC] Music stopped")
    
    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()
        print("[MUSIC] Music paused")
    
    def unpause_music(self):
        """Resume background music."""
        pygame.mixer.music.unpause()
        print("[MUSIC] Music resumed")
    
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"[MUSIC] Volume set to {self.music_volume}")
    
    def toggle_music(self):
        """Toggle music on/off."""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        print(f"[MUSIC] Music {'enabled' if self.music_enabled else 'disabled'}")
        return self.music_enabled
    
    def is_playing(self):
        """Check if music is currently playing."""
        return pygame.mixer.music.get_busy()

# Integration functions for your existing engine.py

def add_music_to_engine(game_engine):
    """Add music manager to existing game engine."""
    game_engine.music_manager = MusicManager()
    
    # Generate music if it doesn't exist
    overworld_file = os.path.join("sounds", "overworld_theme_loop.wav")
    if not os.path.exists(overworld_file):
        print("[MUSIC] Generating overworld music...")
        try:
            from overworld_music_generator import create_overworld_music
            create_overworld_music()
        except ImportError:
            print("[MUSIC] Music generator not found. Please run overworld_music_generator.py first.")
        except Exception as e:
            print(f"[MUSIC] Failed to generate music: {e}")
    
    return game_engine.music_manager

def update_engine_with_music():
    """Shows how to integrate music into your existing engine.py"""
    
    integration_code = '''
# Add this to your Game class __init__ method in engine.py:

# --- Add after audio_manager initialization ---
# Music System
self.music_manager = MusicManager()
if self.music_manager:
    print("[DEBUG] Music system initialized successfully")
    # Start overworld music
    self.music_manager.play_music('overworld')
else:
    print("[DEBUG] Music system failed to initialize")

# Add these methods to your Game class:

def change_music(self, track_name, fade_ms=1000):
    """Change background music."""
    if self.music_manager:
        self.music_manager.play_music(track_name, fade_ms=fade_ms)

def pause_music(self):
    """Pause background music."""
    if self.music_manager:
        self.music_manager.pause_music()

def unpause_music(self):
    """Resume background music."""
    if self.music_manager:
        self.music_manager.unpause_music()

# Add this to your change_map method:
def change_map(self, place):
    """Switch to a new map with appropriate music."""
    # ... existing code ...
    
    # Change music based on location
    if place.name == "Saltwind Village":
        self.change_music('overworld', fade_ms=2000)
    elif "Crypt" in place.name or "Dungeon" in place.name:
        # You could add dungeon music here later
        self.music_manager.set_volume(0.3)  # Lower volume for dungeons
    else:
        self.change_music('overworld')

# Add this to your pause menu handling in input_handler.py:
def _handle_pause_menu_input(self, key):
    """Handle pause menu input with music pausing."""
    # ... existing code ...
    
    if selected_option == "Resume":
        self.game.game_state = 'playing'
        self.game.unpause_music()  # Resume music
    # ... rest of existing code ...

# And in the pause activation:
if key == pygame.K_ESCAPE:
    self.game.game_state = 'pause_menu'
    self.game.pause_music()  # Pause music
    self.game.pause_menu_selected_index = 0
'''
    
    return integration_code

# Example usage script
def setup_music_for_game():
    """Complete setup script for adding music to your game."""
    print("🎵 Setting up music for your RPG...")
    
    # Step 1: Generate music if needed
    sounds_dir = "sounds"
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
    
    overworld_file = os.path.join(sounds_dir, "overworld_theme_loop.wav")
    if not os.path.exists(overworld_file):
        print("🎼 Generating overworld music...")
        try:
            from overworld_music_generator import create_overworld_music
            create_overworld_music()
            print("✅ Music generation complete!")
        except Exception as e:
            print(f"❌ Music generation failed: {e}")
            return False
    else:
        print("✅ Music files already exist")
    
    # Step 2: Test music system
    print("🔊 Testing music system...")
    try:
        pygame.init()
        music_manager = MusicManager()
        music_manager.play_music('overworld')
        print("✅ Music system working!")
        
        # Let it play for a few seconds
        import time
        print("🎵 Playing sample (3 seconds)...")
        time.sleep(3)
        music_manager.stop_music()
        pygame.quit()
        
    except Exception as e:
        print(f"❌ Music system test failed: {e}")
        return False
    
    # Step 3: Show integration instructions
    print("\n📝 INTEGRATION INSTRUCTIONS:")
    print("=" * 50)
    print("1. Add the MusicManager class to your project")
    print("2. Import and initialize it in your engine.py")
    print("3. Add music control methods to your Game class")
    print("4. Call appropriate music changes in your game logic")
    print("\nSee the integration code above for specific examples!")
    
    return True

if __name__ == "__main__":
    setup_music_for_game()