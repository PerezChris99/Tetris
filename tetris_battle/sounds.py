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
                if os.path.exists(sound_path) and os.path.getsize(sound_path) > 0:
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                else:
                    # Create a placeholder sound
                    self.sounds[sound_name] = self.create_placeholder_sound(sound_name)
            except pygame.error:
                # If sound loading fails, create a placeholder
                self.sounds[sound_name] = self.create_placeholder_sound(sound_name)
    
    def create_placeholder_sound(self, sound_name):
        """Create Game Boy-style placeholder sounds for missing audio files"""
        try:
            import numpy as np
            
            sample_rate = 22050
            
            # Game Boy-style sound frequencies and patterns
            if sound_name == 'move':
                # Short high beep
                duration = 0.08
                frequency = 800
            elif sound_name == 'rotate':
                # Medium beep
                duration = 0.1
                frequency = 600
            elif sound_name == 'drop':
                # Low thud
                duration = 0.15
                frequency = 200
            elif sound_name == 'clear':
                # Multi-tone clear sound
                duration = 0.3
                frequency = 1000
            elif sound_name == 'gameover':
                # Descending tone
                duration = 0.8
                frequency = 400
            elif sound_name == 'win':
                # Ascending victory fanfare
                duration = 0.6
                frequency = 800
            elif sound_name == 'lose':
                # Descending loss tone
                duration = 0.5
                frequency = 300
            else:
                duration = 0.1
                frequency = 440
            
            # Generate the waveform
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            if sound_name == 'clear':
                # Multi-tone line clear sound
                wave = (np.sin(frequency * 2 * np.pi * t) + 
                       np.sin(frequency * 1.5 * 2 * np.pi * t)) * 0.3
            elif sound_name == 'gameover':
                # Descending game over sound
                freq_sweep = frequency * (1 - t / duration)
                wave = np.sin(freq_sweep * 2 * np.pi * t) * 0.5
            elif sound_name == 'win':
                # Ascending victory sound
                freq_sweep = frequency * (1 + t / duration)
                wave = np.sin(freq_sweep * 2 * np.pi * t) * 0.4
            else:
                # Simple sine wave
                wave = np.sin(frequency * 2 * np.pi * t) * 0.3
            
            # Apply fade out to prevent clicks
            fade_samples = int(sample_rate * 0.01)  # 10ms fade
            if len(wave) > fade_samples:
                wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit integers
            wave = (wave * 32767).astype(np.int16)
            
            # Make stereo (duplicate to two channels) and ensure C-contiguous
            stereo_wave = np.zeros((len(wave), 2), dtype=np.int16)
            stereo_wave[:, 0] = wave  # Left channel
            stereo_wave[:, 1] = wave  # Right channel
            
            # Ensure the array is C-contiguous
            stereo_wave = np.ascontiguousarray(stereo_wave)
            
            # Create pygame sound
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(self.volume)
            return sound
        except Exception as e:
            # Return None if we can't create the sound
            return None
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:
                pass  # Ignore sound errors silently
    
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
