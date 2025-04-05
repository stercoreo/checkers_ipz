# main.py
import pygame
from game import Game
from menu import Menu

def main():
    """
    Main game loop and screen management.
    Handles switching between menu and game screens.
    """
    pygame.init()
    screen = pygame.display.set_mode((800, 850))
    pygame.display.set_caption("Checkers")
    clock = pygame.time.Clock()
    
    current_screen = "menu"  # Start with menu screen
    menu = Menu(800, 850)    # Initialize menu
    game = None              # Game instance starts as None
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_screen == "menu":
                    action = menu.handle_click(event.pos)
                    if action == "local":
                        # Start local PvP game
                        game = Game(mode='local')
                        current_screen = "game"
                    elif action.startswith("ai_"):
                        # Start vs AI game with selected difficulty
                        difficulty = next(
                            btn["difficulty"] for btn in menu.buttons 
                            if btn["action"] == action
                        )
                        game = Game(mode='ai', difficulty=difficulty)
                        current_screen = "game"
                    elif action == "quit":
                        running = False
        
        # Screen rendering
        if current_screen == "menu":
            menu.draw(screen)
        elif current_screen == "game":
            result = game.run()
            if result == "menu":  # Returned to menu
                current_screen = "menu"
                game = None
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()