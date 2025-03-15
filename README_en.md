[中文](README.md)

### Introduction

Head Pose Controlled Racing Game is an interactive project combining computer vision with racing games. Players control the movement direction and speed of a car through head poses captured by the camera. The game screen is divided into two parts: the left side displays real-time video stream and head pose tracking, and the right side displays the racing game.

### Features

- Control car movement using head poses
- Tilt head left/right to control direction
- Tilt head forward to accelerate
- Tilt head backward to decelerate
- Real-time head tracking and pose recognition
- Dynamic curved road with realistic perspective
- Obstacle avoidance with collision detection
- Score system with time-based bonuses
- Visual feedback for acceleration and braking
- Enhanced sound effects for different game events
- Game over condition when score reaches zero
- Temporary message system for game events
- Semi-transparent information panels
- Customizable display options (camera view, debug info)
- Pause/resume functionality
- Recalibration option during gameplay

### Gameplay

1. Position your head in front of the camera
2. Control the car using head poses:
   - Tilt head left: Move car left
   - Tilt head right: Move car right
   - Tilt head forward (away from camera): Accelerate
   - Tilt head backward (closer to camera): Decelerate
3. Avoid obstacles while staying on the track
4. Earn points by surviving longer and avoiding obstacles
5. Lose points when colliding with obstacles or going off-road
6. Game ends when score reaches zero

### Controls

- **Head Pose**: Control car direction and speed
- **SPACE key**: Pause/resume game
- **R key**: Recalibrate head position
- **C key**: Toggle camera view
- **D key**: Toggle debug information
- **M key**: Toggle game mode
- **ESC key**: Exit game

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/head-racing-game.git
   cd head-racing-game
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the game:
   ```
   python run.py
   ```

### Sound Effects

The game includes the following sound effects:
- `background.mp3`: Background music that plays continuously
- `crash.mp3`: Played when the game ends
- `collision.mp3`: Played when the car collides with obstacles or goes off-road
- `racing.mp3`: Played when the car accelerates

Place your sound files in the `sounds` directory with the filenames listed above.

### System Requirements

- Python 3.7+
- Camera
- See `requirements.txt` for Python package dependencies

### Project Structure

```
head-racing-game/
├── sounds/              # Sound effects and music
├── src/                 # Source code
│   ├── game/            # Racing game logic
│   ├── head_tracking/   # Head pose detection
│   └── __init__.py
├── .gitignore           # Git ignore file
├── LICENSE              # MIT license
├── README.md            # Chinese readme
├── README_en.md         # English readme
├── requirements.txt     # Python dependencies
└── run.py               # Main entry point
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 