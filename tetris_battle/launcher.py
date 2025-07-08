"""
Tetris Battle Main Launcher
Choose between local AI battle and online multiplayer
"""
import pygame
import sys
from config import *

class TestMenu:
    """Submenu for test and demo modes"""
    
    def __init__(self, screen, font_large, font_medium, font_small):
        self.screen = screen
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
        self.clock = pygame.time.Clock()
        
        self.menu_selection = 0
        self.menu_options = [
            "AI Performance Test",
            "Battle Test (AI vs Player)",
            "Network Test",
            "Complete System Test",
            "Sound Test",
            "Statistics Test",
            "Back to Main Menu"
        ]
        
        self.descriptions = [
            "Test AI playing performance and speed",
            "Visual test of AI vs Player battle",
            "Test network connectivity and setup",
            "Comprehensive test of all systems",
            "Test sound system and audio",
            "Test statistics and scoring system",
            "Return to main menu"
        ]
    
    def run(self):
        """Test menu loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if not self._handle_test_selection():
                            return
            
            self._draw_test_menu()
            self.clock.tick(60)
    
    def _handle_test_selection(self) -> bool:
        """Handle test menu selection"""
        option = self.menu_options[self.menu_selection]
        
        if option == "AI Performance Test":
            self._launch_ai_test()
        elif option == "Battle Test (AI vs Player)":
            self._launch_battle_test()
        elif option == "Network Test":
            self._launch_network_test()
        elif option == "Complete System Test":
            self._launch_complete_test()
        elif option == "Sound Test":
            self._launch_sound_test()
        elif option == "Statistics Test":
            self._launch_stats_test()
        elif option == "Back to Main Menu":
            return False
        
        return True
    
    def _launch_ai_test(self):
        """Launch AI performance test"""
        pygame.quit()
        try:
            from test_ai import main as ai_test_main
            ai_test_main()
        except ImportError as e:
            print(f"Error launching AI test: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_battle_test(self):
        """Launch battle test"""
        pygame.quit()
        try:
            from test_battle import main as battle_test_main
            battle_test_main()
        except ImportError as e:
            print(f"Error launching battle test: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_network_test(self):
        """Launch network test"""
        pygame.quit()
        try:
            from network_test import main as network_test_main
            network_test_main()
        except ImportError as e:
            print(f"Error launching network test: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_complete_test(self):
        """Launch complete system test"""
        pygame.quit()
        try:
            from test_complete import main as complete_test_main
            complete_test_main()
        except ImportError as e:
            print(f"Error launching complete test: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_sound_test(self):
        """Launch sound test"""
        pygame.quit()
        try:
            from test_sound import main as sound_test_main
            sound_test_main()
        except ImportError as e:
            print(f"Error launching sound test: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_stats_test(self):
        """Launch statistics test"""
        pygame.quit()
        try:
            from test_stats import main as stats_test_main
            stats_test_main()
        except ImportError as e:
            print(f"Error launching stats test: {e}")
        finally:
            self._reinit_pygame()
    
    def _reinit_pygame(self):
        """Reinitialize pygame after a test ends"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Battle - Test Menu")
        self.clock = pygame.time.Clock()
    
    def _draw_test_menu(self):
        """Draw the test menu"""
        self.screen.fill(UI_BACKGROUND)
        
        # Title
        title = self.font_large.render("TEST & DEMO MODES", True, UI_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Choose a Test Mode", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 160
        for i, option in enumerate(self.menu_options):
            # Highlight selected option
            if i == self.menu_selection:
                # Draw selection background
                option_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, start_y + i * 50 - 5, 400, 40)
                pygame.draw.rect(self.screen, UI_BORDER, option_rect)
                color = BLACK
            else:
                color = UI_TEXT
            
            # Draw option text
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50 + 10))
            self.screen.blit(text, text_rect)
        
        # Description of selected option
        desc_y = start_y + len(self.menu_options) * 50 + 30
        description = self.descriptions[self.menu_selection]
        desc_text = self.font_small.render(description, True, UI_TEXT)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, desc_y))
        self.screen.blit(desc_text, desc_rect)
        
        pygame.display.flip()


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
            "Single Player",
            "Player vs AI",
            "Game Boy Tetris (Classic)",
            "Online Multiplayer",
            "Enhanced Online (Lobby + Spectator)",
            "Test & Demo Modes",
            "Exit Game"
        ]
        
        self.descriptions = [
            "Classic single-player Tetris experience",
            "Battle against an intelligent AI opponent",
            "Authentic 1989 Game Boy Tetris experience",
            "Play against another human over the internet",
            "Advanced multiplayer with lobbies and spectator mode",
            "Access test modes and demonstrations",
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
        
        if option == "Single Player":
            self._launch_single_player()
        elif option == "Player vs AI":
            self._launch_local_battle()
        elif option == "Game Boy Tetris (Classic)":
            self._launch_gameboy_tetris()
        elif option == "Online Multiplayer":
            self._launch_online_battle()
        elif option == "Enhanced Online (Lobby + Spectator)":
            self._launch_enhanced_online()
        elif option == "Test & Demo Modes":
            self._launch_test_menu()
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
    
    def _launch_enhanced_online(self):
        """Launch enhanced online multiplayer with lobby system"""
        pygame.quit()
        try:
            from enhanced_online_battle import main as enhanced_online_main
            enhanced_online_main()
        except ImportError as e:
            print(f"Error launching enhanced online battle: {e}")
            print("Make sure all enhanced network components are properly installed")
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
    
    def _launch_gameboy_tetris(self):
        """Launch Game Boy Tetris mode"""
        pygame.quit()
        try:
            from main_gb import main as gb_main
            gb_main()
        except ImportError as e:
            print(f"Error launching Game Boy Tetris: {e}")
        finally:
            self._reinit_pygame()
    
    def _launch_test_menu(self):
        """Launch test and demo submenu"""
        self._show_test_menu()

    def _show_test_menu(self):
        """Show test and demo modes submenu"""
        test_menu = TestMenu(self.screen, self.font_large, self.font_medium, self.font_small)
        test_menu.run()
        # Re-initialize after test menu
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
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Complete Game Collection", True, UI_TEXT)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 105))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 160
        for i, option in enumerate(self.menu_options):
            # Highlight selected option
            if i == self.menu_selection:
                # Draw selection background
                option_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, start_y + i * 50 - 5, 400, 40)
                pygame.draw.rect(self.screen, UI_BORDER, option_rect)
                color = BLACK
            else:
                color = UI_TEXT
            
            # Draw option text
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 50 + 10))
            self.screen.blit(text, text_rect)
        
        # Description of selected option
        desc_y = start_y + len(self.menu_options) * 50 + 30
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
        version_text = self.font_small.render("Tetris Battle v3.0 - Complete Collection with AI, Online & Classic Modes", True, GRAY)
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(version_text, version_rect)
        
        pygame.display.flip()

def main():
    """Main launcher function"""
    launcher = TetrisLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
