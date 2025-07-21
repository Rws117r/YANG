# game_systems.py - Core game systems (hitstop, visual effects)
import pygame
import math
import sys

class HitstopManager:
    """Manages game freezing for impactful combat feedback."""
    
    def __init__(self):
        self.freeze_time_remaining = 0
        self.freeze_start_time = 0
        self.is_frozen = False
    
    def freeze_game(self, duration_ms):
        """Freeze the game for the specified duration in milliseconds."""
        self.freeze_time_remaining = duration_ms
        self.freeze_start_time = pygame.time.get_ticks()
        self.is_frozen = True
        print(f"[HITSTOP] Freezing for {duration_ms}ms")
        sys.stdout.flush()
    
    def update(self):
        """Update the hitstop timer and unfreeze when duration expires."""
        if self.is_frozen:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.freeze_start_time
            
            if elapsed >= self.freeze_time_remaining:
                self.is_frozen = False
                self.freeze_time_remaining = 0
                print(f"[HITSTOP] Unfrozen after {elapsed}ms")
                sys.stdout.flush()
    
    def should_skip_update(self):
        """Return True if game updates should be skipped due to hitstop."""
        return self.is_frozen

class VisualEffect:
    """Base class for all visual effects."""
    def __init__(self, duration_ms):
        self.start_time = pygame.time.get_ticks()
        self.duration = duration_ms
        self.is_active = True
    
    def update(self):
        """Update the effect and return True if still active."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            self.is_active = False
            return False
        
        return True
    
    def get_progress(self):
        """Return progress from 0.0 to 1.0."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration)

class FlashEffect(VisualEffect):
    """White flash effect for damaged entities."""
    def __init__(self, duration_ms=200):
        super().__init__(duration_ms)
        self.flash_color = (255, 255, 255)
    
    def get_flash_intensity(self):
        """Return flash intensity from 1.0 to 0.0."""
        progress = self.get_progress()
        return max(0.0, 1.0 - (progress * 2))

class KnockbackEffect(VisualEffect):
    """Knockback animation that moves entity and bounces back."""
    def __init__(self, start_x, start_y, target_x, target_y, intensity=1.0, duration_ms=300):
        super().__init__(duration_ms)
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.intensity = intensity
        
        # Calculate knockback direction
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.knockback_dx = (dx / distance) * intensity
            self.knockback_dy = (dy / distance) * intensity
        else:
            self.knockback_dx = 0
            self.knockback_dy = 0
    
    def get_offset(self):
        """Return current visual offset (dx, dy) in pixels."""
        if not self.is_active:
            return (0, 0)
        
        progress = self.get_progress()
        
        # Bounce-back animation
        if progress < 0.3:
            # Quick push out
            t = progress / 0.3
            multiplier = t * self.intensity
        else:
            # Bounce back
            t = (progress - 0.3) / 0.7
            ease_t = t * t * (3.0 - 2.0 * t)  # Smoothstep
            multiplier = self.intensity * (1.0 - ease_t)
        
        # Convert to pixel offset
        from config import TILE_WIDTH, TILE_HEIGHT
        offset_x = self.knockback_dx * multiplier * TILE_WIDTH
        offset_y = self.knockback_dy * multiplier * TILE_HEIGHT
        
        return (int(offset_x), int(offset_y))

class VisualEffectsManager:
    """Manages all visual effects for entities."""
    def __init__(self):
        self.entity_effects = {}
        self.screen_shake = ScreenShakeManager()
    
    def add_flash_effect(self, entity, duration_ms=200):
        """Add a flash effect to an entity."""
        entity_id = id(entity)
        if entity_id not in self.entity_effects:
            self.entity_effects[entity_id] = []
        
        flash = FlashEffect(duration_ms)
        self.entity_effects[entity_id].append(flash)
        print(f"[VFX] Flash effect added to {getattr(entity, 'name', 'entity')}")
        sys.stdout.flush()
    
    def add_knockback_effect(self, entity, attacker_x, attacker_y, archetype="Default"):
        """Add a knockback effect to an entity."""
        intensity_map = {
            "Warrior": 1.5, "Expert": 0.8, "Mage": 1.2, "Monster": 1.0,
            "PowerAttack": 2.0, "SneakAttack": 0.6, "Fireball": 1.8, "Default": 1.0
        }
        
        intensity = intensity_map.get(archetype, 1.0)
        duration = int(300 * (0.8 + intensity * 0.4))
        
        entity_id = id(entity)
        if entity_id not in self.entity_effects:
            self.entity_effects[entity_id] = []
        
        knockback = KnockbackEffect(attacker_x, attacker_y, entity.x, entity.y, intensity, duration)
        self.entity_effects[entity_id].append(knockback)
        print(f"[VFX] {archetype} knockback (intensity {intensity}) added to {getattr(entity, 'name', 'entity')}")
        sys.stdout.flush()
    
    def add_screen_shake(self, archetype, attack_type=None):
        """Add a screen shake effect."""
        self.screen_shake.add_shake(archetype, attack_type)
    
    def update(self):
        """Update all effects and remove expired ones."""
        # Update entity effects
        entities_to_remove = []
        
        for entity_id, effects in self.entity_effects.items():
            active_effects = [effect for effect in effects if effect.update()]
            
            if active_effects:
                self.entity_effects[entity_id] = active_effects
            else:
                entities_to_remove.append(entity_id)
        
        for entity_id in entities_to_remove:
            del self.entity_effects[entity_id]
        
        # Update screen shake
        self.screen_shake.update()
    
    def get_flash_intensity(self, entity):
        """Get the flash intensity for an entity (0.0 to 1.0)."""
        entity_id = id(entity)
        effects = self.entity_effects.get(entity_id, [])
        max_intensity = 0.0
        
        for effect in effects:
            if isinstance(effect, FlashEffect) and effect.is_active:
                max_intensity = max(max_intensity, effect.get_flash_intensity())
        
        return max_intensity
    
    def get_knockback_offset(self, entity):
        """Get the visual offset for knockback effects."""
        entity_id = id(entity)
        effects = self.entity_effects.get(entity_id, [])
        total_dx, total_dy = 0, 0
        
        for effect in effects:
            if isinstance(effect, KnockbackEffect) and effect.is_active:
                dx, dy = effect.get_offset()
                total_dx += dx
                total_dy += dy
        
        return (total_dx, total_dy)
    
    def get_screen_shake_offset(self):
        """Get the current screen shake offset."""
        return self.screen_shake.get_total_shake_offset()
    
    def is_screen_shaking(self):
        """Check if screen is currently shaking."""
        return self.screen_shake.is_shaking()

