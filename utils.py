"""
Utility functions for bot development and analysis
"""

import math
from typing import List, Tuple, Dict
import json

# ============================================================================
# ANALYSIS UTILITIES
# ============================================================================

def analyze_game_state(obs: dict) -> Dict:
    """Analyze and summarize game state."""
    player = obs.get('player', 0)
    planets = obs.get('planets', [])
    fleets = obs.get('fleets', [])
    
    # Count by owner
    planet_counts = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}
    ship_counts = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}
    production_totals = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}
    
    for p in planets:
        owner = p[1]
        ships = p[5]
        production = p[6]
        
        planet_counts[owner] = planet_counts.get(owner, 0) + 1
        ship_counts[owner] = ship_counts.get(owner, 0) + ships
        production_totals[owner] = production_totals.get(owner, 0) + production
    
    fleet_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    fleet_ships = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for f in fleets:
        owner = f[1]
        ships = f[6]
        
        fleet_counts[owner] = fleet_counts.get(owner, 0) + 1
        fleet_ships[owner] = fleet_ships.get(owner, 0) + ships
    
    return {
        'step': obs.get('step', 0),
        'player': player,
        'planet_counts': planet_counts,
        'ship_counts': ship_counts,
        'production_totals': production_totals,
        'fleet_counts': fleet_counts,
        'fleet_ships': fleet_ships,
        'total_ships': {
            owner: ship_counts.get(owner, 0) + fleet_ships.get(owner, 0)
            for owner in range(4)
        }
    }

def print_game_summary(obs: dict):
    """Print a human-readable game summary."""
    analysis = analyze_game_state(obs)
    
    print(f"\n{'='*60}")
    print(f"Step {analysis['step']} - Player {analysis['player']}")
    print(f"{'='*60}")
    
    print("\nPlanets by Owner:")
    for owner, count in sorted(analysis['planet_counts'].items()):
        owner_name = "Neutral" if owner == -1 else f"Player {owner}"
        print(f"  {owner_name}: {count} planets")
    
    print("\nProduction by Owner:")
    for owner, prod in sorted(analysis['production_totals'].items()):
        if owner == -1:
            continue
        print(f"  Player {owner}: {prod} ships/turn")
    
    print("\nTotal Ships (Planets + Fleets):")
    for owner, total in sorted(analysis['total_ships'].items()):
        if owner == -1:
            continue
        print(f"  Player {owner}: {total} ships")
    
    print(f"{'='*60}\n")

# ============================================================================
# DEBUGGING UTILITIES
# ============================================================================

def validate_moves(moves: List[List], obs: dict) -> List[str]:
    """Validate moves and return list of errors."""
    errors = []
    player = obs.get('player', 0)
    planets = {p[0]: p for p in obs.get('planets', [])}
    
    for i, move in enumerate(moves):
        if len(move) != 3:
            errors.append(f"Move {i}: Invalid format (need [planet_id, angle, ships])")
            continue
        
        planet_id, angle, ships = move
        
        # Check planet exists
        if planet_id not in planets:
            errors.append(f"Move {i}: Planet {planet_id} does not exist")
            continue
        
        planet = planets[planet_id]
        
        # Check ownership
        if planet[1] != player:
            errors.append(f"Move {i}: Planet {planet_id} not owned by player {player}")
        
        # Check ship count
        if ships > planet[5]:
            errors.append(f"Move {i}: Not enough ships ({ships} > {planet[5]})")
        
        if ships < 0:
            errors.append(f"Move {i}: Negative ships not allowed")
        
        # Check angle
        if not isinstance(angle, (int, float)):
            errors.append(f"Move {i}: Angle must be numeric")
    
    return errors

def log_decision(planet_id: int, target_id: int, ships: int, reason: str):
    """Log a decision for debugging."""
    print(f"[DECISION] Planet {planet_id} -> Planet {target_id}: {ships} ships ({reason})")

# ============================================================================
# PERFORMANCE UTILITIES
# ============================================================================

def profile_agent(agent_func, obs: dict, num_runs: int = 100):
    """Profile agent performance."""
    import time
    
    times = []
    
    for _ in range(num_runs):
        start = time.time()
        agent_func(obs)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"Performance Profile ({num_runs} runs):")
    print(f"  Average: {avg_time*1000:.2f}ms")
    print(f"  Min: {min_time*1000:.2f}ms")
    print(f"  Max: {max_time*1000:.2f}ms")
    print(f"  Budget: 1000ms")
    print(f"  Margin: {(1.0 - avg_time)*1000:.2f}ms")
    
    if avg_time > 0.9:
        print("  WARNING: Close to time limit!")
    
    return avg_time

# ============================================================================
# GEOMETRY HELPERS
# ============================================================================

def point_in_bounds(x: float, y: float, margin: float = 0) -> bool:
    """Check if point is within board bounds."""
    return margin <= x <= 100 - margin and margin <= y <= 100 - margin

def get_quadrant(x: float, y: float) -> int:
    """Get quadrant (0-3) for a point."""
    if x >= 50 and y < 50:
        return 0  # Top-right
    elif x < 50 and y < 50:
        return 1  # Top-left
    elif x < 50 and y >= 50:
        return 2  # Bottom-left
    else:
        return 3  # Bottom-right

def mirror_point(x: float, y: float, quadrant: int) -> Tuple[float, float]:
    """Mirror a point to a different quadrant."""
    # Symmetry: (x, y), (100-x, y), (x, 100-y), (100-x, 100-y)
    if quadrant == 0:
        return x, y
    elif quadrant == 1:
        return 100 - x, y
    elif quadrant == 2:
        return x, 100 - y
    else:
        return 100 - x, 100 - y

# ============================================================================
# CONFIGURATION
# ============================================================================

class BotConfig:
    """Configuration parameters for bot tuning."""
    
    def __init__(self):
        # Aggression
        self.aggression = 0.7  # 0-1, higher = more aggressive
        
        # Fleet sizing
        self.safety_margin = 15
        self.max_fleet_ratio = 0.8  # Max % of planet ships to send
        
        # Target selection
        self.production_weight = 100
        self.distance_weight = 1.5
        self.neutral_bonus = 80
        self.enemy_bonus = 40
        
        # Defense
        self.defense_threshold = 0.6  # Defend if threat > this ratio
        self.defense_reserve = 0.4  # Keep this % when threatened
        
        # Phases
        self.early_game_turns = 100
        self.late_game_turns = 350
    
    def to_dict(self) -> dict:
        """Export config as dictionary."""
        return {
            'aggression': self.aggression,
            'safety_margin': self.safety_margin,
            'max_fleet_ratio': self.max_fleet_ratio,
            'production_weight': self.production_weight,
            'distance_weight': self.distance_weight,
            'neutral_bonus': self.neutral_bonus,
            'enemy_bonus': self.enemy_bonus,
            'defense_threshold': self.defense_threshold,
            'defense_reserve': self.defense_reserve,
            'early_game_turns': self.early_game_turns,
            'late_game_turns': self.late_game_turns,
        }
    
    def save(self, filename: str = "bot_config.json"):
        """Save config to file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filename: str = "bot_config.json"):
        """Load config from file."""
        config = cls()
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        except FileNotFoundError:
            print(f"Config file {filename} not found, using defaults")
        return config
