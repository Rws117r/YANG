# screens.py
import pygame
from config import *
from ui import draw_text # draw_menu is no longer used
from entities import Player, roll_dice

def title_screen(screen, font, clock):
    """Displays the title screen and handles menu navigation."""
    menu_options = ["New Game", "Quit"]
    selected_index = 0
    
    while True:
        screen.fill(COLOR_BLACK)
        draw_text(screen, "ASCII Adventure RPG", screen.get_width() // 2, screen.get_height() // 4, font, center=True)
        
        # --- MODIFICATION: Manually draw the menu using draw_text ---
        for i, option_text in enumerate(menu_options):
            color = COLOR_SELECTED if i == selected_index else COLOR_WHITE
            y_pos = screen.get_height() // 2 + i * 60
            draw_text(screen, option_text, screen.get_width() // 2, y_pos, font, color, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_index == 0: return "new_game"
                    if selected_index == 1: return "quit"
                elif event.key == pygame.K_ESCAPE:
                    return "quit"

        pygame.display.flip()
        clock.tick(FPS)

def character_creation_screen(screen, font, clock):
    """Guides the player through creating a character."""
    ability_scores = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    archetypes = list(ARCHETYPES.keys())
    
    rolled_scores = sorted([roll_dice(3, 6) for _ in range(6)], reverse=True)
    assigned_scores = {}
    
    current_stat_index = 0
    current_archetype_index = 0
    
    stage = "assign_stats" # Stages: assign_stats, choose_archetype

    while True:
        screen.fill(COLOR_BLACK)
        
        # Draw instructions
        if stage == "assign_stats":
            draw_text(screen, "Assign Your Ability Scores", screen.get_width()//2, 50, font, center=True)
            draw_text(screen, "Use UP/DOWN to select a stat, ENTER to assign the next highest score.", screen.get_width()//2, 90, font, center=True)
        elif stage == "choose_archetype":
            draw_text(screen, "Choose Your Archetype", screen.get_width()//2, 50, font, center=True)
            draw_text(screen, "Use UP/DOWN to select, ENTER to confirm.", screen.get_width()//2, 90, font, center=True)


        # --- Stat Assignment Stage ---
        if stage == "assign_stats":
            # Display rolled scores
            draw_text(screen, "Your Rolls:", 100, 150, font)
            for i, score in enumerate(rolled_scores):
                color = COLOR_GREY if i < len(assigned_scores) else COLOR_WHITE
                draw_text(screen, str(score), 120, 190 + i * 40, font, color=color)

            # Display stats to be assigned
            for i, stat in enumerate(ability_scores):
                color = COLOR_SELECTED if i == current_stat_index else COLOR_WHITE
                value = assigned_scores.get(stat, "__")
                draw_text(screen, f"{stat}: {value}", 400, 190 + i * 40, font, color=color)
        
        # --- Archetype Selection Stage ---
        elif stage == "choose_archetype":
            for i, archetype in enumerate(archetypes):
                color = COLOR_SELECTED if i == current_archetype_index else COLOR_WHITE
                draw_text(screen, archetype, screen.get_width()//2, 200 + i * 60, font, color=color, center=True)
            
            # Display archetype info
            info = ARCHETYPES[archetypes[current_archetype_index]]
            draw_text(screen, f"HP Die: 1d{info['hp_die']}", screen.get_width()//2, 450, font, center=True, color=COLOR_GREY)
            draw_text(screen, f"Proficiencies: {info['proficiencies']}", screen.get_width()//2, 480, font, center=True, color=COLOR_GREY)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None # Go back to title screen
                
                if stage == "assign_stats":
                    if event.key == pygame.K_UP:
                        current_stat_index = (current_stat_index - 1) % len(ability_scores)
                    elif event.key == pygame.K_DOWN:
                        current_stat_index = (current_stat_index + 1) % len(ability_scores)
                    elif event.key == pygame.K_RETURN:
                        stat_to_assign = ability_scores[current_stat_index]
                        if stat_to_assign not in assigned_scores:
                            assigned_scores[stat_to_assign] = rolled_scores[len(assigned_scores)]
                            if len(assigned_scores) == len(ability_scores):
                                stage = "choose_archetype"

                elif stage == "choose_archetype":
                    if event.key == pygame.K_UP:
                        current_archetype_index = (current_archetype_index - 1) % len(archetypes)
                    elif event.key == pygame.K_DOWN:
                        current_archetype_index = (current_archetype_index + 1) % len(archetypes)
                    elif event.key == pygame.K_RETURN:
                        chosen_archetype = archetypes[current_archetype_index]
                        # Create and return the new player object
                        return Player(chosen_archetype, assigned_scores)

        pygame.display.flip()
        clock.tick(FPS)