# Hitstop duration constants
HITSTOP_WARRIOR = 120
HITSTOP_EXPERT = 80
HITSTOP_MAGE = 100
HITSTOP_MONSTER = 90

def get_hitstop_duration(attacker_type, is_critical=False, is_power_attack=False):
    """Return appropriate hitstop duration based on attacker and attack type."""
    base_duration = {
        "Warrior": HITSTOP_WARRIOR,
        "Expert": HITSTOP_EXPERT,
        "Mage": HITSTOP_MAGE,
        "Monster": HITSTOP_MONSTER,
        "PowerAttack": HITSTOP_WARRIOR + 20,
        "SneakAttack": HITSTOP_EXPERT + 10,
        "Spell": HITSTOP_MAGE,
        "MagicMissile": HITSTOP_MAGE - 20,
        "Fireball": HITSTOP_MAGE + 30,
        "Default": 60
    }.get(attacker_type, 60)
    
    if is_critical:
        base_duration += 30
    if is_power_attack:
        base_duration += 20
    
    return base_duration

def lerp_color(color1, color2, t):
    """Linear interpolation between two colors."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    
    return (r, g, b)

class ScreenShakeEffect(VisualEffect):
    """Screen shake effect with easing and intensity variation."""
    def __init__(self, intensity=1.0, duration_ms=250):
        super().__init__(duration_ms)
        self.intensity = intensity
        self.base_magnitude = intensity
    
    def get_shake_offset(self):
        """Return current screen shake offset (dx, dy) in pixels."""
        if not self.is_active:
            return (0, 0)
        
        progress = self.get_progress()
        
        # Easing curve: start strong, fade out smoothly
        # Using exponential decay for natural feel
        ease_factor = (1.0 - progress) ** 2
        current_magnitude = self.base_magnitude * ease_factor
        
        # Generate random shake in both directions
        import random
        shake_x = random.uniform(-current_magnitude, current_magnitude)
        shake_y = random.uniform(-current_magnitude, current_magnitude)
        
        return (int(shake_x), int(shake_y))

class ScreenShakeManager:
    """Manages screen shake effects with intensity stacking."""
    def __init__(self):
        self.active_shakes = []
    
    def add_shake(self, archetype, attack_type=None):
        """Add a screen shake effect based on archetype and attack type."""
        # Intensity mapping for different archetypes and attacks
        intensity_map = {
            "Warrior": 9,      # Heavy shake (8-10 pixels)
            "Expert": 5,       # Medium shake (4-6 pixels)  
            "Mage": 3,         # Light shake (2-4 pixels)
            "Monster": 4,      # Medium shake for monsters
            "PowerAttack": 12, # Extra heavy for power attacks
            "SneakAttack": 3,  # Light shake for stealth
            "Fireball": 8,     # Heavy magical explosion
            "MagicMissile": 2, # Very light for quick spell
            "Default": 4
        }
        
        # Get base intensity
        if attack_type and attack_type in intensity_map:
            intensity = intensity_map[attack_type]
        else:
            intensity = intensity_map.get(archetype, 4)
        
        # Duration based on intensity (heavier shakes last slightly longer)
        duration = int(250 + (intensity * 10))  # 250-370ms range
        
        # Create shake effect
        shake = ScreenShakeEffect(intensity, duration)
        self.active_shakes.append(shake)
        
        print(f"[SCREEN SHAKE] Added {archetype}/{attack_type} shake: {intensity}px for {duration}ms")
        sys.stdout.flush()
    
    def update(self):
        """Update all shake effects and remove expired ones."""
        self.active_shakes = [shake for shake in self.active_shakes if shake.update()]
    
    def get_total_shake_offset(self):
        """Get combined shake offset from all active effects."""
        total_x, total_y = 0, 0
        
        for shake in self.active_shakes:
            shake_x, shake_y = shake.get_shake_offset()
            total_x += shake_x
            total_y += shake_y
        
        # Cap maximum shake to prevent excessive movement
        max_shake = 15
        total_x = max(-max_shake, min(max_shake, total_x))
        total_y = max(-max_shake, min(max_shake, total_y))
        
        return (int(total_x), int(total_y))
    
    def is_shaking(self):
        """Return True if any shake effects are active."""
        return len(self.active_shakes) > 0
    
    def clear_all_shakes(self):
        """Clear all active shake effects."""
        self.active_shakes = []

def apply_flash_to_color(original_color, flash_intensity):
    """Apply white flash effect to a color."""
    if flash_intensity <= 0:
        return original_color
    
    return lerp_color(original_color, (255, 255, 255), flash_intensity)