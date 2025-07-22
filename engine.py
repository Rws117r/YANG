# engine.py - Updated with Music System Integration
import pygame
import math
import json
import os
import sys
from config import *
from ui import *
from world_generation import generate_overworld, generate_cfe_dungeon, Tile
from entities import Monster, NPC, Player, roll_dice
from spells import get_spell_by_name, CORE_SPELLS
from game_systems import HitstopManager, VisualEffectsManager, get_hitstop_duration
from rendering import GameRenderer
from input_handler import InputHandler

from audio_system import initialize_game_audio

class MusicManager:
    """Manages background music for the game."""
    
    def __init__(self):
        self.current_music = None
        self.current_location_type = None
        self.music_volume = 0.6
        self.music_enabled = True
        self.fade_duration = 2000  # 2 seconds
        
        # Music file mappings
        self.music_files = {
            'overworld': 'overworld_theme_loop.wav',
            'overworld_full': 'overworld_theme.wav',
            'menu': 'overworld_theme.wav',
            'village': 'village_theme_loop.wav',
            'village_full': 'village_theme.wav',
            'dungeon': 'dungeon_theme_loop.wav',
            'dungeon_full': 'dungeon_theme.wav',
            'dungeon_ambient': 'dungeon_ambient.wav',
            'silence': None
        }
        
        # Volume settings for different areas
        self.area_volumes = {
            'overworld': 0.6,
            'village': 0.5,
            'dungeon': 0.4,
            'dungeon_ambient': 0.3,
            'menu': 0.7
        }
        
        pygame.mixer.init()
        print("[MUSIC] Music manager initialized")
    
    def play_music(self, track_name, loops=-1, fade_ms=None):
        """Play background music with area-appropriate volume."""
        if not self.music_enabled:
            return
        
        if track_name not in self.music_files:
            print(f"[MUSIC] Unknown track: {track_name}")
            return
        
        # Handle silence
        if self.music_files[track_name] is None:
            self.stop_music(fade_ms or self.fade_duration)
            return
        
        music_file = os.path.join("sounds", self.music_files[track_name])
        
        if not os.path.exists(music_file):
            print(f"[MUSIC] Music file not found: {music_file}")
            return
        
        # Don't restart if already playing the same track
        if self.current_music == track_name and pygame.mixer.music.get_busy():
            return
        
        try:
            # Set appropriate volume for the track
            volume = self.area_volumes.get(track_name, self.music_volume)
            
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms or self.fade_duration)
            
            self.current_music = track_name
            print(f"[MUSIC] Playing: {track_name} (volume: {volume:.1f})")
            
        except pygame.error as e:
            print(f"[MUSIC ERROR] Could not play {music_file}: {e}")
    
    def change_music_for_location(self, location_name, location_type=None):
        """Intelligently change music based on location."""
        # Determine location type if not provided
        if location_type is None:
            location_type = self.detect_location_type(location_name)
        
        # Don't change if already in the same type of location
        if self.current_location_type == location_type:
            return
        
        self.current_location_type = location_type
        
        # Select appropriate music
        if location_type == 'village':
            self.play_music('village', fade_ms=self.fade_duration)
        elif location_type == 'dungeon':
            self.play_music('dungeon', fade_ms=self.fade_duration)
        elif location_type == 'dungeon_stealth':
            self.play_music('dungeon_ambient', fade_ms=self.fade_duration)
        elif location_type == 'overworld':
            self.play_music('overworld', fade_ms=self.fade_duration)
        elif location_type == 'menu':
            self.play_music('menu', fade_ms=self.fade_duration)
        elif location_type == 'silence':
            self.play_music('silence', fade_ms=self.fade_duration)
        
        print(f"[MUSIC] Location: {location_name} -> Music: {location_type}")
    
    def detect_location_type(self, location_name):
        """Detect location type from location name."""
        location_lower = location_name.lower()
        
        if any(word in location_lower for word in ['village', 'town', 'settlement', 'hamlet']):
            return 'village'
        elif any(word in location_lower for word in ['dungeon', 'crypt', 'cave', 'tomb', 'catacomb', 'lair']):
            return 'dungeon'
        elif any(word in location_lower for word in ['tower', 'fortress', 'castle']):
            return 'dungeon'
        else:
            return 'overworld'
    
    def stop_music(self, fade_ms=None):
        """Stop background music."""
        pygame.mixer.music.fadeout(fade_ms or self.fade_duration)
        self.current_music = None
        self.current_location_type = None
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
        if pygame.mixer.music.get_busy() and self.current_music:
            area_volume = self.area_volumes.get(self.current_music, self.music_volume)
            pygame.mixer.music.set_volume(area_volume)
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

