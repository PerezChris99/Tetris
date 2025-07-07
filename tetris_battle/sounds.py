import pygame
import os
from config import *

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.enabled = True
        self.volume = 0.7
        self.load_sounds()
    
    def load_sounds(self):
        """Load sound effects"""
        sound_files = {
            'move': 'move.wav',
            'rotate': 'rotate.wav',
            'drop': 'drop.wav',
            'clear': 'clear.wav',
            'gameover': 'gameover.wav',
            'win': 'win.wav',
            'lose': 'lose.wav'
        }
        
        base_path = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
        
        for sound_name, filename in sound_files.items():
            sound_path = os.path.join(base_path, filename)
            try:
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                else:
                    # Create a placeholder sound or use a default beep
                    self.sounds[sound_name] = self.create_placeholder_sound(sound_name)
            except pygame.error:
                # If sound loading fails, create a placeholder
                self.sounds[sound_name] = self.create_placeholder_sound(sound_name)
    
    def create_placeholder_sound(self, sound_name):
        """Create a placeholder sound for missing audio files"""
        # Create a simple beep sound
        try:
            # Generate a simple sine wave
            import numpy as np
            
            duration = 0.1  # seconds
            sample_rate = 22050
            frequency = 440  # Hz
            
            if sound_name == 'move':
                frequency = 300
                duration = 0.05
            elif sound_name == 'rotate':
                frequency = 500
                duration = 0.1
            elif sound_name == 'drop':
                frequency = 200
                duration = 0.2
            elif sound_name == 'clear':
                frequency = 600
                duration = 0.3
            elif sound_name == 'gameover':
                frequency = 150
                duration = 0.5
            elif sound_name == 'win':
                frequency = 800
                duration = 0.4
            elif sound_name == 'lose':
                frequency = 100
                duration = 0.6
            
            frames = int(duration * sample_rate)
            arr = np.zeros(frames)
            
            for i in range(frames):
                arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
            
            # Convert to 16-bit integers
            arr = (arr * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_arr = np.zeros((frames, 2), dtype=np.int16)
            stereo_arr[:, 0] = arr
            stereo_arr[:, 1] = arr
            
            sound = pygame.sndarray.make_sound(stereo_arr)
            sound.set_volume(self.volume * 0.3)  # Make placeholder sounds quieter
            return sound
        except:
            # If numpy is not available, return None
            return None
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Ignore sound errors
    
    def set_volume(self, volume):
        """Set the volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        pygame.mixer.stop()

# Create some basic sound files if they don't exist
def create_default_sounds():
    """Create default sound files if they don't exist"""
    sounds_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
    
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
    
    # Create placeholder files (these will be replaced with actual sounds)
    sound_files = ['move.wav', 'rotate.wav', 'drop.wav', 'clear.wav', 'gameover.wav', 'win.wav', 'lose.wav']
    
    for sound_file in sound_files:
        sound_path = os.path.join(sounds_dir, sound_file)
        if not os.path.exists(sound_path):
            # Create an empty file as placeholder
            with open(sound_path, 'w') as f:
                f.write('')

# Initialize default sounds
create_default_sounds()
