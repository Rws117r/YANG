# ui.py - Complete version with enhanced spells panel
import pygame
from config import *

def draw_text(surface, text, x, y, font, color=COLOR_WHITE, bg_color=None, center=False, max_width=None):
    """Renders text, now with word-wrapping capabilities and returns number of lines rendered."""
    words = text.split(' ')
    lines = []
    current_line = ""

    if max_width:
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:  # Don't append empty lines
                    lines.append(current_line.rstrip())
                current_line = word + " "
        if current_line:  # Don't forget the last line
            lines.append(current_line.rstrip())
    else:
        lines.append(text)

    y_offset = 0
    for line in lines:
        if line:  # Only render non-empty lines
            text_surface = font.render(line, True, color, bg_color)
            text_rect = text_surface.get_rect()
            if center:
                text_rect.centerx = x
            else:
                text_rect.left = x
            text_rect.top = y + y_offset
            surface.blit(text_surface, text_rect)
        y_offset += font.get_height()
    
    return len(lines)  # Return the number of lines actually rendered

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
    if header and font:
        header_y = rect.top - font.get_height() - 5
        draw_text(surface, header, rect.centerx, header_y, font, COLOR_WHITE, center=True)

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
    """Draws the new scrollable log panel at the bottom with proper text wrapping."""
    border_color = COLOR_FOCUS_BORDER if has_focus else COLOR_WHITE
    draw_panel(surface, rect, "Log", font, border_color)
    
    # Start from the bottom and work our way up
    y = rect.bottom - 5
    messages_displayed = 0
    
    # Calculate available width for text (minus padding)
    text_width = rect.width - 10
    
    # Go through messages in reverse order (newest first)
    for i in range(len(message_log) - 1 - scroll_offset, -1, -1):
        if messages_displayed >= len(message_log):
            break
            
        msg, color = message_log[i]
        
        # Calculate how many lines this message will take
        words = msg.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.rstrip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.rstrip())
        
        # Calculate the total height needed for this message
        message_height = len(lines) * font.get_height()
        
        # Check if we have room for this message
        if y - message_height < rect.top + 5:
            break
        
        # Move up to make room for this message
        y -= message_height
        
        # Render each line of the message
        line_y = y
        for line in lines:
            if line and line_y >= rect.top + 5:  # Make sure we're within bounds
                text_surface = font.render(line, True, color)
                surface.blit(text_surface, (rect.left + 5, line_y))
            line_y += font.get_height()
        
        messages_displayed += 1

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
            if hasattr(item, 'damage_dice') and item.damage_dice:
                stat_str += f"{item.damage_dice}d{item.damage_sides} "
            if hasattr(item, 'bonuses') and item.bonuses.get('attack', 0) > 0:
                stat_str += f"+{item.bonuses['attack']} ATK "
            if hasattr(item, 'bonuses') and item.bonuses.get('ac', 0) > 0:
                stat_str += f"+{item.bonuses['ac']} AC "
            draw_text(surface, stat_str, rect.left + 250, rect.top + y_offset, font, COLOR_GREY)
        y_offset += 30

def draw_inventory_panel(surface, rect, player, selected_index, font):
    """Draws the player's inventory (non-equipped items)."""
    y_offset = 20
    inventory = player.display_inventory
    if not inventory:
        draw_text(surface, "Inventory is empty", rect.centerx, rect.centery, font, COLOR_GREY, center=True)
        return
    
    for i, item in enumerate(inventory):
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
    xp_to_next = player.xp_to_next_level
    draw_bar(surface, rect.left + 50, y, rect.width - 60, font.get_height(), player.xp, xp_to_next, COLOR_XP_BAR, COLOR_GREY)
    draw_text(surface, f"{player.xp}/{xp_to_next}", rect.centerx, y, font, COLOR_WHITE, center=True)
    y += 50

    # CFE Saving Throws
    draw_text(surface, f"Fortitude Save: +{player.fortitude_save}", rect.left + 10, y, font)
    y += 25
    draw_text(surface, f"Reflex Save: +{player.reflex_save}", rect.left + 10, y, font)
    y += 25
    draw_text(surface, f"Will Save: +{player.will_save}", rect.left + 10, y, font)
    y += 35

    # Calculated Stats
    draw_text(surface, f"Attack Bonus: +{player.attack_bonus}", rect.left + 10, y, font)
    y += 25
    draw_text(surface, f"Armor Class: {player.ac}", rect.left + 10, y, font)
    y += 35

    # Core Abilities
    for stat, value in player.abilities.items():
        modifier = player.modifiers[stat]
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        draw_text(surface, f"{stat}: {value} ({mod_str})", rect.left + 10, y, font)
        y += 25
        
    # Gold
    draw_text(surface, f"{GOLD_ICON}: {player.gold}", rect.left + 10, rect.bottom - 40, font, COLOR_GOLD)