class Game:
    """Main game engine class - now with music support."""
    
    def __init__(self, screen, font, clock, player):
        self.screen = screen
        self.font = font
        self.clock = clock
        self.player = player
        self.running = True
        
        # --- Core Systems ---
        self.hitstop_manager = HitstopManager()
        self.vfx_manager = VisualEffectsManager()
        self.renderer = GameRenderer(screen, font, self.vfx_manager)
        self.input_handler = InputHandler(self)
        
        # --- Audio System ---
        self.audio_manager = initialize_game_audio()
        if self.audio_manager:
            print("[DEBUG] Audio system initialized successfully")
            if hasattr(self.player, 'set_audio_manager'):
                self.player.set_audio_manager(self.audio_manager)
        else:
            print("[DEBUG] Audio system failed to initialize - continuing without audio")
        
        # --- Music System ---
        self.music_manager = MusicManager()
        if self.music_manager:
            print("[DEBUG] Music system initialized successfully")
        else:
            print("[DEBUG] Music system failed to initialize")
        
        print("[DEBUG] Core systems initialized")
        
        # --- UI State ---
        self.input_focus = 'world'
        self.panel_tabs = [CHARACTER_SHEET_ICON, EQUIPMENT_ICON, INVENTORY_ICON, SPELLS_ICON, QUESTS_ICON, LOCATIONS_ICON]
        self.active_panel = CHARACTER_SHEET_ICON
        self.inventory_selected_index = 0
        self.equipment_selected_index = 0
        self.quest_selected_index = 0
        self.spells_selected_index = 0
        self.item_options_selected_index = 0
        self.equip_selection_index = 0
        self.pause_menu_selected_index = 0
        self.log_scroll_offset = 0
        self.quest_details_window = None
        
        # --- Spell Targeting State ---
        self.targeting_mode = False
        self.targeting_spell = None
        self.target_cursor = (0, 0)
        self.valid_targets = []
        self.spell_range_tiles = []
        self.spell_area_tiles = []
        
        # --- UI Rects ---
        self.game_rect = pygame.Rect(20, 20, 860, 540)
        self.log_rect = pygame.Rect(20, 580, 860, 120)
        self.right_panel_tabs_rect = pygame.Rect(900, 20, 360, 30)
        buffer = self.right_panel_tabs_rect.height
        panel_y = self.right_panel_tabs_rect.top + buffer
        panel_height = SCREEN_HEIGHT - panel_y - 20
        self.right_panel_rect = pygame.Rect(900, panel_y, 360, panel_height)

        # --- Game State ---
        self.game_state = 'playing'
        self.map_stack = []
        self.load_overworld()

        # Start at village if available
        village = next((p for p in self.places if p.name == "Saltwind Village"), None)
        if village:
            self.player.x, self.player.y = village.x, village.y
            self.change_map(village)
        else:
            # Start overworld music if no village
            if self.music_manager:
                self.music_manager.change_music_for_location("Overworld", "overworld")

        self.look_cursor = (self.player.x, self.player.y)
        self.move_delay = 150
        self.last_move_time = 0

    def load_overworld(self):
        """Load the main overworld map."""
        self.map_width, self.map_height = 200, 200
        self.game_map, player_start, self.monsters, self.places = generate_overworld(self.map_width, self.map_height)
        self.player.x, self.player.y = player_start
        self.all_entities = [self.player] + self.monsters
        self.message_log = [
            ("Welcome to the Core Fantasy Engine!", COLOR_GOLD),
            ("Combat now has satisfying visual feedback!", COLOR_PURPLE),
            ("Attack enemies to see flash, knockback & screen shake!", COLOR_WHITE),
            ("Each archetype has unique movement sounds!", COLOR_BLUE),
            ("Enjoy the atmospheric music as you explore!", COLOR_GREEN),
        ]

    def add_message(self, msg, color=COLOR_WHITE):
        """Add a message to the game log."""
        if msg:
            self.message_log.append((msg, color))
            self.log_scroll_offset = 0
            print(f"[GAME] {msg}")

    def change_music_for_area(self, location_name, location_type=None):
        """Change music when entering new areas."""
        if self.music_manager:
            self.music_manager.change_music_for_location(location_name, location_type)

    def pause_game_music(self):
        """Pause music (for pause menu, conversations, etc.)."""
        if self.music_manager:
            self.music_manager.pause_music()

    def resume_game_music(self):
        """Resume music."""
        if self.music_manager:
            self.music_manager.unpause_music()

    def trigger_hit_effects(self, target, attacker_archetype, attack_type=None, attacker_x=None, attacker_y=None):
        """Trigger hitstop, visual effects, and screen shake for a hit."""
        print(f"[VFX] Hit effects on {getattr(target, 'name', 'target')}: {attacker_archetype}/{attack_type}")
        
        if attacker_x is None:
            attacker_x = self.player.x
        if attacker_y is None:
            attacker_y = self.player.y
        
        effect_type = attack_type if attack_type else attacker_archetype
        
        self.vfx_manager.add_flash_effect(target, 200)
        self.vfx_manager.add_knockback_effect(target, attacker_x, attacker_y, effect_type)
        self.vfx_manager.add_screen_shake(attacker_archetype, attack_type)
        
        duration = get_hitstop_duration(effect_type)
        self.hitstop_manager.freeze_game(duration)

    def change_map(self, place):
        """Switch to a new map with appropriate music."""
        if not place.generator_func:
            self.add_message("This area has not been implemented yet.", COLOR_GREY)
            return

        self.player.known_locations.add(place.name)

        # Save current state
        current_state = {
            "map": self.game_map, "player_pos": (self.player.x, self.player.y),
            "entities": self.all_entities, "places": self.places,
            "width": self.map_width, "height": self.map_height
        }
        self.map_stack.append(current_state)

        # Generate or load map
        if place.generated_map is None:
            map_width, map_height = 50, 50
            new_map, player_start, entities, sub_places = place.generator_func(map_width, map_height)
            place.generated_map = new_map
            place.player_start_pos = player_start
            
            self.game_map = new_map
            self.player.x, self.player.y = player_start
            self.all_entities = [self.player] + entities
            self.places = sub_places
            self.map_width, self.map_height = map_width, map_height
            self.add_message(f"You enter {place.name}.", COLOR_GATEWAY)
        else:
            self.game_map = place.generated_map
            self.player.x, self.player.y = place.player_start_pos
            self.all_entities = [self.player]
            self.places = []
            self.map_width, self.map_height = self.game_map.shape
            self.add_message(f"You return to {place.name}.", COLOR_GATEWAY)

        # Change music based on location
        self.change_music_for_area(place.name)

    def return_to_previous_map(self):
        """Return to the previous map."""
        if not self.map_stack:
            return

        previous_state = self.map_stack.pop()
        self.game_map = previous_state["map"]
        self.player.x, self.player.y = previous_state["player_pos"]
        self.all_entities = previous_state["entities"]
        self.places = previous_state["places"]
        self.map_width = previous_state["width"]
        self.map_height = previous_state["height"]
        self.add_message("You return to the wilderness.", COLOR_GATEWAY)
        
        # Return to overworld music
        self.change_music_for_area("Overworld", "overworld")

    def player_move_or_attack(self, dx, dy):
        """Handle player movement with bump-to-attack combat and contextual audio."""
        new_x, new_y = self.player.x + dx, self.player.y + dy
        if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
            target = next((e for e in self.all_entities 
                          if isinstance(e, Monster) and e.x == new_x and e.y == new_y and e.hp > 0), None)
            
            if target:
                print(f"[COMBAT] Player attacking {target.name}")
                
                if self.audio_manager:
                    self.audio_manager.play_attack_sound(self.player.archetype)
                
                attack_result = self.player.attack(target)
                self.add_message(attack_result, COLOR_BLUE)
                
                if "hits" in attack_result or "damage" in attack_result:
                    if (self.player.archetype == "Warrior" and 
                        hasattr(self.player, 'using_power_attack') and self.player.using_power_attack):
                        self.trigger_hit_effects(target, "Warrior", "PowerAttack", self.player.x, self.player.y)
                    elif (self.player.archetype == "Expert" and 
                          hasattr(self.player, 'last_attack_was_sneak') and self.player.last_attack_was_sneak):
                        self.trigger_hit_effects(target, "Expert", "SneakAttack", self.player.x, self.player.y)
                    else:
                        self.trigger_hit_effects(target, self.player.archetype, None, self.player.x, self.player.y)
                
                if target.hp <= 0:
                    self.add_message(f"{target.name} is defeated!", COLOR_RED)
                    xp_msg = self.player.gain_monster_xp(target.xp_value)
                    self.add_message(xp_msg, COLOR_GOLD)
                    if self.player.check_for_level_up():
                        self.game_state = 'level_up'
                        if self.audio_manager:
                            self.audio_manager.play_level_up()
                
            elif not self.game_map[new_x, new_y].blocked:
                old_x, old_y = self.player.x, self.player.y
                self.player.x, self.player.y = new_x, new_y
                
                if self.audio_manager:
                    tile = self.game_map[new_x, new_y]
                    if tile.name in ["deep water", "shallow water"]:
                        self.audio_manager.play_contextual_movement('water')
                
                tile = self.game_map[new_x, new_y]
                if tile.is_gateway_to:
                    if self.audio_manager:
                        self.audio_manager.play_area_transition()
                    self.change_map(tile.is_gateway_to)
                elif tile.is_exit:
                    if self.audio_manager:
                        self.audio_manager.play_area_transition()
                    self.return_to_previous_map()

    def monster_turns(self):
        """Handle monster turns after player action."""
        if self.hitstop_manager.should_skip_update():
            return
            
        self.all_entities = [e for e in self.all_entities if not (hasattr(e, 'hp') and e.hp <= 0)]
        
        for entity in self.all_entities:
            if entity is not self.player and hasattr(entity, 'hp'):
                message = entity.take_turn(self.player, self.game_map, self.all_entities)
                if message:
                    self.add_message(message, COLOR_RED)
                    if "hits" in message or "damage" in message:
                        self.hitstop_manager.freeze_game(get_hitstop_duration("Monster"))
                
                if self.player.hp <= 0:
                    self.game_state = 'game_over'
                    self.add_message("You have died!", COLOR_RED)
                    self.running = False
                    break

    def handle_continuous_movement(self):
        """Handle continuous movement input."""
        if self.hitstop_manager.should_skip_update():
            return
            
        if self.input_focus != 'world' or self.game_state != 'playing' or self.targeting_mode:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time > self.move_delay:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_UP]: dy = -1
            elif keys[pygame.K_DOWN]: dy = 1
            elif keys[pygame.K_LEFT]: dx = -1
            elif keys[pygame.K_RIGHT]: dx = 1
            
            if dx != 0 or dy != 0:
                self.player_move_or_attack(dx, dy)
                self.monster_turns()
                self.last_move_time = current_time

    def update(self):
        """Update all game systems."""
        self.hitstop_manager.update()
        self.vfx_manager.update()
        
        if not self.hitstop_manager.should_skip_update():
            self.handle_continuous_movement()

    def draw(self):
        """Draw the entire game."""
        self.screen.fill(COLOR_BLACK)
        
        self.renderer.draw_game(
            self.game_map, self.all_entities, self.player,
            self.map_width, self.map_height,
            self.game_rect, self.hitstop_manager.is_frozen,
            targeting_mode=self.targeting_mode,
            spell_range_tiles=self.spell_range_tiles,
            spell_area_tiles=self.spell_area_tiles,
            target_cursor=self.target_cursor,
            look_cursor=self.look_cursor,
            game_state=self.game_state
        )
        
        self.renderer.draw_ui(
            self.right_panel_tabs_rect, self.panel_tabs, self.active_panel,
            self.right_panel_rect, self.player, self.input_focus,
            self.equipment_selected_index, self.inventory_selected_index,
            self.spells_selected_index, self.quest_selected_index
        )
        
        self.renderer.draw_log(
            self.log_rect, self.message_log, self.log_scroll_offset,
            self.input_focus == 'log'
        )
        
        # Draw popups and windows (existing code unchanged)
        if self.game_state == 'level_up':
            level_up_rect = pygame.Rect(0, 0, 400, 200)
            level_up_rect.center = self.screen.get_rect().center
            draw_level_up_window(self.screen, level_up_rect, self.font)
        
        elif self.game_state == 'show_item_options':
            if self.player.display_inventory and self.inventory_selected_index < len(self.player.display_inventory):
                item = self.player.display_inventory[self.inventory_selected_index]
                options = ["Use", "Drop"]
                item_options_rect = pygame.Rect(0, 0, 250, 200)
                item_options_rect.center = self.screen.get_rect().center
                draw_item_options_window(self.screen, item_options_rect, item, options, 
                                       self.item_options_selected_index, self.font)
        
        elif self.game_state == 'select_item_to_equip':
            if self.equipment_selected_index < len(self.player.equipment):
                slot = list(self.player.equipment.keys())[self.equipment_selected_index]
                items = [item for item in self.player.inventory 
                        if hasattr(item, 'equip_slot') and item.equip_slot == slot]
                
                height = 150 + (len(items) * 60) if items else 150
                equip_rect = pygame.Rect(0, 0, 350, height)
                equip_rect.center = self.screen.get_rect().center
                draw_equipment_selection_window(self.screen, equip_rect, items, 
                                              self.equip_selection_index, self.font)
        
        elif self.game_state == 'show_quest_details' and self.quest_details_window:
            quest_rect = pygame.Rect(0, 0, 500, 350)
            quest_rect.center = self.screen.get_rect().center
            draw_quest_details_window(self.screen, quest_rect, self.quest_details_window, self.font)
        
        elif self.game_state == 'pause_menu':
            pause_rect = pygame.Rect(0, 0, 300, 280)
            pause_rect.center = self.screen.get_rect().center
            draw_pause_menu_window(self.screen, pause_rect, self.pause_menu_selected_index, self.font)
        
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        print("[DEBUG] Starting main game loop")
        
        while self.running:
            self.clock.tick(FPS)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.input_handler.handle_event(event)
            
            self.update()
            self.draw()

    def save_game(self, filename="savegame.json"):
        """Save game state."""
        try:
            if not os.path.exists("saves"):
                os.makedirs("saves")
            
            save_data = {
                "player": {
                    "name": self.player.name,
                    "archetype": self.player.archetype,
                    "level": self.player.level,
                    "xp": self.player.xp,
                    "hp": self.player.hp,
                    "max_hp": self.player.max_hp,
                    "gold": self.player.gold,
                    "x": self.player.x,
                    "y": self.player.y,
                    "abilities": self.player.abilities,
                    "known_locations": list(self.player.known_locations),
                }
            }
            
            filepath = os.path.join("saves", filename)
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return "Game saved successfully!"
        except Exception as e:
            return f"Save failed: {str(e)}"

    def load_game(self, filename="savegame.json"):
        """Load game state."""
        try:
            filepath = os.path.join("saves", filename)
            if not os.path.exists(filepath):
                return "No save file found!"
            
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            player_data = save_data["player"]
            self.player.name = player_data["name"]
            self.player.archetype = player_data["archetype"]
            self.player.level = player_data["level"]
            self.player.xp = player_data["xp"]
            self.player.hp = player_data["hp"]
            self.player.max_hp = player_data["max_hp"]
            self.player.gold = player_data["gold"]
            self.player.x = player_data["x"]
            self.player.y = player_data["y"]
            self.player.abilities = player_data["abilities"]
            self.player.update_modifiers()
            self.player.known_locations = set(player_data["known_locations"])
            
            self.load_overworld()
            return "Game loaded successfully!"
        except Exception as e:
            return f"Load failed: {str(e)}"