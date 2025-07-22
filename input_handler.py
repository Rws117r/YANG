# input_handler.py - Updated with Music Controls
import pygame
from config import *

class InputHandler:
    """Handles all input for the game with music support."""
    
    def __init__(self, game):
        self.game = game
    
    def handle_event(self, event):
        """Handle a single pygame event."""
        if event.type != pygame.KEYDOWN:
            return
        
        # Handle targeting mode first
        if self.game.targeting_mode:
            self._handle_targeting_input(event.key)
            return
        
        # Handle different game states
        if self.game.game_state == 'pause_menu':
            self._handle_pause_menu_input(event.key)
        elif self.game.game_state == 'level_up':
            if event.key == pygame.K_RETURN:
                self.game.game_state = 'playing'
        elif self.game.game_state == 'show_item_options':
            self._handle_item_options_input(event.key)
        elif self.game.game_state == 'select_item_to_equip':
            self._handle_equip_selection_input(event.key)
        elif self.game.game_state == 'show_quest_details':
            if event.key == pygame.K_ESCAPE:
                self.game.game_state = 'playing'
                self.game.quest_details_window = None
        elif self.game.game_state == 'playing':
            self._handle_playing_input(event.key)
        elif self.game.game_state == 'looking':
            self._handle_looking_input(event.key)
    
    def _handle_playing_input(self, key):
        """Handle input during normal play."""
        # Global commands
        if key == pygame.K_ESCAPE:
            self.game.game_state = 'pause_menu'
            self.game.pause_menu_selected_index = 0
            # Pause music when entering pause menu
            self.game.pause_game_music()
        elif key == pygame.K_TAB:
            self._cycle_input_focus()
        elif key == pygame.K_l:
            self.game.game_state = 'looking'
            self.game.look_cursor = (self.game.player.x, self.game.player.y)
            self.game.add_message("You look around. (ENTER to interact)", COLOR_SELECTED)
        elif key == pygame.K_r:
            rest_msg = self.game.player.rest()
            self.game.add_message(rest_msg, COLOR_BLUE)
        elif key == pygame.K_m:
            # Toggle music on/off
            if self.game.music_manager:
                enabled = self.game.music_manager.toggle_music()
                status = "enabled" if enabled else "disabled"
                self.game.add_message(f"Music {status}", COLOR_BLUE)
        
        # Focus-specific input
        if self.game.input_focus == 'log':
            self._handle_log_input(key)
        elif self.game.input_focus == 'panel':
            self._handle_panel_input(key)
        # World input is handled by continuous movement
    
    def _handle_looking_input(self, key):
        """Handle input during look mode."""
        if key == pygame.K_ESCAPE:
            self.game.game_state = 'playing'
            self.game.add_message("You stop looking around.")
        elif key == pygame.K_RETURN:
            self._handle_interaction()
        elif key == pygame.K_l:
            self.game.game_state = 'playing'
            self.game.add_message("You stop looking around.")
        else:
            # Handle look cursor movement with arrow keys
            dx, dy = 0, 0
            if key == pygame.K_UP: dy = -1
            elif key == pygame.K_DOWN: dy = 1
            elif key == pygame.K_LEFT: dx = -1
            elif key == pygame.K_RIGHT: dx = 1
            
            if dx != 0 or dy != 0:
                current_time = pygame.time.get_ticks()
                if current_time - self.game.last_move_time > self.game.move_delay:
                    new_x = max(0, min(self.game.map_width - 1, self.game.look_cursor[0] + dx))
                    new_y = max(0, min(self.game.map_height - 1, self.game.look_cursor[1] + dy))
                    self.game.look_cursor = (new_x, new_y)
                    self._get_tile_info(new_x, new_y)
                    self.game.last_move_time = current_time
    
    def _handle_targeting_input(self, key):
        """Handle input during spell targeting mode."""
        if key == pygame.K_ESCAPE:
            self._end_spell_targeting()
            self.game.add_message("Spell targeting cancelled.", COLOR_GREY)
        elif key == pygame.K_RETURN:
            if self.game.target_cursor in self.game.spell_range_tiles:
                self._cast_targeted_spell()
            else:
                self.game.add_message("Target is out of range!", COLOR_RED)
        else:
            # Move targeting cursor
            dx, dy = 0, 0
            if key == pygame.K_UP: dy = -1
            elif key == pygame.K_DOWN: dy = 1
            elif key == pygame.K_LEFT: dx = -1
            elif key == pygame.K_RIGHT: dx = 1
            
            if dx != 0 or dy != 0:
                new_x = max(0, min(self.game.map_width - 1, self.game.target_cursor[0] + dx))
                new_y = max(0, min(self.game.map_height - 1, self.game.target_cursor[1] + dy))
                self.game.target_cursor = (new_x, new_y)
                self._update_spell_area()
    
    def _handle_pause_menu_input(self, key):
        """Handle pause menu input with music controls."""
        pause_options = ["Resume", "Music Volume", "Save Game", "Load Game", "Quit to Title"]
        
        if key == pygame.K_UP:
            self.game.pause_menu_selected_index = max(0, self.game.pause_menu_selected_index - 1)
        elif key == pygame.K_DOWN:
            self.game.pause_menu_selected_index = min(len(pause_options) - 1, self.game.pause_menu_selected_index + 1)
        elif key == pygame.K_ESCAPE:
            self.game.game_state = 'playing'
            # Resume music when exiting pause menu
            self.game.resume_game_music()
        elif key == pygame.K_RETURN:
            selected_option = pause_options[self.game.pause_menu_selected_index]
            
            if selected_option == "Resume":
                self.game.game_state = 'playing'
                # Resume music when resuming game
                self.game.resume_game_music()
            elif selected_option == "Music Volume":
                # Cycle through volume levels
                if self.game.music_manager:
                    current_vol = self.game.music_manager.music_volume
                    volume_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
                    try:
                        current_index = volume_levels.index(round(current_vol, 1))
                        new_index = (current_index + 1) % len(volume_levels)
                    except ValueError:
                        new_index = 3  # Default to 0.6
                    
                    new_vol = volume_levels[new_index]
                    self.game.music_manager.set_volume(new_vol)
                    self.game.add_message(f"Music volume: {int(new_vol * 100)}%", COLOR_BLUE)
            elif selected_option == "Save Game":
                message = self.game.save_game()
                self.game.add_message(message, COLOR_GOLD)
                self.game.game_state = 'playing'
                self.game.resume_game_music()
            elif selected_option == "Load Game":
                message = self.game.load_game()
                self.game.add_message(message, COLOR_GOLD)
                self.game.game_state = 'playing'
                # Music will be set based on loaded location
                if self.game.music_manager:
                    self.game.change_music_for_area("Overworld", "overworld")
            elif selected_option == "Quit to Title":
                self.game.running = False
    
    def _handle_log_input(self, key):
        """Handle log panel input."""
        if key == pygame.K_UP:
            self.game.log_scroll_offset = min(self.game.log_scroll_offset + 1, len(self.game.message_log) - 1)
        elif key == pygame.K_DOWN:
            self.game.log_scroll_offset = max(self.game.log_scroll_offset - 1, 0)
    
    def _handle_panel_input(self, key):
        """Handle side panel input."""
        # Tab navigation
        current_index = self.game.panel_tabs.index(self.game.active_panel)
        if key == pygame.K_RIGHT:
            new_index = (current_index + 1) % len(self.game.panel_tabs)
            self.game.active_panel = self.game.panel_tabs[new_index]
            # Play panel switch sound
            if self.game.audio_manager:
                self.game.audio_manager.play_panel_switch()
        elif key == pygame.K_LEFT:
            new_index = (current_index - 1) % len(self.game.panel_tabs)
            self.game.active_panel = self.game.panel_tabs[new_index]
            # Play panel switch sound
            if self.game.audio_manager:
                self.game.audio_manager.play_panel_switch()
        
        # Panel-specific input
        if self.game.active_panel == INVENTORY_ICON:
            self._handle_inventory_input(key)
        elif self.game.active_panel == EQUIPMENT_ICON:
            self._handle_equipment_input(key)
        elif self.game.active_panel == SPELLS_ICON:
            self._handle_spells_input(key)
        elif self.game.active_panel == QUESTS_ICON:
            self._handle_quests_input(key)
    
    def _handle_inventory_input(self, key):
        """Handle inventory panel input."""
        inventory = self.game.player.display_inventory
        if not inventory:
            return
        
        if key == pygame.K_UP:
            self.game.inventory_selected_index = max(0, self.game.inventory_selected_index - 1)
        elif key == pygame.K_DOWN:
            self.game.inventory_selected_index = min(len(inventory) - 1, self.game.inventory_selected_index + 1)
        elif key == pygame.K_RETURN:
            self.game.game_state = 'show_item_options'
            self.game.item_options_selected_index = 0
    
    def _handle_equipment_input(self, key):
        """Handle equipment panel input."""
        if key == pygame.K_UP:
            self.game.equipment_selected_index = max(0, self.game.equipment_selected_index - 1)
        elif key == pygame.K_DOWN:
            self.game.equipment_selected_index = min(len(self.game.player.equipment) - 1, self.game.equipment_selected_index + 1)
        elif key == pygame.K_RETURN:
            self.game.game_state = 'select_item_to_equip'
            self.game.equip_selection_index = 0
    
    def _handle_spells_input(self, key):
        """Handle spells panel input."""
        if self.game.player.archetype != "Mage":
            return
        
        if hasattr(self.game.player, 'known_spells'):
            all_spells = list(self.game.player.known_spells)
            if not all_spells:
                return
            
            if key == pygame.K_UP:
                self.game.spells_selected_index = max(0, self.game.spells_selected_index - 1)
            elif key == pygame.K_DOWN:
                self.game.spells_selected_index = min(len(all_spells) - 1, self.game.spells_selected_index + 1)
            elif key == pygame.K_RETURN:
                # Prepare selected spell
                spell_name = all_spells[self.game.spells_selected_index]
                from spells import get_spell_by_name
                spell = get_spell_by_name(spell_name)
                if spell:
                    result = self.game.player.prepare_spell(spell_name, spell.level)
                    self.game.add_message(result, COLOR_BLUE)
                    # Play spell prepare sound
                    if self.game.audio_manager:
                        self.game.audio_manager.play_spell_prepare()
            elif key == pygame.K_c:
                # Cast selected spell
                spell_name = all_spells[self.game.spells_selected_index]
                self._cast_spell_from_panel(spell_name)
    
    def _handle_quests_input(self, key):
        """Handle quests panel input."""
        active_quests = sorted(self.game.player.quest_log.active_quests.keys())
        if not active_quests:
            return
        
        if key == pygame.K_UP:
            self.game.quest_selected_index = max(0, self.game.quest_selected_index - 1)
        elif key == pygame.K_DOWN:
            self.game.quest_selected_index = min(len(active_quests) - 1, self.game.quest_selected_index + 1)
        elif key == pygame.K_RETURN:
            quest_name = active_quests[self.game.quest_selected_index]
            self.game.quest_details_window = self.game.player.quest_log.active_quests[quest_name]
            self.game.game_state = 'show_quest_details'
    
    def _cycle_input_focus(self):
        """Cycle through input focus modes."""
        if self.game.input_focus == 'world':
            self.game.input_focus = 'log'
        elif self.game.input_focus == 'log':
            self.game.input_focus = 'panel'
        else:
            self.game.input_focus = 'world'
    
    def _get_tile_info(self, x, y):
        """Get information about a tile and display it."""
        # Check for entities first
        for entity in self.game.all_entities:
            if entity.x == x and entity.y == y and entity is not self.game.player:
                hp_info = f" ({entity.hp}/{getattr(entity, 'max_hp', entity.hp)} HP)" if hasattr(entity, 'hp') else ""
                self.game.add_message(f"You see {entity.name}{hp_info}.", entity.color)
                return
        
        # If no entity, show tile info
        tile = self.game.game_map[x, y]
        self.game.add_message(f"You see {tile.name}.", tile.color)

    def _handle_interaction(self):
        """Handle interaction at look cursor position."""
        x, y = self.game.look_cursor
        import math
        if math.sqrt((x - self.game.player.x)**2 + (y - self.game.player.y)**2) > 1.5:
            self.game.add_message("You are too far away.", COLOR_GREY)
            return

        from entities import NPC
        target_npc = next((e for e in self.game.all_entities 
                          if isinstance(e, NPC) and e.x == x and e.y == y), None)
        if target_npc:
            self.game.add_message(f"{target_npc.name}: '{target_npc.dialogue}'", COLOR_NPC)
            if target_npc.quest:
                quest_message = self.game.player.quest_log.add_quest(target_npc.quest)
                if quest_message:
                    self.game.add_message(quest_message, COLOR_GOLD)
            return

        # Check for treasure
        tile = self.game.game_map[x, y]
        if tile.is_interactive:
            if tile.name == "a chest":
                from items import create_random_treasure
                from world_generation import Tile
                treasure_item, value = create_random_treasure((25, 100))
                self.game.player.inventory.append(treasure_item)
                self.game.player.gold += value
                
                treasure_xp_msg = self.game.player.gain_treasure_xp(value)
                self.game.add_message(f"You open the chest and find {treasure_item.name}!", COLOR_GOLD)
                self.game.add_message(treasure_xp_msg, COLOR_GOLD)
                
                # Play item pickup sound
                if self.game.audio_manager:
                    self.game.audio_manager.play_item_pickup()
                
                if self.game.player.check_for_level_up():
                    self.game.game_state = 'level_up'
                
                self.game.game_map[x, y] = Tile(False, ' ', tile.color, "an empty chest")
            return

        self.game.add_message("There is nothing to interact with there.", COLOR_GREY)
    
    def _cast_spell_from_panel(self, spell_name):
        """Cast a spell from the spells panel."""
        from spells import get_spell_by_name
        spell = get_spell_by_name(spell_name)
        if not spell:
            self.game.add_message(f"Unknown spell: {spell_name}!", COLOR_RED)
            if self.game.audio_manager:
                self.game.audio_manager.play_error()
            return
        
        # Check if spell is prepared
        if spell_name not in self.game.player.prepared_spells.get(spell.level, []):
            self.game.add_message(f"{spell_name} is not prepared!", COLOR_RED)
            if self.game.audio_manager:
                self.game.audio_manager.play_error()
            return
        
        # Check if we have spell slots
        if self.game.player.spell_slots.get(spell.level, 0) <= 0:
            self.game.add_message("No spell slots remaining for that level!", COLOR_RED)
            if self.game.audio_manager:
                self.game.audio_manager.play_error()
            return
        
        # Handle different target types
        if spell.target_type == "self":
            # Cast immediately on self
            result = self.game.player.cast_spell(spell_name, self.game.player, self.game)
            self.game.add_message(result, COLOR_PURPLE)
            
            # Play spell sound
            if self.game.audio_manager:
                self.game.audio_manager.play_spell_sound(spell_name)
            
            from game_systems import get_hitstop_duration
            self.game.hitstop_manager.freeze_game(get_hitstop_duration("Mage", spell_name))
            self.game.monster_turns()
        else:
            # Enter targeting mode
            self._start_spell_targeting(spell_name)
    
    def _start_spell_targeting(self, spell_name):
        """Start spell targeting mode."""
        from spells import get_spell_by_name
        spell = get_spell_by_name(spell_name)
        if not spell:
            return
        
        self.game.targeting_mode = True
        self.game.targeting_spell = spell
        self.game.target_cursor = (self.game.player.x, self.game.player.y)
        
        # Calculate valid targeting areas
        self._calculate_spell_targeting(spell)
        
        self.game.add_message(f"Targeting {spell_name}. Use arrows to aim, ENTER to cast, ESC to cancel.", COLOR_PURPLE)
    
    def _calculate_spell_targeting(self, spell):
        """Calculate valid targeting tiles for the spell."""
        self.game.spell_range_tiles = []
        self.game.spell_area_tiles = []
        
        # Calculate range (convert feet to tiles, roughly 5 feet per tile)
        spell_range = spell.range // 5 if spell.range else 1
        if spell.target_type == "self":
            spell_range = 0
        elif spell.target_type == "touch":
            spell_range = 1
        
        # Calculate all tiles within range
        import math
        for x in range(max(0, self.game.player.x - spell_range), 
                      min(self.game.map_width, self.game.player.x + spell_range + 1)):
            for y in range(max(0, self.game.player.y - spell_range), 
                          min(self.game.map_height, self.game.player.y + spell_range + 1)):
                distance = math.sqrt((x - self.game.player.x)**2 + (y - self.game.player.y)**2)
                if distance <= spell_range:
                    self.game.spell_range_tiles.append((x, y))
        
        # Calculate area of effect around target cursor
        self._update_spell_area()
    
    def _update_spell_area(self):
        """Update area of effect tiles around the target cursor."""
        self.game.spell_area_tiles = []
        
        if not self.game.targeting_spell:
            return
        
        # Area of effect radius (simplified)
        if self.game.targeting_spell.target_type == "area":
            if self.game.targeting_spell.name == "Fireball":
                radius = 2  # 20 foot radius = roughly 4 tiles diameter
            else:
                radius = 1  # Default small area
                
            cx, cy = self.game.target_cursor
            import math
            for x in range(max(0, cx - radius), min(self.game.map_width, cx + radius + 1)):
                for y in range(max(0, cy - radius), min(self.game.map_height, cy + radius + 1)):
                    distance = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if distance <= radius:
                        self.game.spell_area_tiles.append((x, y))
    
    def _end_spell_targeting(self):
        """End targeting mode."""
        self.game.targeting_mode = False
        self.game.targeting_spell = None
        self.game.spell_range_tiles = []
        self.game.spell_area_tiles = []
    
    def _cast_targeted_spell(self):
        """Cast the currently targeted spell."""
        if not self.game.targeting_spell:
            return
        
        spell = self.game.targeting_spell
        target = None
        
        # Find target at cursor position
        from entities import Monster
        for entity in self.game.all_entities:
            if (entity.x == self.game.target_cursor[0] and 
                entity.y == self.game.target_cursor[1] and 
                entity != self.game.player):
                target = entity
                break
        
        # Cast the spell
        if spell.target_type == "self":
            target = self.game.player
        elif spell.target_type in ["single", "area"] and not target:
            # For area spells, we can target empty ground
            if spell.target_type != "area":
                self.game.add_message("No valid target at that location!", COLOR_RED)
                return
        
        # Execute spell
        result = self.game.player.cast_spell(spell.name, target, self.game)
        self.game.add_message(result, COLOR_PURPLE)
        
        # Trigger visual effects for damaging spells
        if target and hasattr(target, 'hp') and ("damage" in result or "hits" in result):
            print(f"[VFX] Spell {spell.name} hit target - triggering effects")
            self.game.trigger_hit_effects(target, "Mage", spell.name, self.game.player.x, self.game.player.y)
        
        # End targeting
        self._end_spell_targeting()
        
        # Trigger monster turns
        self.game.monster_turns()

    def _handle_item_options_input(self, key):
        """Handle input for the item options pop-up."""
        if not self.game.player.display_inventory:
            self.game.game_state = 'playing'
            return
        
        # Make sure we have a valid selection
        if self.game.inventory_selected_index >= len(self.game.player.display_inventory):
            self.game.game_state = 'playing'
            return
            
        item_to_use = self.game.player.display_inventory[self.game.inventory_selected_index]
        options = ["Use", "Drop"]
        
        if key == pygame.K_UP:
            self.game.item_options_selected_index = max(0, self.game.item_options_selected_index - 1)
        elif key == pygame.K_DOWN:
            self.game.item_options_selected_index = min(len(options) - 1, self.game.item_options_selected_index + 1)
        elif key == pygame.K_ESCAPE:
            self.game.game_state = 'playing'
            # Play cancel sound
            if self.game.audio_manager:
                self.game.audio_manager.play_error()
        elif key == pygame.K_RETURN:
            selected_option = options[self.game.item_options_selected_index]
            print(f"[DEBUG] Using item option: {selected_option} on {item_to_use.name}")
            
            if selected_option == "Use":
                result = self.game.player.use_item(item_to_use)
                self.game.add_message(result, COLOR_WHITE)
                # Play item use sound
                if self.game.audio_manager:
                    if "healing" in result.lower():
                        self.game.audio_manager.play_success()
                    else:
                        self.game.audio_manager.play_item_pickup()
                        
            elif selected_option == "Drop":
                if item_to_use in self.game.player.inventory:
                    self.game.player.inventory.remove(item_to_use)
                    self.game.add_message(f"You drop the {item_to_use.name}.", COLOR_WHITE)
                    # Play drop sound (use error sound for negative action)
                    if self.game.audio_manager:
                        self.game.audio_manager.play_error()
                else:
                    self.game.add_message("Item not found in inventory.", COLOR_RED)
                    if self.game.audio_manager:
                        self.game.audio_manager.play_error()
            
            self.game.game_state = 'playing'

    def _handle_equip_selection_input(self, key):
        """Handle input for the equipment selection window."""
        if self.game.equipment_selected_index >= len(self.game.player.equipment):
            self.game.game_state = 'playing'
            return
            
        slot = list(self.game.player.equipment.keys())[self.game.equipment_selected_index]
        items = [item for item in self.game.player.inventory 
                if hasattr(item, 'equip_slot') and item.equip_slot == slot]

        if key == pygame.K_UP:
            self.game.equip_selection_index = max(0, self.game.equip_selection_index - 1)
        elif key == pygame.K_DOWN:
            self.game.equip_selection_index = min(max(0, len(items) - 1), self.game.equip_selection_index + 1)
        elif key == pygame.K_ESCAPE:
            self.game.game_state = 'playing'
        elif key == pygame.K_RETURN and items and self.game.equip_selection_index < len(items):
            item_to_equip = items[self.game.equip_selection_index]
            result = self.game.player.equip(item_to_equip)
            self.game.add_message(result, COLOR_WHITE)
            # Play success sound for successful equipment
            if self.game.audio_manager:
                if "equip" in result.lower():
                    self.game.audio_manager.play_success()
                else:
                    self.game.audio_manager.play_error()
            self.game.game_state = 'playing'