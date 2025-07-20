# engine.py - Complete revised CFE implementation with targeting
import pygame
import math
import json
import os
from config import *
from ui import (
    draw_panel, draw_tabs, draw_log_panel, draw_equipment_panel, 
    draw_inventory_panel, draw_text, draw_character_sheet_panel, 
    draw_locations_panel, draw_quests_panel, draw_quest_details_window, 
    draw_level_up_window, draw_item_options_window, draw_equipment_selection_window, 
    draw_pause_menu_window, draw_spells_panel, draw_targeting_overlay
)
from world_generation import generate_overworld
from world_generation import generate_cfe_dungeon
from world_generation import Tile
from entities import Monster, NPC, Player, roll_dice
from spells import get_spell_by_name, CORE_SPELLS

class Game:
    """The main game engine class with CFE integration and spell targeting."""
    def __init__(self, screen, font, clock, player):
        self.screen = screen
        self.font = font
        self.clock = clock
        self.player = player
        self.running = True
        
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
        self.game_surface = pygame.Surface(self.game_rect.size)

        # --- Game State ---
        self.game_state = 'playing'
        self.map_stack = []
        self.load_overworld()

        village = next((p for p in self.places if p.name == "Saltwind Village"), None)
        if village:
            self.player.x, self.player.y = village.x, village.y
            self.change_map(village)

        self.look_cursor = (self.player.x, self.player.y)
        self.move_delay = 150
        self.last_move_time = 0

    def load_overworld(self):
        """Loads the main overworld map."""
        self.map_width, self.map_height = 200, 200
        self.game_map, player_start, self.monsters, self.places = generate_overworld(self.map_width, self.map_height)
        self.player.x, self.player.y = player_start
        self.all_entities = [self.player] + self.monsters
        self.message_log = [
            ("Welcome to the Core Fantasy Engine!", COLOR_GOLD),
            ("You are on the shores of a vast island.", COLOR_WHITE),
            ("Explore the wilderness. (L to look, TAB to cycle focus)", COLOR_WHITE),
            ("Press C in spells panel to cast spells!", COLOR_BLUE)
        ]

    def change_map(self, place):
        """Switches to a new map, using a cached version if it exists."""
        if not place.generator_func:
            self.add_message("This area has not been implemented yet.", COLOR_GREY)
            return

        self.player.known_locations.add(place.name)

        current_state = {
            "map": self.game_map, "player_pos": (self.player.x, self.player.y),
            "entities": self.all_entities, "places": self.places,
            "width": self.map_width, "height": self.map_height
        }
        self.map_stack.append(current_state)

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
        """Returns the player to the previous map."""
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

    def add_message(self, msg, color=COLOR_WHITE):
        if msg:
            self.message_log.append((msg, color))
            self.log_scroll_offset = 0

    def save_game(self, filename="savegame.json"):
        """Saves the current game state to a JSON file."""
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
                },
                "map_info": {
                    "current_map_type": "overworld" if not self.map_stack else "sub_map",
                    "map_stack_depth": len(self.map_stack)
                }
            }
            
            filepath = os.path.join("saves", filename)
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return f"Game saved successfully!"
        except Exception as e:
            return f"Save failed: {str(e)}"

    def load_game(self, filename="savegame.json"):
        """Loads a game state from a JSON file."""
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

    # --- Spell Targeting System ---
    
    def start_spell_targeting(self, spell_name):
        """Initiate targeting mode for a spell."""
        spell = get_spell_by_name(spell_name)
        if not spell:
            return False
        
        self.targeting_mode = True
        self.targeting_spell = spell
        self.target_cursor = (self.player.x, self.player.y)
        
        # Calculate valid targeting areas
        self.calculate_spell_targeting(spell)
        
        self.add_message(f"Targeting {spell_name}. Use arrows to aim, ENTER to cast, ESC to cancel.", COLOR_PURPLE)
        return True

    def calculate_spell_targeting(self, spell):
        """Calculate valid targeting tiles for the spell."""
        self.spell_range_tiles = []
        self.spell_area_tiles = []
        
        # Calculate range (convert feet to tiles, roughly 5 feet per tile)
        spell_range = spell.range // 5 if spell.range else 1
        if spell.target_type == "self":
            spell_range = 0
        elif spell.target_type == "touch":
            spell_range = 1
        
        # Calculate all tiles within range
        for x in range(max(0, self.player.x - spell_range), 
                      min(self.map_width, self.player.x + spell_range + 1)):
            for y in range(max(0, self.player.y - spell_range), 
                          min(self.map_height, self.player.y + spell_range + 1)):
                distance = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
                if distance <= spell_range:
                    self.spell_range_tiles.append((x, y))
        
        # Calculate area of effect around target cursor
        self.update_spell_area()

    def update_spell_area(self):
        """Update area of effect tiles around the target cursor."""
        self.spell_area_tiles = []
        
        if not self.targeting_spell:
            return
        
        # Area of effect radius (simplified)
        if self.targeting_spell.target_type == "area":
            if self.targeting_spell.name == "Fireball":
                radius = 2  # 20 foot radius = roughly 4 tiles diameter
            else:
                radius = 1  # Default small area
                
            cx, cy = self.target_cursor
            for x in range(max(0, cx - radius), min(self.map_width, cx + radius + 1)):
                for y in range(max(0, cy - radius), min(self.map_height, cy + radius + 1)):
                    distance = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if distance <= radius:
                        self.spell_area_tiles.append((x, y))

    def end_spell_targeting(self):
        """End targeting mode."""
        self.targeting_mode = False
        self.targeting_spell = None
        self.spell_range_tiles = []
        self.spell_area_tiles = []

    def cast_targeted_spell(self):
        """Cast the currently targeted spell."""
        if not self.targeting_spell:
            return
        
        spell = self.targeting_spell
        target = None
        
        # Find target at cursor position
        for entity in self.all_entities:
            if entity.x == self.target_cursor[0] and entity.y == self.target_cursor[1] and entity != self.player:
                target = entity
                break
        
        # Cast the spell
        if spell.target_type == "self":
            target = self.player
        elif spell.target_type in ["single", "area"] and not target:
            # For area spells, we can target empty ground
            if spell.target_type != "area":
                self.add_message("No valid target at that location!", COLOR_RED)
                return
        
        # Execute spell
        result = self.player.cast_spell(spell.name, target, self)
        self.add_message(result, COLOR_PURPLE)
        
        # End targeting
        self.end_spell_targeting()
        
        # Trigger monster turns after spell casting
        self.monster_turns()

    def draw_ui(self):
        # Right Panel
        draw_tabs(self.screen, self.right_panel_tabs_rect, self.panel_tabs, self.active_panel, self.font, self.input_focus == 'panel')
        draw_panel(self.screen, self.right_panel_rect, border_color=COLOR_WHITE)
        
        if self.active_panel == CHARACTER_SHEET_ICON:
            draw_character_sheet_panel(self.screen, self.right_panel_rect, self.player, self.font)
        elif self.active_panel == EQUIPMENT_ICON:
            draw_equipment_panel(self.screen, self.right_panel_rect, self.player, self.equipment_selected_index, self.font)
        elif self.active_panel == INVENTORY_ICON:
            draw_inventory_panel(self.screen, self.right_panel_rect, self.player, self.inventory_selected_index, self.font)
        elif self.active_panel == SPELLS_ICON:
            draw_spells_panel(self.screen, self.right_panel_rect, self.player, self.spells_selected_index, self.font)
        elif self.active_panel == LOCATIONS_ICON:
            draw_locations_panel(self.screen, self.right_panel_rect, self.player, self.font)
        elif self.active_panel == QUESTS_ICON:
            draw_quests_panel(self.screen, self.right_panel_rect, self.player, self.quest_selected_index, self.font)

        # Log Panel
        draw_log_panel(self.screen, self.log_rect, self.message_log, self.log_scroll_offset, self.font, self.input_focus == 'log')
        
        # Game World Border
        if self.targeting_mode:
            border_color = COLOR_PURPLE
        elif self.input_focus == 'world':
            border_color = COLOR_FOCUS_BORDER
        else:
            border_color = COLOR_WHITE
        pygame.draw.rect(self.screen, border_color, self.game_rect, 2)

    def draw_game_world(self):
        self.game_surface.fill(COLOR_BLACK)
        cam_x = self.player.x - (self.game_rect.width // TILE_WIDTH // 2)
        cam_y = self.player.y - (self.game_rect.height // TILE_HEIGHT // 2)

        # Draw terrain
        for y in range(self.game_rect.height // TILE_HEIGHT):
            for x in range(self.game_rect.width // TILE_WIDTH):
                map_x, map_y = cam_x + x, cam_y + y
                if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                    tile = self.game_map[map_x, map_y]
                    
                    pygame.draw.rect(self.game_surface, tile.color, (x * TILE_WIDTH, y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))
                    
                    if tile.char != ' ':
                        glyph_color = tile.glyph_color if tile.glyph_color else COLOR_WHITE
                        if tile.is_gateway_to or tile.is_exit:
                            glyph_color = COLOR_GATEWAY
                        draw_text(self.game_surface, tile.char, x * TILE_WIDTH, y * TILE_HEIGHT, self.font, color=glyph_color)

        # Draw spell targeting overlays
        if self.targeting_mode:
            # Draw range indicators (red)
            for range_x, range_y in self.spell_range_tiles:
                if 0 <= range_x - cam_x < (self.game_rect.width // TILE_WIDTH) and \
                   0 <= range_y - cam_y < (self.game_rect.height // TILE_HEIGHT):
                    screen_x = (range_x - cam_x) * TILE_WIDTH
                    screen_y = (range_y - cam_y) * TILE_HEIGHT
                    draw_text(self.game_surface, "\uf0489", screen_x, screen_y, self.font, color=(240, 72, 137))  # Red glyph
            
            # Draw area of effect (yellow)
            for area_x, area_y in self.spell_area_tiles:
                if 0 <= area_x - cam_x < (self.game_rect.width // TILE_WIDTH) and \
                   0 <= area_y - cam_y < (self.game_rect.height // TILE_HEIGHT):
                    screen_x = (area_x - cam_x) * TILE_WIDTH
                    screen_y = (area_y - cam_y) * TILE_HEIGHT
                    draw_text(self.game_surface, "\uf0489", screen_x, screen_y, self.font, color=COLOR_GOLD)  # Yellow glyph
            
            # Draw targeting cursor (blue)
            cursor_x, cursor_y = self.target_cursor
            if 0 <= cursor_x - cam_x < (self.game_rect.width // TILE_WIDTH) and \
               0 <= cursor_y - cam_y < (self.game_rect.height // TILE_HEIGHT):
                screen_x = (cursor_x - cam_x) * TILE_WIDTH
                screen_y = (cursor_y - cam_y) * TILE_HEIGHT
                draw_text(self.game_surface, "\ue26d", screen_x, screen_y, self.font, color=COLOR_BLUE)  # Blue cursor

        # Draw entities
        for entity in sorted(self.all_entities, key=lambda e: isinstance(e, NPC)):
             if (hasattr(entity, 'hp') and entity.hp > 0) or not hasattr(entity, 'hp'):
                if 0 <= entity.x - cam_x < (self.game_rect.width // TILE_WIDTH) and \
                   0 <= entity.y - cam_y < (self.game_rect.height // TILE_HEIGHT):
                    draw_text(self.game_surface, entity.char, (entity.x - cam_x) * TILE_WIDTH, (entity.y - cam_y) * TILE_HEIGHT, self.font, color=entity.color)

        # Draw look cursor (only when not targeting)
        if self.game_state == 'looking' and not self.targeting_mode:
            cursor_x, cursor_y = self.look_cursor
            if 0 <= cursor_x - cam_x < (self.game_rect.width // TILE_WIDTH) and \
               0 <= cursor_y - cam_y < (self.game_rect.height // TILE_HEIGHT):
                screen_x = (cursor_x - cam_x) * TILE_WIDTH
                screen_y = (cursor_y - cam_y) * TILE_HEIGHT
                pygame.draw.rect(self.game_surface, COLOR_SELECTED, (screen_x, screen_y, TILE_WIDTH, TILE_HEIGHT), 2)

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        self.draw_game_world()
        self.draw_ui()
        self.screen.blit(self.game_surface, self.game_rect.topleft)
        
        if self.game_state == 'show_quest_details' and self.quest_details_window:
            quest_rect = pygame.Rect(0,0, 500, 350)
            quest_rect.center = self.screen.get_rect().center
            draw_quest_details_window(self.screen, quest_rect, self.quest_details_window, self.font)
        
        if self.game_state == 'level_up':
            level_up_rect = pygame.Rect(0,0, 400, 200)
            level_up_rect.center = self.screen.get_rect().center
            draw_level_up_window(self.screen, level_up_rect, self.font)

        if self.game_state == 'show_item_options':
            if self.player.display_inventory:
                item = self.player.display_inventory[self.inventory_selected_index]
                options = ["Use", "Drop"]
                item_options_rect = pygame.Rect(0,0, 250, 200)
                item_options_rect.center = self.screen.get_rect().center
                draw_item_options_window(self.screen, item_options_rect, item, options, self.item_options_selected_index, self.font)

        if self.game_state == 'select_item_to_equip':
            slot = list(self.player.equipment.keys())[self.equipment_selected_index]
            items = [item for item in self.player.inventory if hasattr(item, 'equip_slot') and item.equip_slot == slot]
            
            height = 150 + (len(items) * 60)
            equip_rect = pygame.Rect(0,0, 350, height)
            equip_rect.center = self.screen.get_rect().center
            draw_equipment_selection_window(self.screen, equip_rect, items, self.equip_selection_index, self.font)

        if self.game_state == 'pause_menu':
            pause_rect = pygame.Rect(0, 0, 300, 280)
            pause_rect.center = self.screen.get_rect().center
            draw_pause_menu_window(self.screen, pause_rect, self.pause_menu_selected_index, self.font)

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                # Handle targeting mode first
                if self.targeting_mode:
                    self.handle_targeting_input(event.key)
                    return
                
                # Handle pause menu
                if self.game_state == 'pause_menu':
                    self.handle_pause_menu_input(event.key)
                    return
                
                # Handle other pop-up states
                if self.game_state == 'level_up':
                    if event.key == pygame.K_RETURN: 
                        self.game_state = 'playing'
                    return
                
                if self.game_state == 'show_quest_details':
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'playing'
                        self.quest_details_window = None
                    return
                
                if self.game_state == 'show_item_options':
                    self.handle_item_options_input(event.key)
                    return
                
                if self.game_state == 'select_item_to_equip':
                    self.handle_equip_selection_input(event.key)
                    return

                # Main game escape handling
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == 'looking':
                        self.game_state = 'playing'
                        self.add_message("You stop looking around.")
                    elif self.game_state == 'playing':
                        self.game_state = 'pause_menu'
                        self.pause_menu_selected_index = 0
                
                if event.key == pygame.K_TAB:
                    if self.input_focus == 'world': 
                        self.input_focus = 'log'
                    elif self.input_focus == 'log': 
                        self.input_focus = 'panel'
                    else: 
                        self.input_focus = 'world'
                
                if self.input_focus == 'log':
                    if event.key == pygame.K_UP:
                        self.log_scroll_offset = min(self.log_scroll_offset + 1, len(self.message_log) -1)
                    if event.key == pygame.K_DOWN:
                        self.log_scroll_offset = max(self.log_scroll_offset - 1, 0)
                
                elif self.input_focus == 'panel':
                    self.handle_panel_input(event.key)

                elif self.input_focus == 'world':
                    if self.game_state == 'looking':
                        if event.key == pygame.K_RETURN:
                            self.handle_interaction()

                    if event.key == pygame.K_l:
                        self.game_state = 'looking' if self.game_state == 'playing' else 'playing'
                        if self.game_state == 'looking':
                            self.look_cursor = (self.player.x, self.player.y)
                            self.add_message("You look around. (ENTER to interact)", COLOR_SELECTED)
                        else:
                            self.add_message("You stop looking around.")
                    
                    # CFE Rest command
                    if event.key == pygame.K_r:
                        rest_msg = self.player.rest()
                        self.add_message(rest_msg, COLOR_BLUE)

    def handle_targeting_input(self, key):
        """Handle input during spell targeting mode."""
        if key == pygame.K_ESCAPE:
            self.end_spell_targeting()
            self.add_message("Spell targeting cancelled.", COLOR_GREY)
            return
        
        if key == pygame.K_RETURN:
            # Check if target is in valid range
            if self.target_cursor in self.spell_range_tiles:
                self.cast_targeted_spell()
            else:
                self.add_message("Target is out of range!", COLOR_RED)
            return
        
        # Move targeting cursor
        dx, dy = 0, 0
        if key == pygame.K_UP: dy = -1
        elif key == pygame.K_DOWN: dy = 1
        elif key == pygame.K_LEFT: dx = -1
        elif key == pygame.K_RIGHT: dx = 1
        
        if dx != 0 or dy != 0:
            new_x = max(0, min(self.map_width - 1, self.target_cursor[0] + dx))
            new_y = max(0, min(self.map_height - 1, self.target_cursor[1] + dy))
            self.target_cursor = (new_x, new_y)
            
            # Update area of effect
            self.update_spell_area()

    def handle_pause_menu_input(self, key):
        """Handles input for the pause menu."""
        pause_options = ["Resume", "Save Game", "Load Game", "Quit to Title"]
        
        if key == pygame.K_UP:
            self.pause_menu_selected_index = max(0, self.pause_menu_selected_index - 1)
        elif key == pygame.K_DOWN:
            self.pause_menu_selected_index = min(len(pause_options) - 1, self.pause_menu_selected_index + 1)
        elif key == pygame.K_ESCAPE:
            self.game_state = 'playing'
        elif key == pygame.K_RETURN:
            selected_option = pause_options[self.pause_menu_selected_index]
            
            if selected_option == "Resume":
                self.game_state = 'playing'
            elif selected_option == "Save Game":
                message = self.save_game()
                self.add_message(message, COLOR_GOLD)
                self.game_state = 'playing'
            elif selected_option == "Load Game":
                message = self.load_game()
                self.add_message(message, COLOR_GOLD)
                self.game_state = 'playing'
            elif selected_option == "Quit to Title":
                self.running = False

    def handle_panel_input(self, key):
        """Handles input when the side panel is focused."""
        current_index = self.panel_tabs.index(self.active_panel)
        if key == pygame.K_RIGHT:
            new_index = (current_index + 1) % len(self.panel_tabs)
            self.active_panel = self.panel_tabs[new_index]
        if key == pygame.K_LEFT:
            new_index = (current_index - 1) % len(self.panel_tabs)
            self.active_panel = self.panel_tabs[new_index]
        
        if self.active_panel == INVENTORY_ICON:
            inventory = self.player.display_inventory
            if inventory:
                if key == pygame.K_UP:
                    self.inventory_selected_index = max(0, self.inventory_selected_index - 1)
                if key == pygame.K_DOWN:
                    self.inventory_selected_index = min(len(inventory) - 1, self.inventory_selected_index + 1)
                if key == pygame.K_RETURN:
                    self.game_state = 'show_item_options'
                    self.item_options_selected_index = 0
        
        elif self.active_panel == EQUIPMENT_ICON:
            if key == pygame.K_UP:
                self.equipment_selected_index = max(0, self.equipment_selected_index - 1)
            if key == pygame.K_DOWN:
                self.equipment_selected_index = min(len(self.player.equipment) - 1, self.equipment_selected_index + 1)
            if key == pygame.K_RETURN:
                 self.game_state = 'select_item_to_equip'
                 self.equip_selection_index = 0
        
        elif self.active_panel == SPELLS_ICON and self.player.archetype == "Mage":
            # Handle spell preparation and casting
            if hasattr(self.player, 'known_spells'):
                all_spells = list(self.player.known_spells)
                if all_spells:
                    if key == pygame.K_UP:
                        self.spells_selected_index = max(0, self.spells_selected_index - 1)
                    if key == pygame.K_DOWN:
                        self.spells_selected_index = min(len(all_spells) - 1, self.spells_selected_index + 1)
                    if key == pygame.K_RETURN:
                        # Prepare selected spell
                        spell_name = all_spells[self.spells_selected_index]
                        spell = get_spell_by_name(spell_name)
                        if spell:
                            result = self.player.prepare_spell(spell_name, spell.level)
                            self.add_message(result, COLOR_BLUE)
                    if key == pygame.K_c:
                        # Cast selected spell
                        spell_name = all_spells[self.spells_selected_index]
                        self.cast_spell_from_panel(spell_name)
        
        elif self.active_panel == QUESTS_ICON:
            active_quests = sorted(self.player.quest_log.active_quests.keys())
            if active_quests:
                if key == pygame.K_UP:
                    self.quest_selected_index = max(0, self.quest_selected_index - 1)
                if key == pygame.K_DOWN:
                    self.quest_selected_index = min(len(active_quests) - 1, self.quest_selected_index + 1)
                if key == pygame.K_RETURN:
                    quest_name = active_quests[self.quest_selected_index]
                    self.quest_details_window = self.player.quest_log.active_quests[quest_name]
                    self.game_state = 'show_quest_details'

    def cast_spell_from_panel(self, spell_name):
        """Cast a spell from the spells panel."""
        spell = get_spell_by_name(spell_name)
        if not spell:
            self.add_message(f"Unknown spell: {spell_name}!", COLOR_RED)
            return
        
        # Check if spell is prepared
        if spell_name not in self.player.prepared_spells.get(spell.level, []):
            self.add_message(f"{spell_name} is not prepared!", COLOR_RED)
            return
        
        # Check if we have spell slots
        if self.player.spell_slots.get(spell.level, 0) <= 0:
            self.add_message("No spell slots remaining for that level!", COLOR_RED)
            return
        
        # Handle different target types
        if spell.target_type == "self":
            # Cast immediately on self
            result = self.player.cast_spell(spell_name, self.player, self)
            self.add_message(result, COLOR_PURPLE)
            self.monster_turns()
        else:
            # Enter targeting mode
            self.start_spell_targeting(spell_name)

    def handle_item_options_input(self, key):
        """Handles input for the item options pop-up."""
        if not self.player.display_inventory:
            self.game_state = 'playing'
            return
            
        item_to_use = self.player.display_inventory[self.inventory_selected_index]
        options = ["Use", "Drop"]
        
        if key == pygame.K_UP:
            self.item_options_selected_index = max(0, self.item_options_selected_index - 1)
        if key == pygame.K_DOWN:
            self.item_options_selected_index = min(len(options) - 1, self.item_options_selected_index + 1)
        if key == pygame.K_ESCAPE:
            self.game_state = 'playing'
        if key == pygame.K_RETURN:
            selected_option = options[self.item_options_selected_index]
            if selected_option == "Use":
                self.add_message(self.player.use_item(item_to_use))
            elif selected_option == "Drop":
                self.player.inventory.remove(item_to_use)
                self.add_message(f"You drop the {item_to_use.name}.")
            self.game_state = 'playing'

    def handle_equip_selection_input(self, key):
        """Handles input for the equipment selection window."""
        slot = list(self.player.equipment.keys())[self.equipment_selected_index]
        items = [item for item in self.player.inventory if hasattr(item, 'equip_slot') and item.equip_slot == slot]

        if key == pygame.K_UP:
            self.equip_selection_index = max(0, self.equip_selection_index - 1)
        if key == pygame.K_DOWN:
            self.equip_selection_index = min(len(items) - 1, self.equip_selection_index + 1)
        if key == pygame.K_ESCAPE:
            self.game_state = 'playing'
        if key == pygame.K_RETURN and items:
            item_to_equip = items[self.equip_selection_index]
            self.add_message(self.player.equip(item_to_equip))
            self.game_state = 'playing'

    def handle_interaction(self):
        x, y = self.look_cursor
        if math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2) > 1.5:
            self.add_message("You are too far away.", COLOR_GREY)
            return

        target_npc = next((e for e in self.all_entities if isinstance(e, NPC) and e.x == x and e.y == y), None)
        if target_npc:
            self.add_message(f"{target_npc.name}: '{target_npc.dialogue}'", COLOR_NPC)
            if target_npc.quest:
                quest_message = self.player.quest_log.add_quest(target_npc.quest)
                if quest_message:
                    self.add_message(quest_message, COLOR_GOLD)
            return

        # Check for treasure
        tile = self.game_map[x, y]
        if tile.is_interactive:
            if tile.name == "a chest":
                from items import create_random_treasure
                treasure_item, value = create_random_treasure((25, 100))
                self.player.inventory.append(treasure_item)
                self.player.gold += value
                
                treasure_xp_msg = self.player.gain_treasure_xp(value)
                self.add_message(f"You open the chest and find {treasure_item.name}!", COLOR_GOLD)
                self.add_message(treasure_xp_msg, COLOR_GOLD)
                
                if self.player.check_for_level_up():
                    self.game_state = 'level_up'
                
                self.game_map[x, y] = Tile(False, ' ', tile.color, "an empty chest")
            return

        self.add_message("There is nothing to interact with there.", COLOR_GREY)

    def handle_continuous_movement(self):
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

    def handle_look_cursor(self):
        if self.input_focus != 'world' or self.game_state != 'looking': 
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
                new_x, new_y = self.look_cursor[0] + dx, self.look_cursor[1] + dy
                if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
                    self.look_cursor = (new_x, new_y)
                    self.get_tile_info(new_x, new_y)
                    self.last_move_time = current_time

    def get_tile_info(self, x, y):
        for entity in self.all_entities:
            if entity.x == x and entity.y == y and entity is not self.player:
                hp_info = f" ({entity.hp}/{getattr(entity, 'max_hp', entity.hp)} HP)" if hasattr(entity, 'hp') else ""
                self.add_message(f"You see {entity.name}{hp_info}.", entity.color)
                return
        tile = self.game_map[x, y]
        self.add_message(f"You see {tile.name}.", tile.color)

    def check_for_level_up(self):
        if self.player.check_for_level_up():
            self.game_state = 'level_up'
            level_up_msg = self.player.level_up()
            self.add_message(level_up_msg, COLOR_GOLD)

    def player_move_or_attack(self, dx, dy):
        """Handle player movement with bump-to-attack combat."""
        new_x, new_y = self.player.x + dx, self.player.y + dy
        if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
            target = next((e for e in self.all_entities if isinstance(e, Monster) and e.x == new_x and e.y == new_y and e.hp > 0), None)
            if target:
                # Bump-to-attack: attack the monster
                attack_result = self.player.attack(target)
                self.add_message(attack_result, COLOR_BLUE)
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
        # Remove dead entities
        self.all_entities = [e for e in self.all_entities if not (hasattr(e, 'hp') and e.hp <= 0)]
        
        for entity in self.all_entities:
            if entity is not self.player and hasattr(entity, 'hp'):
                message = entity.take_turn(self.player, self.game_map, self.all_entities)
                if message: 
                    self.add_message(message, COLOR_RED)
                
                if self.player.hp <= 0:
                    self.game_state = 'game_over'
                    self.add_message("You have died!", COLOR_RED)
                    self.running = False
                    break

    def run(self):
        """Main game loop."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_input()
            self.handle_continuous_movement()
            self.handle_look_cursor()
            self.draw()