def draw_locations_panel(surface, rect, player, font):
    """Draws the locations the player has discovered."""
    y_offset = 20
    locations = sorted(list(player.known_locations))
    if not locations:
        draw_text(surface, "No locations discovered", rect.centerx, rect.centery, font, COLOR_GREY, center=True)
        return
    
    for location in locations:
        draw_text(surface, location, rect.left + 10, rect.top + y_offset, font)
        y_offset += 30

def draw_quests_panel(surface, rect, player, selected_index, font):
    """Draws the list of active quests."""
    y_offset = 20
    active_quests = sorted(player.quest_log.active_quests.keys())
    if not active_quests:
        draw_text(surface, "No active quests", rect.centerx, rect.centery, font, COLOR_GREY, center=True)
        return
    
    for i, quest_name in enumerate(active_quests):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        draw_text(surface, quest_name, rect.left + 10, rect.top + y_offset, font, color)
        y_offset += 30

def draw_spells_panel(surface, rect, player, selected_index, font):
    """Enhanced spells panel with prepare and cast options."""
    y_offset = 20
    
    if player.archetype != "Mage":
        draw_text(surface, "No spells available", rect.centerx, rect.centery, font, COLOR_GREY, center=True)
        return
    
    # Show spell slots
    draw_text(surface, "Spell Slots:", rect.left + 10, rect.top + y_offset, font, COLOR_WHITE)
    y_offset += 25
    
    for level in [1, 2, 3]:
        current_slots = player.spell_slots.get(level, 0)
        max_slots = player.max_spell_slots.get(level, 0)
        if max_slots > 0:
            slot_color = COLOR_BLUE if current_slots > 0 else COLOR_RED
            draw_text(surface, f"Level {level}: {current_slots}/{max_slots}", rect.left + 20, rect.top + y_offset, font, slot_color)
            y_offset += 20
    
    y_offset += 15
    draw_text(surface, "Known Spells:", rect.left + 10, rect.top + y_offset, font, COLOR_WHITE)
    y_offset += 25
    
    # Show known spells with enhanced status
    if hasattr(player, 'known_spells'):
        for i, spell_name in enumerate(player.known_spells):
            color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
            
            # Check spell status
            from spells import get_spell_by_name
            spell = get_spell_by_name(spell_name)
            if spell:
                is_prepared = spell_name in player.prepared_spells.get(spell.level, [])
                has_slots = player.spell_slots.get(spell.level, 0) > 0
                
                # Status indicators
                if is_prepared and has_slots:
                    prefix = "[READY] "
                    spell_color = COLOR_GREEN
                elif is_prepared and not has_slots:
                    prefix = "[NO SLOTS] "
                    spell_color = COLOR_RED
                elif not is_prepared:
                    prefix = "[UNPREPARED] "
                    spell_color = COLOR_GREY
                else:
                    prefix = ""
                    spell_color = color
                
                # Use selection color if this spell is selected
                display_color = color if i == selected_index else spell_color
                
                draw_text(surface, f"{prefix}{spell_name}", rect.left + 20, rect.top + y_offset, font, display_color)
                y_offset += 25
    
    # Enhanced instructions
    draw_text(surface, "ENTER to prepare/unprepare", rect.left + 10, rect.bottom - 80, font, COLOR_GREY)
    draw_text(surface, "C to cast selected spell", rect.left + 10, rect.bottom - 60, font, COLOR_BLUE)
    draw_text(surface, "Press R to rest", rect.left + 10, rect.bottom - 40, font, COLOR_GREY)

def draw_quest_details_window(surface, rect, quest, font):
    """Draws a pop-up window with the details of a quest."""
    draw_panel(surface, rect, "Quest Details", font, COLOR_WHITE)
    
    # Quest name
    draw_text(surface, quest.name, rect.centerx, rect.top + 20, font, COLOR_GOLD, center=True)
    
    # Quest description
    draw_text(surface, quest.description, rect.left + 15, rect.top + 60, font, COLOR_WHITE, max_width=rect.width - 30)
    
    # Objectives
    y_offset = 120
    draw_text(surface, "Objectives:", rect.left + 15, rect.top + y_offset, font, COLOR_GREY)
    y_offset += 30
    
    for objective, completed in quest.objectives.items():
        status = "[X]" if completed else "[ ]"
        color = COLOR_GREEN if completed else COLOR_WHITE
        draw_text(surface, f"{status} {objective}", rect.left + 25, rect.top + y_offset, font, color)
        y_offset += 25
    
    # Instructions
    draw_text(surface, "Press ESC to close", rect.centerx, rect.bottom - 25, font, COLOR_GREY, center=True)

