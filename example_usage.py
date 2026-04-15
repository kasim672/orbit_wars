"""
Example usage of the Orbit Wars bot and utilities
Run this to see how everything works together
"""

# Example 1: Basic bot usage
print("="*60)
print("Example 1: Running the basic bot")
print("="*60)

from submission import agent as basic_agent

# Mock observation (simplified game state)
mock_obs = {
    'player': 0,
    'step': 10,
    'angular_velocity': 0.03,
    'planets': [
        # [id, owner, x, y, radius, ships, production]
        [0, 0, 25, 25, 2.6, 50, 5],    # Our home planet
        [1, -1, 40, 30, 2.0, 20, 3],   # Neutral planet nearby
        [2, -1, 60, 40, 1.6, 15, 2],   # Another neutral
        [3, 1, 75, 75, 2.6, 45, 5],    # Enemy home planet
    ],
    'fleets': [],
    'initial_planets': [
        [0, 0, 25, 25, 2.6, 10, 5],
        [1, -1, 40, 30, 2.0, 20, 3],
        [2, -1, 60, 40, 1.6, 15, 2],
        [3, 1, 75, 75, 2.6, 10, 5],
    ],
    'comet_planet_ids': [],
    'remainingOverageTime': 60.0
}

moves = basic_agent(mock_obs)
print(f"\nBot decided to make {len(moves)} move(s):")
for i, move in enumerate(moves):
    planet_id, angle, ships = move
    print(f"  Move {i+1}: Launch {ships} ships from planet {planet_id} at angle {angle:.2f} radians")

# Example 2: Using utilities
print("\n" + "="*60)
print("Example 2: Analyzing game state")
print("="*60)

from utils import analyze_game_state, print_game_summary, validate_moves

# Analyze the game state
analysis = analyze_game_state(mock_obs)
print(f"\nGame Analysis:")
print(f"  Current step: {analysis['step']}")
print(f"  Your player ID: {analysis['player']}")
print(f"  Planets controlled: {analysis['planet_counts']}")
print(f"  Total ships: {analysis['total_ships']}")

# Validate moves
print("\n" + "="*60)
print("Example 3: Validating moves")
print("="*60)

errors = validate_moves(moves, mock_obs)
if errors:
    print("❌ Found errors in moves:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ All moves are valid!")

# Example 3: Advanced bot
print("\n" + "="*60)
print("Example 4: Running advanced bot")
print("="*60)

from advanced_bot import agent as advanced_agent

# More complex scenario with threats
complex_obs = {
    'player': 0,
    'step': 150,
    'angular_velocity': 0.04,
    'planets': [
        [0, 0, 25, 25, 2.6, 80, 5],    # Our main planet
        [1, 0, 35, 35, 2.0, 40, 3],    # Our second planet
        [2, -1, 50, 30, 1.6, 25, 2],   # Neutral
        [3, 1, 70, 70, 2.6, 60, 5],    # Enemy planet
        [4, 1, 60, 50, 2.0, 30, 3],    # Enemy planet
    ],
    'fleets': [
        # [id, owner, x, y, angle, from_planet_id, ships]
        [0, 1, 45, 40, 3.5, 3, 50],    # Enemy fleet heading toward us!
    ],
    'initial_planets': [
        [0, 0, 25, 25, 2.6, 10, 5],
        [1, 0, 35, 35, 2.0, 10, 3],
        [2, -1, 50, 30, 1.6, 25, 2],
        [3, 1, 70, 70, 2.6, 10, 5],
        [4, 1, 60, 50, 2.0, 10, 3],
    ],
    'comet_planet_ids': [],
    'remainingOverageTime': 55.0
}

advanced_moves = advanced_agent(complex_obs)
print(f"\nAdvanced bot decided to make {len(advanced_moves)} move(s):")
for i, move in enumerate(advanced_moves):
    planet_id, angle, ships = move
    print(f"  Move {i+1}: Launch {ships} ships from planet {planet_id} at angle {angle:.2f} radians")

print("\nNote: Advanced bot detected enemy fleet and may have prioritized defense!")

# Example 4: Math utilities
print("\n" + "="*60)
print("Example 5: Using math utilities")
print("="*60)

from submission import distance, angle_to, fleet_speed, travel_time

# Calculate distance between two planets
p1_x, p1_y = 25, 25
p2_x, p2_y = 75, 75
dist = distance(p1_x, p1_y, p2_x, p2_y)
print(f"\nDistance from (25,25) to (75,75): {dist:.2f} units")

# Calculate angle
angle = angle_to(p1_x, p1_y, p2_x, p2_y)
print(f"Angle from (25,25) to (75,75): {angle:.2f} radians ({angle*180/3.14159:.1f} degrees)")

# Calculate fleet speed for different sizes
print("\nFleet speeds:")
for ships in [1, 10, 50, 100, 500, 1000]:
    speed = fleet_speed(ships)
    time = travel_time(dist, ships)
    print(f"  {ships:4d} ships: speed={speed:.2f} units/turn, travel_time={time:.1f} turns")

# Example 5: Configuration
print("\n" + "="*60)
print("Example 6: Bot configuration")
print("="*60)

from utils import BotConfig

config = BotConfig()
print("\nDefault configuration:")
print(f"  Aggression: {config.aggression}")
print(f"  Safety margin: {config.safety_margin}")
print(f"  Max fleet ratio: {config.max_fleet_ratio}")
print(f"  Production weight: {config.production_weight}")

# Modify and save
config.aggression = 0.9  # More aggressive
config.safety_margin = 10  # Less safety margin
print("\nModified configuration:")
print(f"  Aggression: {config.aggression}")
print(f"  Safety margin: {config.safety_margin}")

# Save to file
config.save("my_config.json")
print("\n✅ Configuration saved to my_config.json")

# Load from file
loaded_config = BotConfig.load("my_config.json")
print(f"✅ Configuration loaded: aggression={loaded_config.aggression}")

# Example 6: Performance profiling
print("\n" + "="*60)
print("Example 7: Performance profiling")
print("="*60)

from utils import profile_agent

print("\nProfiling basic bot (100 runs)...")
avg_time = profile_agent(basic_agent, mock_obs, num_runs=100)

if avg_time < 0.5:
    print("✅ Excellent performance! Plenty of time budget remaining.")
elif avg_time < 0.9:
    print("✅ Good performance. Within time budget.")
else:
    print("⚠️  Warning: Close to time limit. Consider optimization.")

# Summary
print("\n" + "="*60)
print("Summary")
print("="*60)
print("""
You now know how to:
✅ Run the basic bot
✅ Run the advanced bot
✅ Analyze game state
✅ Validate moves
✅ Use math utilities
✅ Configure bot parameters
✅ Profile performance

Next steps:
1. Submit submission.py to Kaggle
2. Watch replays and learn
3. Make improvements
4. Test locally with test_local.py
5. Submit improved versions

Good luck! 🚀
""")
