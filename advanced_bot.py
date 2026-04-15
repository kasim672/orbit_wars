"""
Advanced Orbit Wars Bot with Enhanced Strategy
This version includes:
- Orbital prediction
- Defense logic
- Combat simulation
- Multi-fleet coordination
- Comet strategies
"""

import math
from typing import List, Tuple, Optional, Dict, Set
from collections import defaultdict

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

class ThreatAssessment:
    def __init__(self, planet_id: int, incoming_ships: int, eta: float, attacker: int):
        self.planet_id = planet_id
        self.incoming_ships = incoming_ships
        self.eta = eta
        self.attacker = attacker

# ============================================================================
# MATH UTILITIES
# ============================================================================

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def angle_to(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle from point 1 to point 2 in radians."""
    return math.atan2(y2 - y1, x2 - x1)

def normalize_angle(angle: float) -> float:
    """Normalize angle to [-pi, pi]."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

def fleet_speed(num_ships: int, max_speed: float = MAX_SPEED) -> float:
    """Calculate fleet speed based on ship count."""
    if num_ships <= 0:
        return 1.0
    return 1.0 + (max_speed - 1.0) * (math.log(num_ships) / math.log(1000)) ** 1.5

def travel_time(dist: float, num_ships: int) -> float:
    """Calculate travel time for a fleet."""
    speed = fleet_speed(num_ships)
    return dist / speed if speed > 0 else float('inf')

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

def calculate_intercept_angle(source_x: float, source_y: float, 
                             target_x: float, target_y: float,
                             target_vx: float, target_vy: float,
                             fleet_ships: int, max_iterations: int = 10) -> Optional[float]:
    """
    Calculate angle to intercept a moving target.
    Uses iterative approach to find intercept point.
    """
    speed = fleet_speed(fleet_ships)
    
    for _ in range(max_iterations):
        # Calculate time to reach target
        dx = target_x - source_x
        dy = target_y - source_y
        dist = math.sqrt(dx * dx + dy * dy)
        time = dist / speed
        
        # Predict target position at that time
        future_x = target_x + target_vx * time
        future_y = target_y + target_vy * time
        
        # Update target position for next iteration
        target_x = future_x
        target_y = future_y
    
    return angle_to(source_x, source_y, target_x, target_y)

def line_intersects_circle(x1: float, y1: float, x2: float, y2: float,
                          cx: float, cy: float, radius: float) -> bool:
    """Check if line segment intersects with circle."""
    dx = x2 - x1
    dy = y2 - y1
    fx = x1 - cx
    fy = y1 - cy
    
    a = dx * dx + dy * dy
    if a < 1e-10:  # Points are the same
        return distance(x1, y1, cx, cy) <= radius
    
    b = 2 * (fx * dx + fy * dy)
    c = (fx * fx + fy * fy) - radius * radius
    
    discriminant = b * b - 4 * a * c
    
    if discriminant < 0:
        return False
    
    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)
    
    return (0 <= t1 <= 1) or (0 <= t2 <= 1) or (t1 < 0 and t2 > 1)

def path_crosses_sun(x1: float, y1: float, x2: float, y2: float) -> bool:
    """Check if path crosses the sun."""
    return line_intersects_circle(x1, y1, x2, y2, CENTER[0], CENTER[1], SUN_RADIUS)

def find_safe_angle(source_x: float, source_y: float, 
                   target_x: float, target_y: float,
                   num_samples: int = 16) -> Optional[float]:
    """Find a safe angle that avoids the sun."""
    direct_angle = angle_to(source_x, source_y, target_x, target_y)
    
    # Check direct path first
    if not path_crosses_sun(source_x, source_y, target_x, target_y):
        return direct_angle
    
    # Try angles around the direct path
    for offset in [math.pi/8, -math.pi/8, math.pi/4, -math.pi/4, math.pi/3, -math.pi/3]:
        test_angle = direct_angle + offset
        # Project a point far in that direction
        test_x = source_x + math.cos(test_angle) * 100
        test_y = source_y + math.sin(test_angle) * 100
        
        if not path_crosses_sun(source_x, source_y, test_x, test_y):
            return test_angle
    
    return None  # No safe path found

# ============================================================================
# COMBAT SIMULATION
# ============================================================================

def simulate_combat(attackers: Dict[int, int], defender_owner: int, 
                   defender_ships: int) -> Tuple[int, int]:
    """
    Simulate combat and return (winner_owner, remaining_ships).
    Returns (-1, 0) if all destroyed.
    """
    if not attackers:
        return defender_owner, defender_ships
    
    # Group attackers by owner
    attacker_forces = list(attackers.items())
    attacker_forces.sort(key=lambda x: x[1], reverse=True)
    
    # Largest vs second largest
    if len(attacker_forces) >= 2:
        largest = attacker_forces[0]
        second = attacker_forces[1]
        
        if largest[1] > second[1]:
            survivor_owner = largest[0]
            survivor_ships = largest[1] - second[1]
        else:
            # Tie - all attackers destroyed
            return defender_owner, defender_ships
    else:
        survivor_owner = attacker_forces[0][0]
        survivor_ships = attacker_forces[0][1]
    
    # Survivor fights defender
    if survivor_owner == defender_owner:
        return defender_owner, defender_ships + survivor_ships
    else:
        if survivor_ships > defender_ships:
            return survivor_owner, survivor_ships - defender_ships
        else:
            return defender_owner, defender_ships - survivor_ships

