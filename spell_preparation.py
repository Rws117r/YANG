# spell_preparation.py - Magical spell preparation animation system
import pygame
import math
from config import *

class SpellPreparationAnimator:
    """Manages the magical spell preparation animation with ring effects."""
    
    def __init__(self, vfx_manager):
        self.vfx_manager = vfx_manager
        self.is_active = False
        self.start_time = 0
        self.duration = 1200  # 1.2 seconds total animation
        self.current_position = 0  # Current position in the ring (0-11)
        self.glyph_progress = {}  # Track each position's glyph progression
        
        # Ring positions relative to player (2 tiles away)
        self.ring_positions = [
            (0, -2),   # 12 o'clock
            (1, -2),   # 1 o'clock
            (2, -1),   # 2 o'clock  
            (2, 0),    # 3 o'clock
            (2, 1),    # 4 o'clock
            (1, 2),    # 5 o'clock
            (0, 2),    # 6 o'clock
            (-1, 2),   # 7 o'clock
            (-2, 1),   # 8 o'clock
            (-2, 0),   # 9 o'clock
            (-2, -1),  # 10 o'clock
            (-1, -2)   # 11 o'clock
        ]
        
        # Glyph progression sequence - using simpler, more reliable characters
        self.glyph_sequence = [
            '·',       # Small dot (U+00B7)
            '-',       # Target/bullseye (U+2299) 
            '~',       # Circle
            '*',       # Empty star (U+2606)
            'O'        # Filled star (U+2605)
        ]
        
        # Color progression based on player level (smooth transitions)
        self.level_colors = {
            1: pygame.Color(100, 150, 255),   # Bright blue
            2: pygame.Color(120, 130, 255),   # Blue-purple
            3: pygame.Color(140, 110, 255),   # Purple
            4: pygame.Color(160, 90, 255),    # Deep purple
            5: pygame.Color(180, 70, 230),    # Purple-red
            6: pygame.Color(200, 50, 200),    # Magenta
            7: pygame.Color(220, 30, 170),    # Red-purple
            8: pygame.Color(240, 20, 140),    # Red
            9: pygame.Color(255, 30, 100),    # Bright red
            10: pygame.Color(255, 50, 50),    # Pure red
            11: pygame.Color(255, 200, 0)     # Gold
        }
    
    def get_level_color(self, player_level):
        """Get smooth color transition based on player level."""
        # Clamp level to our range
        level = max(1, min(11, player_level))
        
        if level in self.level_colors:
            return self.level_colors[level]
        
        # For levels beyond 11, stay gold
        if level > 11:
            return self.level_colors[11]
        
        # This shouldn't happen, but fallback to blue
        return self.level_colors[1]
    
    def start_preparation(self, player_level):
        """Start the spell preparation animation."""
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        self.current_position = 0
        self.glyph_progress = {}
        self.player_level = player_level
        
        # Start screen darkening effect
        self.vfx_manager.start_screen_darkening(self.duration)
        
        print(f"[SPELL PREP] Starting preparation animation for level {player_level}")
    
    def update(self):
        """Update the preparation animation."""
        if not self.is_active:
            return False
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            self.is_active = False
            self.vfx_manager.end_screen_darkening()
            print("[SPELL PREP] Animation complete")
            return False
        
        # Calculate animation progress (0.0 to 1.0)
        progress = elapsed / self.duration
        
        # Determine how many positions should be animated
        total_positions = len(self.ring_positions)
        
        # Animation flows around the ring clockwise
        ring_progress = progress * total_positions
        
        # Update each position's glyph progression
        active_positions = 0
        for pos_index in range(total_positions):
            # Check if this position should be active yet
            if ring_progress >= pos_index:
                # Calculate how long this position has been active
                position_start_progress = pos_index / total_positions
                position_elapsed_progress = max(0, progress - position_start_progress)
                
                # Each glyph takes time to cycle through all states
                glyph_cycle_duration = 0.6 / total_positions  # Time for full glyph cycle
                position_progress = min(1.0, position_elapsed_progress / glyph_cycle_duration)
                
                # Determine which glyph to show based on progress
                glyph_steps = len(self.glyph_sequence)
                glyph_index = min(glyph_steps - 1, int(position_progress * glyph_steps))
                
                # Calculate brightness (brighter as it progresses)
                brightness = min(1.0, position_progress * 1.2 + 0.4)  # Minimum brightness
                
                self.glyph_progress[pos_index] = {
                    'glyph_index': glyph_index,
                    'progress': position_progress,
                    'brightness': brightness
                }
                active_positions += 1
        
        # Debug output every 200ms
        if elapsed % 200 < 50:  # Print roughly every 200ms
            print(f"[SPELL PREP] Progress: {progress:.2f}, Active positions: {active_positions}/{total_positions}")
        
        return True
    
    def get_ring_glyphs(self, player_x, player_y):
        """Get the current ring glyphs and their properties for rendering."""
        if not self.is_active:
            return []
        
        ring_glyphs = []
        base_color = self.get_level_color(self.player_level)
        
        for pos_index, (dx, dy) in enumerate(self.ring_positions):
            if pos_index in self.glyph_progress:
                progress_data = self.glyph_progress[pos_index]
                glyph_index = progress_data['glyph_index']
                brightness = progress_data['brightness']
                
                # Calculate position
                world_x = player_x + dx
                world_y = player_y + dy
                
                # Get current glyph
                glyph = self.glyph_sequence[glyph_index]
                
                # Calculate color with brightness
                color = pygame.Color(base_color)
                
                # Apply brightness (make it glow)
                r = min(255, int(color.r * brightness))
                g = min(255, int(color.g * brightness))
                b = min(255, int(color.b * brightness))
                final_color = (r, g, b)
                
                ring_glyphs.append({
                    'x': world_x,
                    'y': world_y,
                    'glyph': glyph,
                    'color': final_color,
                    'brightness': brightness
                })
                
                # Debug output for first few glyphs
                if pos_index < 3:
                    print(f"[GLYPH DEBUG] Pos {pos_index}: '{glyph}' (index {glyph_index}) at ({world_x}, {world_y}) brightness {brightness:.2f}")
        
        return ring_glyphs
    
    def is_animation_active(self):
        """Check if the preparation animation is currently active."""
        return self.is_active

