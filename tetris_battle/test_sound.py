#!/usr/bin/env python3
"""
Sound System Test
"""
import pygame
import time
from sounds import SoundManager

def main():
    pygame.init()
    
    print("Testing Sound System...")
    sound_manager = SoundManager()
    
    # Test all sounds
    sounds_to_test = ['move', 'rotate', 'drop', 'clear', 'win', 'lose', 'gameover']
    
    for sound_name in sounds_to_test:
        print(f"\nTesting {sound_name} sound...")
        sound_manager.play_sound(sound_name)
        time.sleep(1)
    
    # Test toggle
    print(f"\nToggling sound (currently {'ON' if sound_manager.enabled else 'OFF'})")
    sound_manager.toggle_sound()
    
    print("\nTrying to play move sound with sound toggled...")
    sound_manager.play_sound('move')
    time.sleep(1)
    
    # Toggle back
    print("\nToggling sound back...")
    sound_manager.toggle_sound()
    
    print("\nTrying to play move sound again...")
    sound_manager.play_sound('move')
    time.sleep(1)
    
    print("\nSound test completed!")

if __name__ == "__main__":
    main()
