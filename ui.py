# ui.py
import pygame
from config import *

def draw_text(surface, text, x, y, font, color=COLOR_WHITE, bg_color=None, center=False, max_width=None):
    """Renders text, now with word-wrapping capabilities."""
    words = text.split(' ')
    lines = []
    current_line = ""

    if max_width:
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
    else:
        lines.append(text)

    y_offset = 0
    for line in lines:
        text_surface = font.render(line, True, color, bg_color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.centerx = x
        else:
            text_rect.left = x
        text_rect.top = y + y_offset
        surface.blit(text_surface, text_rect)
        y_offset += font.get_height()

def draw_bar(surface, x, y, width, height, value, max_value, bar_color, back_color):
    """Draws a status bar (for HP, XP, etc.)."""
    pygame.draw.rect(surface, back_color, (x, y, width, height))
    fill_width = int(width * (value / max_value))
    fill_width = min(width, max(0, fill_width))
    if fill_width > 0:
        pygame.draw.rect(surface, bar_color, (x, y, fill_width, height))

def draw_panel(surface, rect, header=None, font=None, border_color=COLOR_WHITE):
    """Draws a standard panel with an optional header."""
    pygame.draw.rect(surface, COLOR_BLACK, rect)
    pygame.draw.rect(surface, border_color, rect, 2)

def draw_tabs(surface, rect, tabs, active_tab, font, has_focus):
    """Draws dynamic, rectangular ICON tabs."""
    tab_width = rect.width // len(tabs)
    x_offset = rect.left
    
    for i, tab_icon in enumerate(tabs):
        is_active = (tab_icon == active_tab) and has_focus
        
        top_y = rect.top - 5 if is_active else rect.top
        tab_rect = pygame.Rect(x_offset, top_y, tab_width, rect.height + 5)

        bg_color = COLOR_BLACK
        icon_color = COLOR_WHITE if is_active else COLOR_GREY
        
        pygame.draw.rect(surface, bg_color, tab_rect)
        
        if is_active:
            pygame.draw.rect(surface, COLOR_WHITE, tab_rect, 2)
        else:
            pygame.draw.rect(surface, COLOR_GREY, tab_rect, 1)

        icon_font = pygame.font.Font(FONT_NAME, FONT_SIZE + 4)
        icon_surf = icon_font.render(tab_icon, True, icon_color)
        icon_rect = icon_surf.get_rect()
        icon_rect.center = tab_rect.center
        surface.blit(icon_surf, icon_rect)
        
        x_offset += tab_width

def draw_log_panel(surface, rect, message_log, scroll_offset, font, has_focus):
    """Draws the new scrollable log panel at the bottom."""
    border_color = COLOR_FOCUS_BORDER if has_focus else COLOR_WHITE
    draw_panel(surface, rect, "Log", font, border_color)
    
    y = rect.bottom - font.get_height() - 5
    for i in range(len(message_log) - 1 - scroll_offset, -1, -1):
        msg, color = message_log[i]
        draw_text(surface, msg, rect.left + 5, y, font, color, max_width=rect.width - 10)
        y -= font.get_height() * (1 + msg.count('\n'))
        if y < rect.top:
            break

def draw_equipment_panel(surface, rect, player, selected_index, font):
    """Draws the player's equipped items with stats."""
    y_offset = 20 
    for i, (slot, item) in enumerate(player.equipment.items()):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        item_name = item.name if item else "---"
        draw_text(surface, f"{slot}:", rect.left + 10, rect.top + y_offset, font, COLOR_GREY)
        draw_text(surface, item_name, rect.left + 120, rect.top + y_offset, font, color)
        if item:
            stat_str = ""
            if item.damage_dice:
                stat_str += f"{item.damage_dice}d{item.damage_sides} "
            if item.bonuses.get('attack', 0) > 0:
                stat_str += f"+{item.bonuses['attack']} ATK "
            if item.bonuses.get('ac', 0) > 0:
                stat_str += f"+{item.bonuses['ac']} AC "
            draw_text(surface, stat_str, rect.left + 250, rect.top + y_offset, font, COLOR_GREY)
        y_offset += 30

def draw_inventory_panel(surface, rect, player, selected_index, font):
    """Draws the player's inventory (non-equipped items)."""
    y_offset = 20
    for i, item in enumerate(player.display_inventory):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        draw_text(surface, item.name, rect.left + 10, rect.top + y_offset, font, color)
        y_offset += 30

def draw_character_sheet_panel(surface, rect, player, font):
    """Draws the player's ability scores and stats."""
    y = rect.top + 20
    draw_text(surface, player.name, rect.centerx, y, font, COLOR_WHITE, center=True)
    y += 25
    draw_text(surface, f"Level {player.level} {player.archetype}", rect.centerx, y, font, COLOR_GREY, center=True)
    y += 35
    
    draw_text(surface, "HP", rect.left + 10, y, font, COLOR_WHITE)
    draw_bar(surface, rect.left + 50, y, rect.width - 60, font.get_height(), player.hp, player.max_hp, COLOR_HP_BAR, COLOR_GREY)
    draw_text(surface, f"{player.hp}/{player.max_hp}", rect.centerx, y, font, COLOR_WHITE, center=True)
    y += 35

    draw_text(surface, "XP", rect.left + 10, y, font, COLOR_WHITE)
    draw_bar(surface, rect.left + 50, y, rect.width - 60, font.get_height(), player.xp, player.xp_to_next_level, COLOR_XP_BAR, COLOR_GREY)
    draw_text(surface, f"{player.xp}/{player.xp_to_next_level}", rect.centerx, y, font, COLOR_WHITE, center=True)
    y += 50

    # Calculated Stats
    draw_text(surface, f"Attack Bonus: +{player.attack_bonus}", rect.left + 10, y, font)
    y += 30
    draw_text(surface, f"Armor Class: {player.ac}", rect.left + 10, y, font)
    y += 50

    # Core Abilities
    for stat, value in player.abilities.items():
        modifier = player.modifiers[stat]
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        draw_text(surface, f"{stat}: {value} ({mod_str})", rect.left + 10, y, font)
        y += 30
        
    # Gold
    draw_text(surface, f"{GOLD_ICON}: {player.gold}", rect.left + 10, rect.bottom - 40, font, COLOR_GOLD)


def draw_locations_panel(surface, rect, player, font):
    """Draws the locations the player has discovered."""
    y_offset = 20
    for location in sorted(list(player.known_locations)):
        draw_text(surface, location, rect.left + 10, rect.top + y_offset, font)
        y_offset += 30

def draw_quests_panel(surface, rect, player, selected_index, font):
    """Draws the list of active quests."""
    y_offset = 20
    for i, quest_name in enumerate(sorted(player.quest_log.active_quests.keys())):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        draw_text(surface, quest_name, rect.left + 10, rect.top + y_offset, font, color)
        y_offset += 30

def draw_quest_details_window(surface, rect, quest, font):
    """Draws a pop-up window with the details of a quest."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0,0))

    draw_panel(surface, rect, header=quest.name, font=font)
    draw_text(surface, quest.description, rect.left + 15, rect.top + 30, font, COLOR_WHITE, max_width=rect.width - 30)

def draw_level_up_window(surface, rect, font):
    """Draws the level up confirmation window."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0,0))
    draw_panel(surface, rect, header="Level Up!", font=font)
    draw_text(surface, "You feel stronger!", rect.centerx, rect.centery - 20, font, center=True)
    draw_text(surface, "Press ENTER to continue", rect.centerx, rect.centery + 20, font, COLOR_GREY, center=True)

def draw_item_options_window(surface, rect, item, options, selected_index, font):
    """Draws the options for an inventory item."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0,0))
    draw_panel(surface, rect, header=item.name, font=font)
    for i, option in enumerate(options):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        draw_text(surface, option, rect.centerx, rect.top + 30 + i * 40, font, color, center=True)

def draw_equipment_selection_window(surface, rect, items, selected_index, font):
    """Draws a list of equippable items with their stats."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0,0))
    draw_panel(surface, rect, header="Choose Item to Equip", font=font)
    if not items:
        draw_text(surface, "Nothing to equip.", rect.centerx, rect.centery, font, COLOR_GREY, center=True)
    else:
        y_offset = 30
        for i, item in enumerate(items):
            color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
            draw_text(surface, item.name, rect.centerx, rect.top + y_offset, font, color, center=True)
            y_offset += 25
            
            stat_str = ""
            if item.damage_dice:
                stat_str += f"{item.damage_dice}d{item.damage_sides} "
            if item.bonuses.get('attack', 0) > 0:
                stat_str += f"+{item.bonuses['attack']} ATK "
            if item.bonuses.get('ac', 0) > 0:
                stat_str += f"+{item.bonuses['ac']} AC "
            draw_text(surface, stat_str, rect.centerx, rect.top + y_offset, font, COLOR_GREY, center=True)
            y_offset += 35
