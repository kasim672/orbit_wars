"""
Orbit Wars Competition Bot
Main submission file for Kaggle
"""

import math
from typing import List, Tuple, Optional

# ============================================================================
# CONSTANTS
# ============================================================================

CENTER = (50.0, 50.0)
SUN_RADIUS = 10.0
BOARD_SIZE = 100.0
MAX_SPEED = 6.0
ROTATION_RADIUS_LIMIT = 50.0

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class Planet:
    def __init__(self, id, owner, x, y, radius, ships, production):
        self.id = id
        self.owner = owner
        self.x = x
        self.y = y
        self.radius = radius
        self.ships = ships
        self.production = production
    
    def __repr__(self):
        return f"Planet({self.id}, owner={self.owner}, pos=({self.x:.1f},{self.y:.1f}), ships={self.ships})"

class Fleet:
    def __init__(self, id, owner, x, y, angle, from_planet_id, ships):
        self.id = id
        self.owner = owner
        self.x = x
        self.y = y
        self.angle = angle
        self.from_planet_id = from_planet_id
        self.ships = ships
    
    def __repr__(self):
        return f"Fleet({self.id}, owner={self.owner}, ships={self.ships})"

# ============================================================================
# MATH UTILITIES
# ============================================================================

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def angle_to(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle from point 1 to point 2 in radians."""
    return math.atan2(y2 - y1, x2 - x1)

def fleet_speed(num_ships: int, max_speed: float = MAX_SPEED) -> float:
    """Calculate fleet speed based on ship count."""
    if num_ships <= 0:
        return 1.0
    return 1.0 + (max_speed - 1.0) * (math.log(num_ships) / math.log(1000)) ** 1.5

def travel_time(dist: float, num_ships: int) -> float:
    """Calculate travel time for a fleet."""
    speed = fleet_speed(num_ships)
    return dist / speed

def predict_planet_position(planet: Planet, initial_planet: Planet, 
                           angular_velocity: float, turns: int) -> Tuple[float, float]:
    """Predict future position of an orbiting planet."""
    # Check if planet orbits
    dist_to_center = distance(initial_planet.x, initial_planet.y, CENTER[0], CENTER[1])
    if dist_to_center + planet.radius >= ROTATION_RADIUS_LIMIT:
        # Static planet
        return planet.x, planet.y
    
    # Calculate current angle from center
    current_angle = math.atan2(planet.y - CENTER[1], planet.x - CENTER[0])
    
    # Predict future angle
    future_angle = current_angle + angular_velocity * turns
    
    # Calculate future position
    radius = dist_to_center
    future_x = CENTER[0] + radius * math.cos(future_angle)
    future_y = CENTER[1] + radius * math.sin(future_angle)
    
    return future_x, future_y

def line_intersects_circle(x1: float, y1: float, x2: float, y2: float,
                          cx: float, cy: float, radius: float) -> bool:
    """Check if line segment intersects with circle."""
    # Vector from point 1 to point 2
    dx = x2 - x1
    dy = y2 - y1
    
    # Vector from point 1 to circle center
    fx = x1 - cx
    fy = y1 - cy
    
    # Quadratic equation coefficients
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = (fx * fx + fy * fy) - radius * radius
    
    discriminant = b * b - 4 * a * c
    
    if discriminant < 0:
        return False
    
    # Check if intersection is within segment
    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)
    
    return (0 <= t1 <= 1) or (0 <= t2 <= 1) or (t1 < 0 and t2 > 1)

def path_crosses_sun(x1: float, y1: float, x2: float, y2: float) -> bool:
    """Check if path crosses the sun."""
    return line_intersects_circle(x1, y1, x2, y2, CENTER[0], CENTER[1], SUN_RADIUS)

# ============================================================================
# GAME STATE ANALYSIS
# ============================================================================

class GameState:
    def __init__(self, obs: dict):
        self.obs = obs
        self.player = obs.get('player', 0)
        self.angular_velocity = obs.get('angular_velocity', 0.0)
        self.comet_planet_ids = set(obs.get('comet_planet_ids', []))
        
        # Parse planets
        self.planets = [Planet(*p) for p in obs.get('planets', [])]
        self.initial_planets = [Planet(*p) for p in obs.get('initial_planets', [])]
        
        # Parse fleets
        self.fleets = [Fleet(*f) for f in obs.get('fleets', [])]
        
        # Categorize planets
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner != self.player and p.owner != -1]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]
        
        # Build planet lookup
        self.planet_by_id = {p.id: p for p in self.planets}
        self.initial_planet_by_id = {p.id: p for p in self.initial_planets}
    
    def get_predicted_position(self, planet: Planet, turns: int) -> Tuple[float, float]:
        """Get predicted position of planet after N turns."""
        initial = self.initial_planet_by_id.get(planet.id, planet)
        return predict_planet_position(planet, initial, self.angular_velocity, turns)
    
    def total_ships(self, owner: int) -> int:
        """Calculate total ships for a player."""
        planet_ships = sum(p.ships for p in self.planets if p.owner == owner)
        fleet_ships = sum(f.ships for f in self.fleets if f.owner == owner)
        return planet_ships + fleet_ships

# ============================================================================
# STRATEGY
# ============================================================================

class Strategy:
    def __init__(self, game_state: GameState):
        self.gs = game_state
    
    def evaluate_target(self, source: Planet, target: Planet) -> float:
        """Evaluate how good a target is (higher = better)."""
        # Calculate distance and travel time
        dist = distance(source.x, source.y, target.x, target.y)
        ships_needed = target.ships + 1
        
        if ships_needed > source.ships:
            return -1000  # Can't attack
        
        time = travel_time(dist, ships_needed)
        
        # Check if path crosses sun
        if path_crosses_sun(source.x, source.y, target.x, target.y):
            return -1000  # Unsafe path
        
        # Score based on production value and cost
        production_value = target.production * 100
        distance_penalty = dist * 2
        ship_cost = ships_needed * 1
        
        # Bonus for neutral planets (easier to capture)
        neutral_bonus = 50 if target.owner == -1 else 0
        
        score = production_value + neutral_bonus - distance_penalty - ship_cost
        
        return score
    
    def select_best_target(self, source: Planet) -> Optional[Planet]:
        """Select the best target planet to attack from source."""
        targets = self.gs.neutral_planets + self.gs.enemy_planets
        
        if not targets:
            return None
        
        best_target = None
        best_score = -float('inf')
        
        for target in targets:
            score = self.evaluate_target(source, target)
            if score > best_score:
                best_score = score
                best_target = target
        
        return best_target if best_score > 0 else None
    
    def calculate_fleet_size(self, source: Planet, target: Planet) -> int:
        """Calculate optimal fleet size to send."""
        # Base requirement: enough to conquer
        base_needed = target.ships + 1
        
        # Add buffer for production during travel
        dist = distance(source.x, source.y, target.x, target.y)
        time = travel_time(dist, base_needed)
        production_buffer = int(target.production * time) if target.owner != -1 else 0
        
        total_needed = base_needed + production_buffer + 5  # +5 safety margin
        
        # Don't send more than 80% of garrison (keep some defense)
        max_send = int(source.ships * 0.8)
        
        return min(total_needed, max_send)

# ============================================================================
# MAIN AGENT
# ============================================================================

def agent(obs: dict) -> List[List]:
    """
    Main agent function called each turn.
    Returns list of moves: [[from_planet_id, angle, num_ships], ...]
    """
    # Parse game state
    gs = GameState(obs)
    strategy = Strategy(gs)
    
    moves = []
    
    # For each of our planets, consider launching attacks
    for planet in gs.my_planets:
        # Skip if planet has too few ships
        if planet.ships < 10:
            continue
        
        # Skip comets (they might leave soon)
        if planet.id in gs.comet_planet_ids:
            continue
        
        # Find best target
        target = strategy.select_best_target(planet)
        
        if target is None:
            continue
        
        # Calculate fleet size
        fleet_size = strategy.calculate_fleet_size(planet, target)
        
        if fleet_size < 5:  # Don't send tiny fleets
            continue
        
        # Calculate angle to target
        angle = angle_to(planet.x, planet.y, target.x, target.y)
        
        # Add move
        moves.append([planet.id, angle, fleet_size])
    
    return moves