class ScreenDarkeningEffect:
    """Manages screen darkening during spell preparation."""
    
    def __init__(self):
        self.is_active = False
        self.start_time = 0
        self.duration = 1000
        self.max_darkness = 0.7  # How dark to make the screen (0.0 - 1.0)
    
    def start(self, duration_ms):
        """Start the screen darkening effect."""
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        self.duration = duration_ms
        print("[SCREEN DARKEN] Starting screen darkening effect")
    
    def end(self):
        """End the screen darkening effect."""
        self.is_active = False
        print("[SCREEN DARKEN] Ending screen darkening effect")
    
    def update(self):
        """Update the darkening effect."""
        if not self.is_active:
            return 0.0
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            return 0.0
        
        # Create a smooth fade in and out
        progress = elapsed / self.duration
        
        # Fade in quickly, stay dark, fade out quickly
        if progress < 0.2:
            # Fade in (0.0 to 1.0)
            fade_factor = progress / 0.2
        elif progress > 0.8:
            # Fade out (1.0 to 0.0)
            fade_factor = (1.0 - progress) / 0.2
        else:
            # Stay at full darkness
            fade_factor = 1.0
        
        return self.max_darkness * fade_factor
    
    def get_darkness_level(self):
        """Get current darkness level (0.0 to 1.0)."""
        return self.update()

# Integration methods for the main VFX manager
def enhance_vfx_manager():
    """Add spell preparation support to the existing VFX manager."""
    def add_screen_darkening(self, duration_ms=1000):
        """Add screen darkening support to VFXManager."""
        if not hasattr(self, 'screen_darkening'):
            self.screen_darkening = ScreenDarkeningEffect()
    
    def start_screen_darkening(self, duration_ms):
        """Start screen darkening effect."""
        if not hasattr(self, 'screen_darkening'):
            self.screen_darkening = ScreenDarkeningEffect()
        self.screen_darkening.start(duration_ms)
    
    def end_screen_darkening(self):
        """End screen darkening effect."""
        if hasattr(self, 'screen_darkening'):
            self.screen_darkening.end()
    
    def get_screen_darkness(self):
        """Get current screen darkness level."""
        if hasattr(self, 'screen_darkening'):
            return self.screen_darkening.get_darkness_level()
        return 0.0
    
    # Add methods to VisualEffectsManager class
    import types
    from game_systems import VisualEffectsManager
    
    VisualEffectsManager.start_screen_darkening = start_screen_darkening
    VisualEffectsManager.end_screen_darkening = end_screen_darkening
    VisualEffectsManager.get_screen_darkness = get_screen_darkness

# Usage example for integration:
"""
# In engine.py initialization:
from spell_preparation import SpellPreparationAnimator, enhance_vfx_manager

# Enhance the VFX manager with darkening support
enhance_vfx_manager()

# Create spell preparation animator
self.spell_prep_animator = SpellPreparationAnimator(self.vfx_manager)

# In the update loop:
self.spell_prep_animator.update()

# When player presses R to prepare spells:
if key == pygame.K_r:
    self.spell_prep_animator.start_preparation(self.player.level)
    # ... rest of spell preparation logic

# In rendering:
# Get ring glyphs and render them
ring_glyphs = self.spell_prep_animator.get_ring_glyphs(self.player.x, self.player.y)
for glyph_data in ring_glyphs:
    # Render each glyph with its position and color
    pass

# Apply screen darkening
darkness = self.vfx_manager.get_screen_darkness()
if darkness > 0:
    # Create dark overlay surface and apply it
    pass
"""