"""
Elite Orbit Wars Bot - Target: 3500+ Rating
Advanced features: Defense, prediction, optimization, coordination
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
# CORE DATA STRUCTURES
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

class Fleet:
    def __init__(self, id, owner, x, y, angle, from_planet_id, ships):
        self.id = id
        self.owner = owner
        self.x = x
        self.y = y
        self.angle = angle
        self.from_planet_id = from_planet_id
        self.ships = ships

# ============================================================================
# MATH UTILITIES
# ============================================================================

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def angle_to(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.atan2(y2 - y1, x2 - x1)

def normalize_angle(angle: float) -> float:
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

def fleet_speed(num_ships: int) -> float:
    if num_ships <= 0:
        return 1.0
    return 1.0 + (MAX_SPEED - 1.0) * (math.log(num_ships) / math.log(1000)) ** 1.5

def travel_time(dist: float, num_ships: int) -> float:
    speed = fleet_speed(num_ships)
    return dist / speed if speed > 0 else float('inf')

def predict_planet_position(px: float, py: float, angular_velocity: float, turns: int) -> Tuple[float, float]:
    """Predict future position of orbiting planet."""
    dist_to_center = distance(px, py, CENTER[0], CENTER[1])
    if dist_to_center >= ROTATION_RADIUS_LIMIT - 5:
        return px, py
    
    current_angle = math.atan2(py - CENTER[1], px - CENTER[0])
    future_angle = current_angle + angular_velocity * turns
    
    future_x = CENTER[0] + dist_to_center * math.cos(future_angle)
    future_y = CENTER[1] + dist_to_center * math.sin(future_angle)
    
    return future_x, future_y

def line_intersects_circle(x1: float, y1: float, x2: float, y2: float,
                          cx: float, cy: float, radius: float) -> bool:
    dx = x2 - x1
    dy = y2 - y1
    fx = x1 - cx
    fy = y1 - cy
    
    a = dx * dx + dy * dy
    if a < 1e-10:
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
    return line_intersects_circle(x1, y1, x2, y2, CENTER[0], CENTER[1], SUN_RADIUS)

def find_safe_angle(sx: float, sy: float, tx: float, ty: float) -> Optional[float]:
    """Find safe angle avoiding sun."""
    direct = angle_to(sx, sy, tx, ty)
    
    if not path_crosses_sun(sx, sy, tx, ty):
        return direct
    
    for offset in [0.3, -0.3, 0.6, -0.6, 0.9, -0.9, 1.2, -1.2]:
        test_angle = direct + offset
        test_x = sx + math.cos(test_angle) * 150
        test_y = sy + math.sin(test_angle) * 150
        if not path_crosses_sun(sx, sy, test_x, test_y):
            return test_angle
    
    return None

# ============================================================================
# GAME STATE
# ============================================================================

class GameState:
    def __init__(self, obs: dict):
        self.obs = obs
        self.player = obs.get('player', 0)
        self.step = obs.get('step', 0)
        self.angular_velocity = obs.get('angular_velocity', 0.0)
        self.comet_ids = set(obs.get('comet_planet_ids', []))
        
        self.planets = [Planet(*p) for p in obs.get('planets', [])]
        self.fleets = [Fleet(*f) for f in obs.get('fleets', [])]
        
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner != self.player and p.owner != -1]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]
        
        self.planet_map = {p.id: p for p in self.planets}
        
        # Analyze threats
        self.threats = self._analyze_threats()
        
        # Calculate scores
        self.my_score = self._calculate_score(self.player)
        self.enemy_scores = {i: self._calculate_score(i) for i in range(4) if i != self.player}
    
    def _analyze_threats(self) -> Dict[int, List[Tuple[int, float, int]]]:
        """Analyze incoming threats to our planets."""
        threats = defaultdict(list)
        
        for fleet in self.fleets:
            if fleet.owner == self.player:
                continue
            
            for planet in self.my_planets:
                dist = distance(fleet.x, fleet.y, planet.x, planet.y)
                angle_to_planet = angle_to(fleet.x, fleet.y, planet.x, planet.y)
                angle_diff = abs(normalize_angle(fleet.angle - angle_to_planet))
                
                if angle_diff < 0.5 and dist < 60:
                    eta = travel_time(dist, fleet.ships)
                    threats[planet.id].append((fleet.ships, eta, fleet.owner))
        
        return threats
    
    def _calculate_score(self, owner: int) -> int:
        """Calculate total ships for a player."""
        planet_ships = sum(p.ships for p in self.planets if p.owner == owner)
        fleet_ships = sum(f.ships for f in self.fleets if f.owner == owner)
        return planet_ships + fleet_ships
    
    def get_phase(self) -> str:
        """Determine game phase."""
        if self.step < 80:
            return "early"
        elif self.step < 350:
            return "mid"
        else:
            return "late"
    
    def predict_position(self, planet: Planet, turns: int) -> Tuple[float, float]:
        """Predict planet position after N turns."""
        return predict_planet_position(planet.x, planet.y, self.angular_velocity, turns)

# ============================================================================
# ELITE STRATEGY
# ============================================================================

class EliteStrategy:
    def __init__(self, gs: GameState):
        self.gs = gs
        self.phase = gs.get_phase()
        self.used_planets = set()
    
    def evaluate_target(self, source: Planet, target: Planet) -> float:
        """Advanced target evaluation."""
        dist = distance(source.x, source.y, target.x, target.y)
        
        # Estimate ships needed
        base_needed = target.ships + 1
        time = travel_time(dist, base_needed)
        
        if target.owner != -1:
            base_needed += int(target.production * time * 1.3)
        
        # Can't afford
        if base_needed > source.ships * 0.85:
            return -10000
        
        # Check sun
        if path_crosses_sun(source.x, source.y, target.x, target.y):
            if find_safe_angle(source.x, source.y, target.x, target.y) is None:
                return -10000
        
        # Value calculation
        production_value = target.production ** 2 * 80
        distance_penalty = dist * 1.2
        ship_cost = base_needed * 0.8
        
        # Bonuses
        neutral_bonus = 100 if target.owner == -1 else 0
        high_prod_bonus = 150 if target.production >= 4 else 0
        enemy_bonus = 60 if target.owner != -1 and target.owner != self.gs.player else 0
        
        # Penalties
        comet_penalty = 200 if target.id in self.gs.comet_ids else 0
        far_penalty = 50 if dist > 50 else 0
        
        # Phase adjustments
        if self.phase == "early":
            neutral_bonus *= 1.8
            production_value *= 1.5
        elif self.phase == "late":
            enemy_bonus *= 2.5
            distance_penalty *= 0.5
        
        score = (production_value + neutral_bonus + high_prod_bonus + enemy_bonus 
                - distance_penalty - ship_cost - comet_penalty - far_penalty)
        
        # Prioritize if we're behind
        if self.gs.my_score < max(self.gs.enemy_scores.values(), default=0):
            enemy_bonus *= 1.5
        
        return score
    
    def calculate_fleet_size(self, source: Planet, target: Planet) -> int:
        """Calculate optimal fleet size."""
        dist = distance(source.x, source.y, target.x, target.y)
        base = target.ships + 1
        time = travel_time(dist, base)
        
        production_buffer = int(target.production * time * 1.4) if target.owner != -1 else 0
        safety = 15 if self.phase == "early" else 25
        
        total = base + production_buffer + safety
        
        # Reserve for defense
        if source.id in self.gs.threats:
            max_send = int(source.ships * 0.5)
        else:
            max_send = int(source.ships * 0.88)
        
        return min(total, max_send, source.ships - 8)
    
    def should_defend(self, planet: Planet) -> Optional[Tuple[int, float]]:
        """Check if planet needs reinforcement."""
        if planet.id not in self.gs.threats:
            return None
        
        threats = self.gs.threats[planet.id]
        if not threats:
            return None
        
        total_incoming = sum(t[0] for t in threats)
        min_eta = min(t[1] for t in threats)
        
        our_strength = planet.ships + int(planet.production * min_eta)
        
        if total_incoming > our_strength * 1.1:
            needed = int((total_incoming - our_strength) * 1.3)
            return (needed, min_eta)
        
        return None
    
    def find_reinforcement(self, target: Planet, needed: int, urgency: float) -> Optional[Tuple[Planet, int]]:
        """Find best planet to send reinforcements."""
        candidates = []
        
        for p in self.gs.my_planets:
            if p.id == target.id or p.id in self.used_planets:
                continue
            if p.ships < needed + 15:
                continue
            
            dist = distance(p.x, p.y, target.x, target.y)
            time = travel_time(dist, needed)
            
            if time > urgency * 0.8:
                continue
            
            score = p.ships / (dist + 1)
            candidates.append((p, score, needed))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return (candidates[0][0], candidates[0][2])
        
        return None
    
    def select_targets(self, source: Planet) -> List[Tuple[Planet, float]]:
        """Select best targets for a planet."""
        all_targets = self.gs.neutral_planets + self.gs.enemy_planets
        
        scored = []
        for target in all_targets:
            score = self.evaluate_target(source, target)
            if score > 0:
                scored.append((target, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:2]

# ============================================================================
# MAIN AGENT
# ============================================================================

def agent(obs: dict) -> List[List]:
    """
    Elite agent targeting 3500+ rating.
    """
    gs = GameState(obs)
    strategy = EliteStrategy(gs)
    moves = []
    
    # Phase 1: DEFENSE (Critical!)
    for planet in gs.my_planets:
        if planet.id in strategy.used_planets:
            continue
        
        defense = strategy.should_defend(planet)
        if defense:
            needed, urgency = defense
            
            reinforcement = strategy.find_reinforcement(planet, needed, urgency)
            if reinforcement and urgency < 15:
                source, ships = reinforcement
                angle = angle_to(source.x, source.y, planet.x, planet.y)
                
                # Check sun
                safe_angle = find_safe_angle(source.x, source.y, planet.x, planet.y)
                if safe_angle is not None:
                    moves.append([source.id, safe_angle, ships])
                    strategy.used_planets.add(source.id)
    
    # Phase 2: OFFENSE
    for planet in gs.my_planets:
        if planet.id in strategy.used_planets:
            continue
        
        if planet.ships < 12:
            continue
        
        # Skip comets in mid/late game
        if planet.id in gs.comet_ids and gs.step > 150:
            continue
        
        targets = strategy.select_targets(planet)
        if not targets:
            continue
        
        target, score = targets[0]
        
        fleet_size = strategy.calculate_fleet_size(planet, target)
        if fleet_size < 6:
            continue
        
        # Predict target position if orbiting
        dist = distance(planet.x, planet.y, target.x, target.y)
        eta = travel_time(dist, fleet_size)
        
        if dist < ROTATION_RADIUS_LIMIT - 10:
            future_x, future_y = gs.predict_position(target, int(eta))
            angle = angle_to(planet.x, planet.y, future_x, future_y)
        else:
            angle = angle_to(planet.x, planet.y, target.x, target.y)
        
        # Find safe path
        safe_angle = find_safe_angle(planet.x, planet.y, target.x, target.y)
        if safe_angle is not None:
            moves.append([planet.id, safe_angle, fleet_size])
            strategy.used_planets.add(planet.id)
    
    return moves
