# rendering.py - Handles all game rendering with visual effects
import pygame
from config import *
from ui import *
from game_systems import apply_flash_to_color

class GameRenderer:
    """Handles all rendering for the game with visual effects support."""
    
    def __init__(self, screen, font, vfx_manager):
        self.screen = screen
        self.font = font
        self.vfx_manager = vfx_manager
        self.game_surface = pygame.Surface((860, 540))  # Game area surface
    
    def draw_game(self, game_map, all_entities, player, map_width, map_height, 
                  game_rect, is_frozen=False, **kwargs):
        """Draw the main game world with visual effects."""
        self.game_surface.fill(COLOR_BLACK)
        
        # Calculate camera position
        cam_x = player.x - (game_rect.width // TILE_WIDTH // 2)
        cam_y = player.y - (game_rect.height // TILE_HEIGHT // 2)
        
        # Draw terrain
        self._draw_terrain(game_map, map_width, map_height, cam_x, cam_y, game_rect)
        
        # Draw spell targeting overlays if in targeting mode
        if kwargs.get('targeting_mode', False):
            self._draw_targeting_overlays(kwargs, cam_x, cam_y, game_rect)
        
        # Draw entities with visual effects
        self._draw_entities(all_entities, player, cam_x, cam_y, game_rect)
        
        # Draw look cursor
        if kwargs.get('game_state') == 'looking' and not kwargs.get('targeting_mode', False):
            self._draw_look_cursor(kwargs.get('look_cursor'), cam_x, cam_y, game_rect)
        
        # Draw game border with hitstop feedback
        border_color = COLOR_WHITE if is_frozen else COLOR_FOCUS_BORDER
        border_width = 4 if is_frozen else 2
        pygame.draw.rect(self.screen, border_color, game_rect, border_width)
        
        # Blit game surface to main screen
        self.screen.blit(self.game_surface, game_rect.topleft)
        
        # Draw hitstop indicator
        if is_frozen:
            hitstop_text = "HITSTOP ACTIVE"
            text_surface = self.font.render(hitstop_text, True, COLOR_WHITE)
            self.screen.blit(text_surface, (game_rect.left + 10, game_rect.top + 10))
    
    def _draw_terrain(self, game_map, map_width, map_height, cam_x, cam_y, game_rect):
        """Draw the terrain tiles."""
        for y in range(game_rect.height // TILE_HEIGHT):
            for x in range(game_rect.width // TILE_WIDTH):
                map_x, map_y = cam_x + x, cam_y + y
                if 0 <= map_x < map_width and 0 <= map_y < map_height:
                    tile = game_map[map_x, map_y]
                    
                    # Draw tile background
                    pygame.draw.rect(self.game_surface, tile.color, 
                                   (x * TILE_WIDTH, y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))
                    
                    # Draw tile character
                    if tile.char != ' ':
                        glyph_color = tile.glyph_color if tile.glyph_color else COLOR_WHITE
                        if tile.is_gateway_to or tile.is_exit:
                            glyph_color = COLOR_GATEWAY
                        draw_text(self.game_surface, tile.char, x * TILE_WIDTH, y * TILE_HEIGHT, 
                                self.font, color=glyph_color)
    
    def _draw_targeting_overlays(self, kwargs, cam_x, cam_y, game_rect):
        """Draw spell targeting overlays."""
        spell_range_tiles = kwargs.get('spell_range_tiles', [])
        spell_area_tiles = kwargs.get('spell_area_tiles', [])
        target_cursor = kwargs.get('target_cursor', (0, 0))
        
        # Draw range indicators (red)
        for range_x, range_y in spell_range_tiles:
            if 0 <= range_x - cam_x < (game_rect.width // TILE_WIDTH) and \
               0 <= range_y - cam_y < (game_rect.height // TILE_HEIGHT):
                screen_x = (range_x - cam_x) * TILE_WIDTH
                screen_y = (range_y - cam_y) * TILE_HEIGHT
                draw_text(self.game_surface, "\uf0489", screen_x, screen_y, 
                        self.font, color=(240, 72, 137))
        
        # Draw area of effect (yellow)
        for area_x, area_y in spell_area_tiles:
            if 0 <= area_x - cam_x < (game_rect.width // TILE_WIDTH) and \
               0 <= area_y - cam_y < (game_rect.height // TILE_HEIGHT):
                screen_x = (area_x - cam_x) * TILE_WIDTH
                screen_y = (area_y - cam_y) * TILE_HEIGHT
                draw_text(self.game_surface, "\uf0489", screen_x, screen_y, 
                        self.font, color=COLOR_GOLD)
        
        # Draw targeting cursor (blue)
        cursor_x, cursor_y = target_cursor
        if 0 <= cursor_x - cam_x < (game_rect.width // TILE_WIDTH) and \
           0 <= cursor_y - cam_y < (game_rect.height // TILE_HEIGHT):
            screen_x = (cursor_x - cam_x) * TILE_WIDTH
            screen_y = (cursor_y - cam_y) * TILE_HEIGHT
            draw_text(self.game_surface, "\ue26d", screen_x, screen_y, 
                    self.font, color=COLOR_BLUE)
    
    def _draw_entities(self, all_entities, player, cam_x, cam_y, game_rect):
        """Draw all entities with visual effects."""
        from entities import NPC
        
        # Sort entities (NPCs on top)
        sorted_entities = sorted(all_entities, key=lambda e: isinstance(e, NPC))
        
        for entity in sorted_entities:
            # Check if entity is alive and visible
            if (hasattr(entity, 'hp') and entity.hp > 0) or not hasattr(entity, 'hp'):
                if 0 <= entity.x - cam_x < (game_rect.width // TILE_WIDTH) and \
                   0 <= entity.y - cam_y < (game_rect.height // TILE_HEIGHT):
                    
                    # Calculate base position
                    base_x = (entity.x - cam_x) * TILE_WIDTH
                    base_y = (entity.y - cam_y) * TILE_HEIGHT
                    
                    # Apply knockback offset
                    knockback_dx, knockback_dy = self.vfx_manager.get_knockback_offset(entity)
                    final_x = base_x + knockback_dx
                    final_y = base_y + knockback_dy
                    
                    # Apply flash effect to color
                    original_color = entity.color
                    flash_intensity = self.vfx_manager.get_flash_intensity(entity)
                    if flash_intensity > 0:
                        final_color = apply_flash_to_color(original_color, flash_intensity)
                    else:
                        final_color = original_color
                    
                    # Draw entity
                    draw_text(self.game_surface, entity.char, final_x, final_y, 
                            self.font, color=final_color)
    
    def _draw_look_cursor(self, look_cursor, cam_x, cam_y, game_rect):
        """Draw the look cursor."""
        if not look_cursor:
            return
            
        cursor_x, cursor_y = look_cursor
        if 0 <= cursor_x - cam_x < (game_rect.width // TILE_WIDTH) and \
           0 <= cursor_y - cam_y < (game_rect.height // TILE_HEIGHT):
            screen_x = (cursor_x - cam_x) * TILE_WIDTH
            screen_y = (cursor_y - cam_y) * TILE_HEIGHT
            pygame.draw.rect(self.game_surface, COLOR_SELECTED, 
                           (screen_x, screen_y, TILE_WIDTH, TILE_HEIGHT), 2)
    
    def draw_ui(self, right_panel_tabs_rect, panel_tabs, active_panel, right_panel_rect, 
                player, input_focus, equipment_selected_index, inventory_selected_index, 
                spells_selected_index, quest_selected_index):
        """Draw all UI panels."""
        # Draw tabs
        draw_tabs(self.screen, right_panel_tabs_rect, panel_tabs, active_panel, 
                 self.font, input_focus == 'panel')
        
        # Draw panel background
        draw_panel(self.screen, right_panel_rect, border_color=COLOR_WHITE)
        
        # Draw active panel content
        if active_panel == CHARACTER_SHEET_ICON:
            draw_character_sheet_panel(self.screen, right_panel_rect, player, self.font)
        elif active_panel == EQUIPMENT_ICON:
            draw_equipment_panel(self.screen, right_panel_rect, player, 
                               equipment_selected_index, self.font)
        elif active_panel == INVENTORY_ICON:
            draw_inventory_panel(self.screen, right_panel_rect, player, 
                               inventory_selected_index, self.font)
        elif active_panel == SPELLS_ICON:
            draw_spells_panel(self.screen, right_panel_rect, player, 
                            spells_selected_index, self.font)
        elif active_panel == LOCATIONS_ICON:
            draw_locations_panel(self.screen, right_panel_rect, player, self.font)
        elif active_panel == QUESTS_ICON:
            draw_quests_panel(self.screen, right_panel_rect, player, 
                            quest_selected_index, self.font)
    
    def draw_log(self, log_rect, message_log, log_scroll_offset, has_focus):
        """Draw the message log panel."""
        draw_log_panel(self.screen, log_rect, message_log, log_scroll_offset, 
                      self.font, has_focus)