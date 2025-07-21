# engine.py - Refactored CFE Engine with Visual Effects
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

class Game:
    """Main game engine class - now cleaner and more focused."""
    
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
            ("Attack enemies to see flash and knockback effects!", COLOR_WHITE),
        ]

    def add_message(self, msg, color=COLOR_WHITE):
        """Add a message to the game log."""
        if msg:
            self.message_log.append((msg, color))
            self.log_scroll_offset = 0
            print(f"[GAME] {msg}")

    def trigger_hit_effects(self, target, attacker_archetype, attack_type=None, attacker_x=None, attacker_y=None):
        """Trigger both hitstop and visual effects for a hit."""
        print(f"[VFX] Hit effects on {getattr(target, 'name', 'target')}: {attacker_archetype}/{attack_type}")
        
        # Use attacker position or default to player position
        if attacker_x is None:
            attacker_x = self.player.x
        if attacker_y is None:
            attacker_y = self.player.y
        
        # Determine effect type
        effect_type = attack_type if attack_type else attacker_archetype
        
        # Add visual effects
        self.vfx_manager.add_flash_effect(target, 200)
        self.vfx_manager.add_knockback_effect(target, attacker_x, attacker_y, effect_type)
        
        # Trigger hitstop
        duration = get_hitstop_duration(effect_type)
        self.hitstop_manager.freeze_game(duration)

    def change_map(self, place):
        """Switch to a new map."""
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

    def player_move_or_attack(self, dx, dy):
        """Handle player movement with bump-to-attack combat."""
        new_x, new_y = self.player.x + dx, self.player.y + dy
        if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
            # Check for monster to attack
            target = next((e for e in self.all_entities 
                          if isinstance(e, Monster) and e.x == new_x and e.y == new_y and e.hp > 0), None)
            
            if target:
                print(f"[COMBAT] Player attacking {target.name}")
                
                # Attack the monster
                attack_result = self.player.attack(target)
                self.add_message(attack_result, COLOR_BLUE)
                
                # Trigger visual effects if hit
                if "hits" in attack_result or "damage" in attack_result:
                    # Determine attack type
                    if (self.player.archetype == "Warrior" and 
                        hasattr(self.player, 'using_power_attack') and self.player.using_power_attack):
                        self.trigger_hit_effects(target, "Warrior", "PowerAttack", self.player.x, self.player.y)
                    elif (self.player.archetype == "Expert" and 
                          hasattr(self.player, 'last_attack_was_sneak') and self.player.last_attack_was_sneak):
                        self.trigger_hit_effects(target, "Expert", "SneakAttack", self.player.x, self.player.y)
                    else:
                        self.trigger_hit_effects(target, self.player.archetype, None, self.player.x, self.player.y)
                
                # Handle death
                if target.hp <= 0:
                    self.add_message(f"{target.name} is defeated!", COLOR_RED)
                    xp_msg = self.player.gain_monster_xp(target.xp_value)
                    self.add_message(xp_msg, COLOR_GOLD)
                    if self.player.check_for_level_up():
                        self.game_state = 'level_up'
                
            elif not self.game_map[new_x, new_y].blocked:
                # Move to empty space
                self.player.x, self.player.y = new_x, new_y
                tile = self.game_map[new_x, new_y]
                if tile.is_gateway_to:
                    self.change_map(tile.is_gateway_to)
                elif tile.is_exit:
                    self.return_to_previous_map()

    def monster_turns(self):
        """Handle monster turns after player action."""
        # Skip during hitstop
        if self.hitstop_manager.should_skip_update():
            return
            
        # Remove dead entities
        self.all_entities = [e for e in self.all_entities if not (hasattr(e, 'hp') and e.hp <= 0)]
        
        for entity in self.all_entities:
            if entity is not self.player and hasattr(entity, 'hp'):
                message = entity.take_turn(self.player, self.game_map, self.all_entities)
                if message:
                    self.add_message(message, COLOR_RED)
                    # Trigger hitstop for monster hits
                    if "hits" in message or "damage" in message:
                        self.hitstop_manager.freeze_game(get_hitstop_duration("Monster"))
                
                if self.player.hp <= 0:
                    self.game_state = 'game_over'
                    self.add_message("You have died!", COLOR_RED)
                    self.running = False
                    break

    def handle_continuous_movement(self):
        """Handle continuous movement input."""
        # Skip during hitstop
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
        # Update core systems
        self.hitstop_manager.update()
        self.vfx_manager.update()
        
        # Only update game logic if not frozen
        if not self.hitstop_manager.should_skip_update():
            self.handle_continuous_movement()
            # Add other updates here as needed

    def draw(self):
        """Draw the entire game."""
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
        
        # Draw UI panels
        self.renderer.draw_ui(
            self.right_panel_tabs_rect, self.panel_tabs, self.active_panel,
            self.right_panel_rect, self.player, self.input_focus,
            self.equipment_selected_index, self.inventory_selected_index,
            self.spells_selected_index, self.quest_selected_index
        )
        
        # Draw log
        self.renderer.draw_log(
            self.log_rect, self.message_log, self.log_scroll_offset,
            self.input_focus == 'log'
        )
        
        # Draw popups and windows
        if self.game_state == 'level_up':
            level_up_rect = pygame.Rect(0, 0, 400, 200)
            level_up_rect.center = self.screen.get_rect().center
            draw_level_up_window(self.screen, level_up_rect, self.font)
        
        # Add other popup windows as needed...
        
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        print("[DEBUG] Starting main game loop")
        
        while self.running:
            self.clock.tick(FPS)
            
            # Handle input
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.input_handler.handle_event(event)
            
            # Update game systems
            self.update()
            
            # Draw everything
            self.draw()

    # Save/Load methods (simplified for now)
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