def draw_level_up_window(surface, rect, font):
    """Draws the level up confirmation window."""
    draw_panel(surface, rect, "Level Up!", font, COLOR_GOLD)
    
    draw_text(surface, "You feel stronger!", rect.centerx, rect.centery - 20, font, COLOR_GOLD, center=True)
    draw_text(surface, "Your abilities have improved!", rect.centerx, rect.centery, font, COLOR_WHITE, center=True)
    draw_text(surface, "Press ENTER to continue", rect.centerx, rect.centery + 30, font, COLOR_GREY, center=True)

def draw_item_options_window(surface, rect, item, options, selected_index, font):
    """Draws the options for an inventory item."""
    draw_panel(surface, rect, item.name, font, COLOR_WHITE)
    
    # Item description if available
    if hasattr(item, 'description') and item.description:
        draw_text(surface, item.description, rect.left + 10, rect.top + 20, font, COLOR_GREY, max_width=rect.width - 20)
        y_start = rect.top + 70
    else:
        y_start = rect.top + 30
    
    # Options
    for i, option in enumerate(options):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        draw_text(surface, option, rect.centerx, y_start + i * 30, font, color, center=True)
    
    # Instructions
    draw_text(surface, "ESC to cancel", rect.centerx, rect.bottom - 25, font, COLOR_GREY, center=True)

def draw_equipment_selection_window(surface, rect, items, selected_index, font):
    """Draws a list of equippable items with their stats."""
    draw_panel(surface, rect, "Choose Item to Equip", font, COLOR_WHITE)
    
    if not items:
        draw_text(surface, "Nothing to equip.", rect.centerx, rect.centery, font, COLOR_GREY, center=True)
        draw_text(surface, "Press ESC to cancel", rect.centerx, rect.centery + 30, font, COLOR_GREY, center=True)
    else:
        y_offset = 30
        for i, item in enumerate(items):
            color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
            draw_text(surface, item.name, rect.centerx, rect.top + y_offset, font, color, center=True)
            y_offset += 25
            
            stat_str = ""
            if hasattr(item, 'damage_dice') and item.damage_dice:
                stat_str += f"{item.damage_dice}d{item.damage_sides} "
            if hasattr(item, 'bonuses') and item.bonuses.get('attack', 0) > 0:
                stat_str += f"+{item.bonuses['attack']} ATK "
            if hasattr(item, 'bonuses') and item.bonuses.get('ac', 0) > 0:
                stat_str += f"+{item.bonuses['ac']} AC "
            if stat_str:
                draw_text(surface, stat_str, rect.centerx, rect.top + y_offset, font, COLOR_GREY, center=True)
            y_offset += 35
        
        # Instructions
        draw_text(surface, "ENTER to equip, ESC to cancel", rect.centerx, rect.bottom - 25, font, COLOR_GREY, center=True)

def draw_pause_menu_window(surface, rect, selected_index, font):
    """Draws the pause menu with save/load/quit options."""
    draw_panel(surface, rect, "Game Menu", font, COLOR_WHITE)
    
    # Menu options
    options = ["Resume", "Save Game", "Load Game", "Quit to Title"]
    
    # Draw title
    draw_text(surface, "Game Paused", rect.centerx, rect.top + 20, font, COLOR_WHITE, center=True)
    
    # Draw options
    y_offset = 60
    for i, option in enumerate(options):
        color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
        draw_text(surface, option, rect.centerx, rect.top + y_offset, font, color, center=True)
        y_offset += 35
    
    # Draw instructions
    draw_text(surface, "Use UP/DOWN to navigate", rect.centerx, rect.bottom - 45, font, COLOR_GREY, center=True)
    draw_text(surface, "ENTER to select, ESC to close", rect.centerx, rect.bottom - 25, font, COLOR_GREY, center=True)

def draw_targeting_overlay(surface, rect, font):
    """Draws targeting mode instructions."""
    draw_panel(surface, rect, "Spell Targeting", font, COLOR_PURPLE)
    
    instructions = [
        "Use arrow keys to aim",
        "ENTER to cast spell",
        "ESC to cancel targeting",
        "",
        "Red: Valid targets",
        "Yellow: Area of effect", 
        "Blue: Targeting cursor"
    ]
    
    y_offset = 20
    for instruction in instructions:
        if instruction == "":
            y_offset += 10
        else:
            color = COLOR_WHITE
            if "Red:" in instruction:
                color = (240, 72, 137)
            elif "Yellow:" in instruction:
                color = COLOR_GOLD
            elif "Blue:" in instruction:
                color = COLOR_BLUE
                
            draw_text(surface, instruction, rect.centerx, rect.top + y_offset, font, color, center=True)
            y_offset += 25