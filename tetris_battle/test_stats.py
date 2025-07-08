#!/usr/bin/env python3
"""
Game Boy Tetris Battle - Statistics Validation
"""
import pygame
import time
import matplotlib.pyplot as plt

# Test data for statistics
test_stats = [
    {'round': 1, 'winner': 'Player', 'player': {'score': 1200, 'lines': 8, 'pieces': 25, 'level': 1, 'time': 120}, 'ai': {'score': 800, 'lines': 5, 'pieces': 20, 'level': 0, 'time': 120}},
    {'round': 2, 'winner': 'AI', 'player': {'score': 900, 'lines': 6, 'pieces': 22, 'level': 0, 'time': 90}, 'ai': {'score': 1500, 'lines': 10, 'pieces': 28, 'level': 1, 'time': 90}},
    {'round': 3, 'winner': 'Player', 'player': {'score': 2100, 'lines': 15, 'pieces': 40, 'level': 1, 'time': 180}, 'ai': {'score': 1800, 'lines': 12, 'pieces': 35, 'level': 1, 'time': 180}}
]

def generate_test_stats_graph():
    """Generate Game Boy style statistics graph"""
    try:
        # Create figure with Game Boy color scheme
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.patch.set_facecolor('#8BAC0F')  # Game Boy background
        
        # Set up data for graphs
        rounds = [stat['round'] for stat in test_stats]
        player_scores = [stat['player']['score'] for stat in test_stats]
        ai_scores = [stat['ai']['score'] for stat in test_stats]
        player_lines = [stat['player']['lines'] for stat in test_stats]
        ai_lines = [stat['ai']['lines'] for stat in test_stats]
        player_pieces = [stat['player']['pieces'] for stat in test_stats]
        ai_pieces = [stat['ai']['pieces'] for stat in test_stats]
        
        # Game Boy color palette
        gb_colors = {'player': '#0F380F', 'ai': '#306230'}
        
        # Score comparison
        ax1.plot(rounds, player_scores, 'o-', color=gb_colors['player'], label='Player', linewidth=2)
        ax1.plot(rounds, ai_scores, 's-', color=gb_colors['ai'], label='AI', linewidth=2)
        ax1.set_title('SCORE COMPARISON', fontsize=14, color='#0F380F')
        ax1.set_xlabel('Round')
        ax1.set_ylabel('Score')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#9BBC0F')
        
        # Lines cleared comparison
        ax2.plot(rounds, player_lines, 'o-', color=gb_colors['player'], label='Player', linewidth=2)
        ax2.plot(rounds, ai_lines, 's-', color=gb_colors['ai'], label='AI', linewidth=2)
        ax2.set_title('LINES CLEARED', fontsize=14, color='#0F380F')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Lines')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#9BBC0F')
        
        # Pieces per minute
        player_ppm = [stat['player']['pieces'] / max(stat['player']['time']/60, 1) for stat in test_stats]
        ai_ppm = [stat['ai']['pieces'] / max(stat['ai']['time']/60, 1) for stat in test_stats]
        
        ax3.plot(rounds, player_ppm, 'o-', color=gb_colors['player'], label='Player', linewidth=2)
        ax3.plot(rounds, ai_ppm, 's-', color=gb_colors['ai'], label='AI', linewidth=2)
        ax3.set_title('PIECES PER MINUTE', fontsize=14, color='#0F380F')
        ax3.set_xlabel('Round')
        ax3.set_ylabel('PPM')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_facecolor('#9BBC0F')
        
        # Win/Loss record
        player_wins = sum(1 for stat in test_stats if stat['winner'] == 'Player')
        ai_wins = sum(1 for stat in test_stats if stat['winner'] == 'AI')
        
        ax4.bar(['Player', 'AI'], [player_wins, ai_wins], 
               color=[gb_colors['player'], gb_colors['ai']])
        ax4.set_title('WIN RECORD', fontsize=14, color='#0F380F')
        ax4.set_ylabel('Wins')
        ax4.set_facecolor('#9BBC0F')
        
        # Style all axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(colors='#0F380F')
            ax.spines['bottom'].set_color('#0F380F')
            ax.spines['top'].set_color('#0F380F')
            ax.spines['right'].set_color('#0F380F')
            ax.spines['left'].set_color('#0F380F')
        
        plt.tight_layout()
        plt.suptitle('TETRIS BATTLE STATISTICS - GAME BOY STYLE', 
                    fontsize=16, color='#0F380F', y=0.98)
        plt.show()
        
    except Exception as e:
        print(f"Error generating stats graph: {e}")

def main():
    print("Testing Game Boy Tetris Statistics...")
    generate_test_stats_graph()
    print("Statistics test completed!")

if __name__ == "__main__":
    main()
