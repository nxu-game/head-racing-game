import pygame
import random
import math
import numpy as np
import time
import traceback

class RacingGame:
    def __init__(self, width, height):
        """
        Initialize racing game
        
        Args:
            width (int): Game window width
            height (int): Game window height
        """
        print(f"Initializing racing game: width={width}, height={height}")
        
        # Basic settings
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Road parameters
        self.road_width = 300  # Road width
        self.road_center_x = width // 2  # Road center position
        self.road_line_width = 10  # Road center line width
        self.road_line_length = 30  # Road center line length
        self.road_line_gap = 30  # Road center line gap
        self.road_line_offset = 0  # Road center line offset
        
        # Road curve parameters
        self.road_curvature = 0.0  # Current road curvature
        self.target_curve = 0.0  # Target road curvature
        self.max_curvature = 0.3  # Maximum curvature
        self.curvature_change_speed = 0.002  # Curvature change speed
        
        # Road segment parameters
        self.road_segments = []
        self.segment_height = 5  # Reduced segment height for smoother road
        self.num_segments = height // self.segment_height + 10  # Increased segments for continuity
        
        # Game state
        self.distance = 0
        self.speed = 0.0
        self.max_speed = 10.0
        self.min_speed = 0.0
        self.acceleration = 0.05
        self.deceleration = 0.1
        self.friction = 0.01
        self.steering = 0
        self.max_steering = 5
        self.steering_sensitivity = 5.0
        self.car_x = width // 2
        self.car_y = height - 100
        self.car_width = 40
        self.car_height = 70
        self.car_speed_x = 0
        self.score = 100  # Initial score is 100
        self.game_over = False
        self.game_over_sound_played = False  # Flag to track if game over sound has been played
        
        # Time related
        self.start_time = time.time()
        self.last_time_score = time.time()
        self.time_score_interval = 5.0  # Add score every 5 seconds
        self.time_score_amount = 5  # Add 5 points each time
        
        # Obstacles
        self.obstacles = []
        self.obstacle_width = 40
        self.obstacle_height = 60
        self.obstacle_speed = 5
        self.obstacle_spawn_rate = 0.03  # Increased obstacle spawn rate
        self.last_obstacle_time = time.time()
        self.min_obstacle_distance = 100
        
        # Collision penalties
        self.collision_penalty = 10  # Lose 10 points for collision
        self.off_road_penalty = 5    # Lose 5 points for going off-road
        self.last_collision_time = 0  # Last collision time
        self.collision_cooldown = 1.0  # Collision cooldown time (seconds)
        
        # Mountains and clouds
        self.mountains = self.generate_mountains()
        self.clouds = self.generate_clouds()
        
        # Initialize pygame
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)  # Add small font
        
        # Load images
        try:
            self.car_img = pygame.Surface((self.car_width, self.car_height))
            self.car_img.fill((255, 0, 0))  # Red car
            
            self.obstacle_img = pygame.Surface((self.obstacle_width, self.obstacle_height))
            self.obstacle_img.fill((0, 0, 255))  # Blue obstacle
        except Exception as e:
            print(f"Error loading images: {e}")
        
        # Generate initial road segments
        self.generate_road_segments()
        
        # Force generate some initial obstacles
        self._spawn_initial_obstacles()
        
        # Game messages
        self.messages = []  # Store temporary messages
        self.message_duration = 2.0  # Message display time (seconds)
        
        print("Racing game initialization complete")
    
    def generate_road_segments(self):
        """Generate road segments"""
        self.road_segments = []
        
        # Generate road segments from bottom to top
        for i in range(self.num_segments):
            y = self.height - i * self.segment_height
            
            # Randomly generate road curvature
            if random.random() < 0.1:
                self.target_curve = random.uniform(-self.max_curvature, self.max_curvature)
            
            # Smooth transition to target curvature
            if self.road_curvature < self.target_curve:
                self.road_curvature = min(self.road_curvature + self.curvature_change_speed, self.target_curve)
            elif self.road_curvature > self.target_curve:
                self.road_curvature = max(self.road_curvature - self.curvature_change_speed, self.target_curve)
            
            # Add road segment
            self.road_segments.append({
                'y': y,
                'curve': self.road_curvature
            })
    
    def generate_mountains(self):
        """Generate mountains"""
        try:
            mountains = []
            num_mountains = 10
            
            for i in range(num_mountains):
                x = int(i * self.width / num_mountains)
                height = random.randint(20, 50)
                width = random.randint(100, 200)
                mountains.append((x, height, width))
            
            return mountains
        except Exception as e:
            print(f"Error generating mountains: {e}")
            print(traceback.format_exc())
            return []
    
    def generate_clouds(self):
        """Generate clouds"""
        try:
            clouds = []
            num_clouds = 5
            
            for _ in range(num_clouds):
                x = random.randint(0, self.width)
                y = random.randint(20, 100)
                radius = random.randint(20, 40)
                speed = random.uniform(0.2, 0.5)
                clouds.append((x, y, radius, speed))
            
            return clouds
        except Exception as e:
            print(f"Error generating clouds: {e}")
            print(traceback.format_exc())
            return []
    
    def _spawn_initial_obstacles(self):
        """Generate initial obstacles"""
        for i in range(3):  # Generate 3 initial obstacles
            road_left, road_right = self._get_road_boundaries(i * 200)
            obstacle_x = random.uniform(road_left + 20, road_right - self.obstacle_width - 20)
            self.obstacles.append((obstacle_x, i * 200))
    
    def update(self, head_angle, head_tilt):
        """
        Update game state
        
        Args:
            head_angle (float): Head left/right angle, used to control steering
            head_tilt (float): Head forward/backward tilt, used to control acceleration/deceleration
                               Positive value means closer to camera (brake)
                               Negative value means away from camera (accelerate)
        """
        try:
            if self.game_over:
                return
            
            # Update speed (based on head tilt)
            # Head tilting forward (negative value) means accelerate
            # Head tilting backward (positive value) means brake
            if head_tilt < -0.1:  # Head away from camera
                self.speed += self.acceleration * (-head_tilt) * 3  # Increased acceleration coefficient
                self._add_message("Accelerating...")
            elif head_tilt > 0.1:  # Head closer to camera
                self.speed -= self.deceleration * head_tilt * 3  # Increased deceleration coefficient
                self._add_message("Braking...")
            else:
                # Natural deceleration (friction)
                self.speed -= self.friction if self.speed > 0 else -self.friction
            
            # Limit speed range
            self.speed = max(self.min_speed, min(self.max_speed, self.speed))
            
            # Ensure minimum speed to keep the game moving
            if not self.game_over and self.speed < 1.0:
                self.speed = 1.0
            
            # Update road line offset (simulate road movement)
            if self.speed > 0:
                self.road_line_offset += self.speed * 3  # Increased movement speed
                if self.road_line_offset > self.road_line_length + self.road_line_gap:
                    self.road_line_offset = 0
                
                # Update road segments
                for segment in self.road_segments:
                    segment['y'] += self.speed * 3  # Increased movement speed
                
                # Remove road segments that are off-screen
                self.road_segments = [seg for seg in self.road_segments if seg['y'] < self.height + self.segment_height]
                
                # Add new road segments
                while len(self.road_segments) < self.num_segments:
                    # Randomly generate road curvature
                    if random.random() < 0.05:
                        self.target_curve = random.uniform(-self.max_curvature, self.max_curvature)
                    
                    # Smooth transition to target curvature
                    if self.road_curvature < self.target_curve:
                        self.road_curvature = min(self.road_curvature + self.curvature_change_speed, self.target_curve)
                    elif self.road_curvature > self.target_curve:
                        self.road_curvature = max(self.road_curvature - self.curvature_change_speed, self.target_curve)
                    
                    # Add new road segment
                    new_y = self.road_segments[0]['y'] - self.segment_height if self.road_segments else 0
                    self.road_segments.insert(0, {
                        'y': new_y,
                        'curve': self.road_curvature
                    })
            
            # Update car horizontal position (based on head angle and road curvature)
            self.car_speed_x = head_angle * self.steering_sensitivity
            self.car_x += self.car_speed_x
            
            # Get road boundaries at current position
            road_left, road_right = self._get_road_boundaries(self.car_y)
            
            # Check if car is off-road
            if self.car_x < road_left or self.car_x + self.car_width > road_right:
                # If off-road, deduct points
                if time.time() - self.last_collision_time > self.collision_cooldown:
                    self.score -= self.off_road_penalty
                    self.last_collision_time = time.time()
                    self._add_message(f"Off-road! -{self.off_road_penalty} points")
                    print(f"Off-road! -{self.off_road_penalty} points, current score: {self.score}")
            
            # Limit car to road boundaries (but allow slight off-road for player to feel penalty)
            self.car_x = max(road_left - 20, min(road_right - self.car_width + 20, self.car_x))
            
            # Update obstacles
            self._update_obstacles()
            
            # Check collisions
            if self._check_collision():
                # Collision penalty
                if time.time() - self.last_collision_time > self.collision_cooldown:
                    self.score -= self.collision_penalty
                    self.last_collision_time = time.time()
                    self._add_message(f"Collision! -{self.collision_penalty} points")
                    print(f"Collision! -{self.collision_penalty} points, current score: {self.score}")
            
            # Check if game is over (score is 0)
            if self.score <= 0:
                self.score = 0
                self.game_over = True
                self._add_message("Game Over: Score is 0")
                print("Game Over: Score is 0")
            
            # Update clouds
            for i, (x, y, radius, speed) in enumerate(self.clouds):
                x += speed
                if x > self.width + radius:
                    x = -radius
                self.clouds[i] = (x, y, radius, speed)
            
            # Increase score (based on speed)
            if self.speed > 0 and not self.game_over:
                self.score += int(self.speed * 0.01)  # Higher speed means more points
            
            # Increase score based on time
            current_time = time.time()
            if current_time - self.last_time_score >= self.time_score_interval and not self.game_over:
                self.score += self.time_score_amount
                self.last_time_score = current_time
                self._add_message(f"Survival bonus +{self.time_score_amount} points")
                print(f"Survival time bonus: +{self.time_score_amount} points, current score: {self.score}")
            
            # Update messages
            self.messages = [(msg, time_added) for msg, time_added in self.messages 
                            if current_time - time_added < self.message_duration]
        
        except Exception as e:
            print(f"Error updating game state: {e}")
            print(traceback.format_exc())
    
    def _get_road_boundaries(self, y_pos):
        """Get road boundaries at specified position"""
        # Find closest road segment
        closest_segment = None
        min_distance = float('inf')
        
        for segment in self.road_segments:
            distance = abs(segment['y'] - y_pos)
            if distance < min_distance:
                min_distance = distance
                closest_segment = segment
        
        if closest_segment:
            # Calculate road center position (based on curvature)
            center_x = self.road_center_x + closest_segment['curve'] * (y_pos / self.height) * 200
            
            # Calculate road boundaries
            left_boundary = center_x - self.road_width // 2
            right_boundary = center_x + self.road_width // 2
            
            return left_boundary, right_boundary
        
        # Default return
        return self.road_center_x - self.road_width // 2, self.road_center_x + self.road_width // 2
    
    def _update_obstacles(self):
        """Update obstacles"""
        try:
            # Move existing obstacles
            new_obstacles = []
            for x, y in self.obstacles:
                y += self.speed * 3  # Increased obstacle movement speed to match road movement
                
                # If obstacle is still on screen, keep it
                if y < self.height:
                    new_obstacles.append((x, y))
                else:
                    # Obstacle left screen, add small score
                    self.score += 1
                    self._add_message("Avoided obstacle +1 point")
            
            self.obstacles = new_obstacles
            
            # Generate new obstacles
            current_time = time.time()
            if (current_time - self.last_obstacle_time > 1.0 and 
                random.random() < self.obstacle_spawn_rate and 
                self.speed > 0.5):  # Lower speed threshold for generating obstacles
                
                # Ensure new obstacles maintain distance from existing ones
                can_spawn = True
                if self.obstacles:
                    for _, y in self.obstacles:
                        if y < self.min_obstacle_distance:
                            can_spawn = False
                            break
                
                if can_spawn:
                    # Get road boundaries
                    road_left, road_right = self._get_road_boundaries(0)
                    
                    # Randomly generate obstacle within road
                    obstacle_x = random.uniform(road_left + 20, road_right - self.obstacle_width - 20)
                    self.obstacles.append((obstacle_x, 0))
                    self.last_obstacle_time = current_time
                    print(f"Generated obstacle: x={obstacle_x}, y=0")
        
        except Exception as e:
            print(f"Error updating obstacles: {e}")
            print(traceback.format_exc())
    
    def _check_collision(self):
        """Check collisions"""
        try:
            # Get car collision rectangle
            car_rect = pygame.Rect(int(self.car_x), int(self.car_y), self.car_width, self.car_height)
            
            # Check collision with obstacles
            for i, (x, y) in enumerate(self.obstacles[:]):
                obstacle_rect = pygame.Rect(int(x), int(y), self.obstacle_width, self.obstacle_height)
                if car_rect.colliderect(obstacle_rect):
                    print(f"Collision with obstacle: car position=({self.car_x}, {self.car_y}), obstacle position=({x}, {y})")
                    # Remove collided obstacle
                    self.obstacles.pop(i)
                    return True
            
            # Check if severely off-road
            road_left, road_right = self._get_road_boundaries(self.car_y)
            
            if self.car_x + self.car_width < road_left - 50 or self.car_x > road_right + 50:
                print(f"Severely off-road: car position=({self.car_x}, {self.car_y}), road boundaries=({road_left}, {road_right})")
                self.score -= self.off_road_penalty * 2  # Severely off-road, double penalty
                return True
            
            return False
        
        except Exception as e:
            print(f"Error checking collisions: {e}")
            print(traceback.format_exc())
            return False
    
    def render(self):
        """
        Render game
        
        Returns:
            pygame.Surface: Rendered game surface
        """
        try:
            # Clear screen
            self.surface.fill((135, 206, 235))  # Sky blue
            
            # Draw mountains
            for x, height, width in self.mountains:
                pygame.draw.polygon(
                    self.surface,
                    (100, 100, 100),  # Gray
                    [
                        (x, self.height // 3),
                        (x + width // 2, self.height // 3 - height),
                        (x + width, self.height // 3)
                    ]
                )
            
            # Draw clouds
            for x, y, radius, _ in self.clouds:
                pygame.draw.circle(self.surface, (255, 255, 255), (int(x), int(y)), radius)
                pygame.draw.circle(self.surface, (255, 255, 255), (int(x + radius * 0.7), int(y)), int(radius * 0.8))
                pygame.draw.circle(self.surface, (255, 255, 255), (int(x - radius * 0.7), int(y)), int(radius * 0.8))
            
            # Draw grass
            pygame.draw.rect(
                self.surface,
                (34, 139, 34),  # Forest green
                (0, self.height // 3, self.width, self.height)
            )
            
            # Draw curved road
            self._draw_curved_road()
            
            # Draw obstacles
            for x, y in self.obstacles:
                self.surface.blit(self.obstacle_img, (int(x), int(y)))
            
            # Draw player car
            self.surface.blit(self.car_img, (int(self.car_x), int(self.car_y)))
            
            # Create semi-transparent info panel
            info_panel = pygame.Surface((200, 150), pygame.SRCALPHA)
            info_panel.fill((0, 0, 0, 128))  # Semi-transparent black
            self.surface.blit(info_panel, (10, 10))
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.surface.blit(score_text, (20, 20))
            
            # Draw speed
            speed_text = self.font.render(f"Speed: {int(self.speed * 10)} km/h", True, (255, 255, 255))
            self.surface.blit(speed_text, (20, 60))
            
            # Draw road curvature
            curve_text = self.small_font.render(f"Road Curvature: {self.road_curvature:.2f}", True, (255, 255, 255))
            self.surface.blit(curve_text, (20, 100))
            
            # Draw game time
            game_time = int(time.time() - self.start_time)
            time_text = self.small_font.render(f"Game Time: {game_time}s", True, (255, 255, 255))
            self.surface.blit(time_text, (20, 130))
            
            # Draw temporary messages
            self._draw_messages()
            
            # Draw control hints
            self._draw_control_hints()
            
            # If game over, show game over text
            if self.game_over:
                self._draw_game_over()
            
            return self.surface
        
        except Exception as e:
            print(f"Error rendering game: {e}")
            print(traceback.format_exc())
            
            # Create an error screen
            error_surface = pygame.Surface((self.width, self.height))
            error_surface.fill((0, 0, 0))  # Black background
            
            # Show error message
            error_text = self.font.render(f"Rendering Error: {str(e)}", True, (255, 0, 0))
            error_surface.blit(error_text, (20, 20))
            
            return error_surface
    
    def _draw_messages(self):
        """Draw temporary messages"""
        # Show messages in top-right corner
        y_offset = 20
        for message, _ in self.messages:
            msg_surface = self.small_font.render(message, True, (255, 255, 0))
            self.surface.blit(msg_surface, (self.width - msg_surface.get_width() - 20, y_offset))
            y_offset += 30
    
    def _draw_curved_road(self):
        """Draw curved road"""
        try:
            # Ensure road segments are sorted by y-coordinate
            sorted_segments = sorted(self.road_segments, key=lambda seg: seg['y'])
            
            # Draw each road segment
            for i, segment in enumerate(sorted_segments):
                y = segment['y']
                curve = segment['curve']
                
                # Calculate road center position
                center_x = self.road_center_x + curve * (y / self.height) * 200
                
                # Calculate road boundaries
                left_boundary = center_x - self.road_width // 2
                right_boundary = center_x + self.road_width // 2
                
                # Draw road segment
                pygame.draw.rect(
                    self.surface,
                    (128, 128, 128),  # Gray
                    (left_boundary, y, self.road_width, self.segment_height)
                )
                
                # Draw road edge lines
                pygame.draw.line(
                    self.surface,
                    (255, 255, 255),  # White
                    (left_boundary, y),
                    (left_boundary, y + self.segment_height),
                    2
                )
                pygame.draw.line(
                    self.surface,
                    (255, 255, 255),  # White
                    (right_boundary, y),
                    (right_boundary, y + self.segment_height),
                    2
                )
                
                # Draw center line
                if (y + int(self.road_line_offset)) % (self.road_line_length + self.road_line_gap) < self.road_line_length:
                    pygame.draw.rect(
                        self.surface,
                        (255, 255, 0),  # Yellow
                        (center_x - self.road_line_width // 2, y, self.road_line_width, 10)
                    )
        except Exception as e:
            print(f"Error drawing curved road: {e}")
            print(traceback.format_exc())
    
    def _draw_game_over(self):
        """Draw game over screen"""
        try:
            # Create semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.surface.blit(overlay, (0, 0))
            
            # Draw game over text
            game_over_text = self.font.render("Game Over", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.surface.blit(game_over_text, text_rect)
            
            # Draw final score
            score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
            self.surface.blit(score_text, score_rect)
            
            # Draw game time
            game_time = int(time.time() - self.start_time)
            time_text = self.font.render(f"Game Time: {game_time}s", True, (255, 255, 255))
            time_rect = time_text.get_rect(center=(self.width // 2, self.height // 2 + 40))
            self.surface.blit(time_text, time_rect)
            
            # Draw restart hint
            restart_text = self.font.render("Press ESC to exit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
            self.surface.blit(restart_text, restart_rect)
        
        except Exception as e:
            print(f"Error drawing game over screen: {e}")
    
    def draw_text(self, text, size, x, y, color=(255, 255, 255)):
        """
        Draw text on game surface
        
        Args:
            text (str): Text to draw
            size (int): Font size
            x (int): x coordinate
            y (int): y coordinate
            color (tuple, optional): Text color. Defaults to (255, 255, 255).
        """
        try:
            font = pygame.font.Font(None, size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (x, y)
            self.surface.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error drawing text: {e}")
            print(traceback.format_exc())
    
    def _add_message(self, message):
        """Add temporary message"""
        self.messages.append((message, time.time())) 

    def _draw_control_hints(self):
        """Draw control hints"""
        # Create semi-transparent control hint panel
        hint_panel = pygame.Surface((250, 80), pygame.SRCALPHA)
        hint_panel.fill((0, 0, 0, 128))  # Semi-transparent black
        self.surface.blit(hint_panel, (self.width - 260, self.height - 90))
        
        # Draw control hints
        tilt_text = self.small_font.render("Head closer to camera = Brake", True, (255, 255, 255))
        self.surface.blit(tilt_text, (self.width - 250, self.height - 80))
        
        tilt_text2 = self.small_font.render("Head away from camera = Accelerate", True, (255, 255, 255))
        self.surface.blit(tilt_text2, (self.width - 250, self.height - 60))
        
        angle_text = self.small_font.render("Head tilt left/right = Steering", True, (255, 255, 255))
        self.surface.blit(angle_text, (self.width - 250, self.height - 40)) 