# ============================================================================
# GAME STATE ANALYSIS
# ============================================================================

class GameState:
    def __init__(self, obs: dict):
        self.obs = obs
        self.player = obs.get('player', 0)
        self.angular_velocity = obs.get('angular_velocity', 0.0)
        self.comet_planet_ids = set(obs.get('comet_planet_ids', []))
        self.step = obs.get('step', 0)
        
        # Parse planets
        self.planets = [Planet(*p) for p in obs.get('planets', [])]
        self.initial_planets = [Planet(*p) for p in obs.get('initial_planets', [])]
        
        # Parse fleets
        self.fleets = [Fleet(*f) for f in obs.get('fleets', [])]
        
        # Categorize planets
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner != self.player and p.owner != -1]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]
        
        # Build lookups
        self.planet_by_id = {p.id: p for p in self.planets}
        self.initial_planet_by_id = {p.id: p for p in self.initial_planets}
        
        # Analyze threats
        self.threats = self._analyze_threats()
    
    def get_predicted_position(self, planet: Planet, turns: int) -> Tuple[float, float]:
        """Get predicted position of planet after N turns."""
        initial = self.initial_planet_by_id.get(planet.id, planet)
        return predict_planet_position(planet, initial, self.angular_velocity, turns)
    
    def is_orbiting(self, planet: Planet) -> bool:
        """Check if planet is orbiting."""
        initial = self.initial_planet_by_id.get(planet.id, planet)
        dist_to_center = distance(initial.x, initial.y, CENTER[0], CENTER[1])
        return dist_to_center + planet.radius < ROTATION_RADIUS_LIMIT
    
    def _analyze_threats(self) -> Dict[int, List[ThreatAssessment]]:
        """Analyze incoming threats to our planets."""
        threats = defaultdict(list)
        
        for fleet in self.fleets:
            if fleet.owner == self.player:
                continue  # Our own fleet
            
            # Check which planet this fleet might hit
            for planet in self.my_planets:
                # Simple check: is fleet heading toward planet?
                dist = distance(fleet.x, fleet.y, planet.x, planet.y)
                angle_to_planet = angle_to(fleet.x, fleet.y, planet.x, planet.y)
                angle_diff = abs(normalize_angle(fleet.angle - angle_to_planet))
                
                # If fleet is roughly heading toward planet
                if angle_diff < math.pi / 4 and dist < 50:
                    eta = travel_time(dist, fleet.ships)
                    threats[planet.id].append(
                        ThreatAssessment(planet.id, fleet.ships, eta, fleet.owner)
                    )
        
        return threats
    
    def total_ships(self, owner: int) -> int:
        """Calculate total ships for a player."""
        planet_ships = sum(p.ships for p in self.planets if p.owner == owner)
        fleet_ships = sum(f.ships for f in self.fleets if f.owner == owner)
        return planet_ships + fleet_ships
    
    def get_game_phase(self) -> str:
        """Determine current game phase."""
        if self.step < 100:
            return "early"
        elif self.step < 350:
            return "mid"
        else:
            return "late"

# ============================================================================
# ADVANCED STRATEGY
# ============================================================================

