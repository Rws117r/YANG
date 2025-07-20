# main.py
import pygame
from config import *
from screens import title_screen, character_creation_screen
from engine import Game

def main():
    """Main function to run the game."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ASCII Adventure RPG")
    clock = pygame.time.Clock()
    
    try:
        font = pygame.font.Font(FONT_NAME, FONT_SIZE)
    except FileNotFoundError:
        print(f"Error: Font file '{FONT_NAME}' not found.")
        return

    while True:
        # Start with the title screen
        choice = title_screen(screen, font, clock)
        
        if choice == "quit":
            break
        
        if choice == "new_game":
            # Move to character creation
            player = character_creation_screen(screen, font, clock)
            
            if player:
                # If a player was created, start the main game
                game = Game(screen, font, clock, player)
                game.run()
                # When the game loop ends, it returns to the title screen

    pygame.quit()

if __name__ == "__main__":
    main()
