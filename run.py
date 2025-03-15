import os
import sys
import pygame
import cv2
import numpy as np
import mediapipe as mp
from pygame.locals import *
import traceback
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import game modules
from head_tracking.head_tracker import HeadTracker
from game.racing import RacingGame

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Game states
STATE_CALIBRATION = 0
STATE_GAME = 1
STATE_PAUSED = 2

# Initialize display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Head Racing Game")
clock = pygame.time.Clock()

# Initialize head tracker
head_tracker = None
try:
    head_tracker = HeadTracker()
    print("Head tracker initialized successfully")
except Exception as e:
    print(f"Error initializing head tracker: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Initialize racing game
racing_game = None
try:
    racing_game = RacingGame(WINDOW_WIDTH, WINDOW_HEIGHT)
    print("Racing game initialized successfully")
except Exception as e:
    print(f"Error initializing racing game: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Load sounds
try:
    pygame.mixer.init()
    background_music = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sounds', 'background.mp3'))
    crash_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sounds', 'crash.mp3'))
    # Load new sound effects
    collision_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sounds', 'collision.mp3'))
    racing_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'sounds', 'racing.mp3'))
    
    # Set volume for each sound
    background_music.set_volume(0.5)
    crash_sound.set_volume(0.8)
    collision_sound.set_volume(0.8)
    racing_sound.set_volume(0.6)
    
    # Play background music
    background_music.play(-1)  # Loop indefinitely
    
    print("All sounds loaded successfully")
except Exception as e:
    print(f"Error loading sounds: {e}")
    print(traceback.format_exc())
    # Initialize empty sound objects to prevent errors
    background_music = None
    crash_sound = None
    collision_sound = None
    racing_sound = None

# Initialize game state
current_state = STATE_CALIBRATION
paused = False
show_camera = True
show_debug = False
last_key_time = 0
key_cooldown = 0.2  # seconds

# Calibrate head tracker
print("Starting head tracker calibration...")
calibration_success = head_tracker.calibrate()
if calibration_success:
    print("Calibration successful")
else:
    print("Calibration failed, using default values")

# Switch to game state
current_state = STATE_GAME

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            current_time = time.time()
            if current_time - last_key_time > key_cooldown:
                last_key_time = current_time
                
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if current_state == STATE_GAME:
                        current_state = STATE_PAUSED
                        print("Game paused")
                    elif current_state == STATE_PAUSED:
                        current_state = STATE_GAME
                        print("Game resumed")
                elif event.key == pygame.K_c:
                    show_camera = not show_camera
                    print(f"Camera display: {'on' if show_camera else 'off'}")
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                    print(f"Debug info: {'on' if show_debug else 'off'}")
                elif event.key == pygame.K_r:
                    print("Recalibrating head tracker...")
                    head_tracker.calibrate()
                    print("Calibration complete")
                elif event.key == pygame.K_m:
                    # Toggle between different modes
                    if current_state == STATE_GAME:
                        current_state = STATE_PAUSED
                        print("Game paused")
                    elif current_state == STATE_PAUSED:
                        current_state = STATE_GAME
                        print("Game resumed")
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update head tracker
    head_tracker.update()
    
    # Get head position
    head_angle = head_tracker.get_head_angle()
    head_tilt = head_tracker.get_head_tilt()
    
    # Update game based on current state
    if current_state == STATE_GAME:
        # Get previous game state for sound effects
        previous_speed = racing_game.speed
        previous_collision_time = racing_game.last_collision_time
        
        # Update game state
        racing_game.update(head_angle, head_tilt)
        
        # Play sound effects based on game state changes
        try:
            # Play racing sound when accelerating
            if racing_sound and racing_game.speed > previous_speed + 0.5:
                racing_sound.play()
            
            # Play collision sound when collision occurs
            if collision_sound and racing_game.last_collision_time > previous_collision_time:
                collision_sound.play()
            
            # Play crash sound when game over
            if crash_sound and racing_game.game_over and not racing_game.game_over_sound_played:
                crash_sound.play()
                racing_game.game_over_sound_played = True
        except Exception as e:
            print(f"Error playing sound effects: {e}")
    
    # Render game
    game_surface = racing_game.render()
    screen.blit(game_surface, (0, 0))
    
    # Render camera feed if enabled
    if show_camera:
        try:
            camera_surface = head_tracker.get_frame_surface(CAMERA_WIDTH, CAMERA_HEIGHT)
            screen.blit(camera_surface, (WINDOW_WIDTH - CAMERA_WIDTH, 0))
        except Exception as e:
            print(f"Error rendering camera feed: {e}")
            print(traceback.format_exc())
    
    # Show debug info if enabled
    if show_debug:
        try:
            # Create debug panel
            debug_panel = pygame.Surface((400, 200))
            debug_panel.fill((0, 0, 0))
            
            # Add debug text
            font = pygame.font.Font(None, 24)
            
            # Head tracking info
            head_text = font.render(f"Head Angle: {head_angle:.2f}, Tilt: {head_tilt:.2f}", True, (255, 255, 255))
            debug_panel.blit(head_text, (10, 10))
            
            # Game state info
            state_text = font.render(f"Game State: {'Running' if current_state == STATE_GAME else 'Paused'}", True, (255, 255, 255))
            debug_panel.blit(state_text, (10, 40))
            
            # FPS info
            fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
            debug_panel.blit(fps_text, (10, 70))
            
            # Controls info
            controls_text = font.render("Controls: ESC=Exit, SPACE=Pause, C=Toggle Camera, D=Toggle Debug", True, (255, 255, 255))
            debug_panel.blit(controls_text, (10, 100))
            
            # More controls info
            more_controls_text = font.render("R=Recalibrate, M=Toggle Mode", True, (255, 255, 255))
            debug_panel.blit(more_controls_text, (10, 130))
            
            # Display debug panel
            screen.blit(debug_panel, (0, WINDOW_HEIGHT - 200))
        except Exception as e:
            print(f"Error rendering debug info: {e}")
            print(traceback.format_exc())
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Clean up
pygame.quit()
print("Game exited successfully")
sys.exit(0) 