class AdvancedStrategy:
    def __init__(self, game_state: GameState):
        self.gs = game_state
        self.phase = game_state.get_game_phase()
    
    def evaluate_target(self, source: Planet, target: Planet) -> float:
        """Evaluate how good a target is (higher = better)."""
        # Calculate distance
        dist = distance(source.x, source.y, target.x, target.y)
        
        # Estimate ships needed
        ships_needed = target.ships + 1
        time = travel_time(dist, ships_needed)
        
        # Account for production during travel
        if target.owner != -1:
            ships_needed += int(target.production * time)
        
        if ships_needed > source.ships * 0.8:
            return -1000  # Too expensive
        
        # Check sun collision
        if path_crosses_sun(source.x, source.y, target.x, target.y):
            safe_angle = find_safe_angle(source.x, source.y, target.x, target.y)
            if safe_angle is None:
                return -1000  # No safe path
        
        # Calculate value
        production_value = target.production * 100
        
        # Distance penalty (non-linear)
        distance_penalty = dist * 1.5
        
        # Ship cost
        ship_cost = ships_needed * 0.5
        
        # Neutral bonus
        neutral_bonus = 80 if target.owner == -1 else 0
        
        # Enemy bonus (disrupting enemy is valuable)
        enemy_bonus = 40 if target.owner != -1 and target.owner != self.gs.player else 0
        
        # High production bonus
        high_prod_bonus = 50 if target.production >= 4 else 0
        
        # Comet penalty (they leave)
        comet_penalty = 100 if target.id in self.gs.comet_planet_ids else 0
        
        # Phase-specific adjustments
        if self.phase == "early":
            neutral_bonus *= 1.5  # Prioritize expansion
        elif self.phase == "late":
            enemy_bonus *= 2  # Prioritize disruption
        
        score = (production_value + neutral_bonus + enemy_bonus + high_prod_bonus 
                - distance_penalty - ship_cost - comet_penalty)
        
        return score
    
    def select_targets(self, source: Planet, max_targets: int = 3) -> List[Tuple[Planet, float]]:
        """Select multiple targets ranked by score."""
        targets = self.gs.neutral_planets + self.gs.enemy_planets
        
        if not targets:
            return []
        
        scored_targets = []
        for target in targets:
            score = self.evaluate_target(source, target)
            if score > 0:
                scored_targets.append((target, score))
        
        scored_targets.sort(key=lambda x: x[1], reverse=True)
        return scored_targets[:max_targets]
    
    def calculate_fleet_size(self, source: Planet, target: Planet, 
                           aggressive: bool = False) -> int:
        """Calculate optimal fleet size to send."""
        dist = distance(source.x, source.y, target.x, target.y)
        base_needed = target.ships + 1
        time = travel_time(dist, base_needed)
        
        # Account for production
        production_buffer = int(target.production * time * 1.2) if target.owner != -1 else 0
        
        # Safety margin
        safety = 10 if aggressive else 20
        
        total_needed = base_needed + production_buffer + safety
        
        # Check for threats to source
        if source.id in self.gs.threats:
            # Keep more for defense
            max_send = int(source.ships * 0.6)
        else:
            max_send = int(source.ships * 0.85)
        
        return min(total_needed, max_send, source.ships - 5)
    
    def should_defend(self, planet: Planet) -> Optional[Tuple[int, float]]:
        """Check if planet needs defense. Returns (ships_needed, urgency)."""
        if planet.id not in self.gs.threats:
            return None
        
        threats = self.gs.threats[planet.id]
        if not threats:
            return None
        
        # Calculate total incoming
        total_incoming = sum(t.incoming_ships for t in threats)
        
        # Calculate our strength at arrival
        min_eta = min(t.eta for t in threats)
        our_ships = planet.ships + int(planet.production * min_eta)
        
        if total_incoming > our_ships:
            ships_needed = total_incoming - our_ships + 10
            urgency = min_eta
            return (ships_needed, urgency)
        
        return None
    
    def find_reinforcement_source(self, target_planet: Planet, 
                                  ships_needed: int) -> Optional[Planet]:
        """Find best planet to send reinforcements from."""
        candidates = []
        
        for planet in self.gs.my_planets:
            if planet.id == target_planet.id:
                continue
            if planet.ships < ships_needed + 10:
                continue
            
            dist = distance(planet.x, planet.y, target_planet.x, target_planet.y)
            time = travel_time(dist, ships_needed)
            
            # Score based on distance and available ships
            score = planet.ships / (dist + 1)
            candidates.append((planet, score, time))
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

# ============================================================================
# MAIN AGENT
# ============================================================================

def agent(obs: dict) -> List[List]:
    """
    Advanced agent with defense, orbital prediction, and multi-target coordination.
    """
    gs = GameState(obs)
    strategy = AdvancedStrategy(gs)
    
    moves = []
    used_planets = set()
    
    # Phase 1: Handle defense
    for planet in gs.my_planets:
        if planet.id in used_planets:
            continue
        
        defense_needed = strategy.should_defend(planet)
        if defense_needed:
            ships_needed, urgency = defense_needed
            
            # Find reinforcement
            source = strategy.find_reinforcement_source(planet, ships_needed)
            if source and urgency < 10:  # Only if we have time
                angle = angle_to(source.x, source.y, planet.x, planet.y)
                moves.append([source.id, angle, min(ships_needed, source.ships - 10)])
                used_planets.add(source.id)
    
    # Phase 2: Offensive moves
    for planet in gs.my_planets:
        if planet.id in used_planets:
            continue
        
        if planet.ships < 15:
            continue
        
        # Skip comets unless early game
        if planet.id in gs.comet_planet_ids and gs.step > 100:
            continue
        
        # Get best targets
        targets = strategy.select_targets(planet, max_targets=1)
        
        if not targets:
            continue
        
        target, score = targets[0]
        
        # Calculate fleet
        fleet_size = strategy.calculate_fleet_size(planet, target)
        
        if fleet_size < 5:
            continue
        
        # Calculate angle (with orbital prediction if needed)
        if gs.is_orbiting(target):
            # Predict target position
            dist = distance(planet.x, planet.y, target.x, target.y)
            eta = travel_time(dist, fleet_size)
            future_x, future_y = gs.get_predicted_position(target, int(eta))
            angle = angle_to(planet.x, planet.y, future_x, future_y)
        else:
            angle = angle_to(planet.x, planet.y, target.x, target.y)
        
        # Check for sun and find safe path if needed
        if path_crosses_sun(planet.x, planet.y, target.x, target.y):
            safe_angle = find_safe_angle(planet.x, planet.y, target.x, target.y)
            if safe_angle is not None:
                angle = safe_angle
            else:
                continue  # Skip if no safe path
        
        moves.append([planet.id, angle, fleet_size])
        used_planets.add(planet.id)
    
    return moves
