"""
Tetris Battle Main Launcher
Choose between local AI battle and online multiplayer
"""
import pygame
import sys
from config import *

class TetrisLauncher:
    """Main launcher for Tetris Battle"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Main Menu")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Menu state
        self.menu_selection = 0
        self.menu_options = [
            "Local Battle (vs AI)",
            "Online Multiplayer",
            "Single Player",
            "Exit Game"
        ]
        
        self.descriptions = [
            "Battle against an intelligent AI opponent",
            "Play against another human over the internet",
            "Classic single-player Tetris experience",
            "Exit the game"
        ]
    
    def run(self):
        """Main menu loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if not self._handle_selection():
                            running = False
            
            self._draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def _handle_selection(self) -> bool:
        """Handle menu selection"""
        option = self.menu_options[self.menu_selection]
        
        if option == "Local Battle (vs AI)":
            self._launch_local_battle()
        elif option == "Online Multiplayer":
            self._launch_online_battle()
        elif option == "Single Player":
            self._launch_single_player()
        elif option == "Exit Game":
            return False
        
        # Return to main menu after game ends
        return True
    
    def _launch_local_battle(self):
        """Launch local AI battle"""
        pygame.quit()
        try:
            from main import main as local_main
            local_main()
        except ImportError as e:
            print(f"Error launching local battle: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_online_battle(self):
        """Launch online multiplayer"""
        pygame.quit()
        try:
            from online_battle import main as online_main
            online_main()
        except ImportError as e:
            print(f"Error launching online battle: {e}")
            print("Make sure all network components are properly installed")
        finally:
            self._reinit_pygame()
    
    def _launch_single_player(self):
        """Launch single player mode"""
        pygame.quit()
        try:
            from single_player import main as single_main
            single_main()
        except ImportError as e:
            print(f"Error launching single player: {e}")
        finally:
            self._reinit_pygame()
    
    def _reinit_pygame(self):
        """Reinitialize pygame after a game ends"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Main Menu")
        self.clock = pygame.time.Clock()
    
    def _draw(self):
        """Draw the main menu"""
        self.screen.fill(UI_BACKGROUND)
        
        # Title
        title = self.font_large.render("TETRIS BATTLE", True, UI_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Choose Your Game Mode", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 200
        for i, option in enumerate(self.menu_options):
            # Highlight selected option
            if i == self.menu_selection:
                # Draw selection background
                option_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, start_y + i * 60 - 5, 400, 50)
                pygame.draw.rect(self.screen, UI_BORDER, option_rect)
                color = BLACK
            else:
                color = UI_TEXT
            
            # Draw option text
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60 + 15))
            self.screen.blit(text, text_rect)
        
        # Description of selected option
        desc_y = start_y + len(self.menu_options) * 60 + 40
        description = self.descriptions[self.menu_selection]
        desc_text = self.font_small.render(description, True, UI_TEXT)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, desc_y))
        self.screen.blit(desc_text, desc_rect)
        
        # Controls
        controls = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "Press ESC to exit"
        ]
        
        controls_y = desc_y + 60
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, controls_y + i * 20))
            self.screen.blit(text, text_rect)
        
        # Version info
        version_text = self.font_small.render("Tetris Battle v2.0 - Now with Online Multiplayer!", True, GRAY)
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(version_text, version_rect)
        
        pygame.display.flip()

def main():
    """Main launcher function"""
    launcher = TetrisLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
