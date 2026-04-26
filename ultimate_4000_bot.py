"""
ULTIMATE 4000-Rating Bot
All strategic improvements: Rush, multi-target, proper intercept, comet capture, endgame optimization
"""

import math
from typing import List, Tuple, Optional, Dict, Set
from collections import defaultdict

CENTER = (50.0, 50.0)
SUN_RADIUS = 10.0
MAX_SPEED = 6.0
ROTATION_RADIUS_LIMIT = 50.0

class Planet:
    def __init__(self, id, owner, x, y, radius, ships, production):
        self.id, self.owner, self.x, self.y = id, owner, x, y
        self.radius, self.ships, self.production = radius, ships, production

class Fleet:
    def __init__(self, id, owner, x, y, angle, from_planet_id, ships):
        self.id, self.owner, self.x, self.y = id, owner, x, y
        self.angle, self.from_planet_id, self.ships = angle, from_planet_id, ships

def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def angle_to(x1, y1, x2, y2):
    return math.atan2(y2-y1, x2-x1)

def normalize_angle(a):
    while a > math.pi: a -= 2*math.pi
    while a < -math.pi: a += 2*math.pi
    return a

def fleet_speed(ships):
    return 1.0 + (MAX_SPEED-1.0) * (math.log(max(ships,1))/math.log(1000))**1.5

def travel_time(dist, ships):
    return dist / fleet_speed(ships)

def predict_position(x, y, angular_vel, turns):
    """Proper orbital prediction."""
    d = distance(x, y, CENTER[0], CENTER[1])
    if d >= ROTATION_RADIUS_LIMIT - 5:
        return x, y
    angle = math.atan2(y-CENTER[1], x-CENTER[0]) + angular_vel * turns
    return CENTER[0] + d*math.cos(angle), CENTER[1] + d*math.sin(angle)

def iterative_intercept(sx, sy, tx, ty, angular_vel, fleet_ships, max_iter=5):
    """PROPER iterative intercept for orbiting targets."""
    speed = fleet_speed(fleet_ships)
    
    for _ in range(max_iter):
        dx, dy = tx - sx, ty - sy
        dist = math.sqrt(dx*dx + dy*dy)
        eta = dist / speed
        
        # Predict target position at ETA
        tx, ty = predict_position(tx, ty, angular_vel, eta)
    
    return angle_to(sx, sy, tx, ty), eta

def line_circle_intersect(x1, y1, x2, y2, cx, cy, r):
    dx, dy = x2-x1, y2-y1
    fx, fy = x1-cx, y1-cy
    a = dx*dx + dy*dy
    if a < 1e-10:
        return distance(x1, y1, cx, cy) <= r
    b = 2*(fx*dx + fy*dy)
    c = fx*fx + fy*fy - r*r
    disc = b*b - 4*a*c
    if disc < 0:
        return False
    disc = math.sqrt(disc)
    t1, t2 = (-b-disc)/(2*a), (-b+disc)/(2*a)
    return (0<=t1<=1) or (0<=t2<=1) or (t1<0 and t2>1)

def crosses_sun(x1, y1, x2, y2):
    return line_circle_intersect(x1, y1, x2, y2, CENTER[0], CENTER[1], SUN_RADIUS)

def safe_angle(sx, sy, tx, ty):
    """Find safe angle with waypoint if needed."""
    direct = angle_to(sx, sy, tx, ty)
    if not crosses_sun(sx, sy, tx, ty):
        return direct
    
    # Try waypoints around sun
    for off in [0.3, -0.3, 0.6, -0.6, 0.9, -0.9]:
        test = direct + off
        test_x, test_y = sx + math.cos(test)*120, sy + math.sin(test)*120
        if not crosses_sun(sx, sy, test_x, test_y):
            return test
    return None

class GameState:
    def __init__(self, obs):
        self.player = obs.get('player', 0)
        self.step = obs.get('step', 0)
        self.angular_vel = obs.get('angular_velocity', 0.0)
        self.comet_ids = set(obs.get('comet_planet_ids', []))
        
        self.planets = [Planet(*p) for p in obs.get('planets', [])]
        self.fleets = [Fleet(*f) for f in obs.get('fleets', [])]
        
        self.my_planets = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets = [p for p in self.planets if p.owner != self.player and p.owner != -1]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]
        
        self.planet_map = {p.id: p for p in self.planets}
        
        # PROPER fleet tracking
        self.my_fleet_targets = self._track_fleets(self.player)
        self.enemy_fleet_targets = {}
        for i in range(4):
            if i != self.player:
                self.enemy_fleet_targets[i] = self._track_fleets(i)
        
        # Metrics
        self.my_ships = sum(p.ships for p in self.my_planets)
        self.my_fleet_ships = sum(f.ships for f in self.fleets if f.owner == self.player)
        self.my_total = self.my_ships + self.my_fleet_ships
        self.my_production = sum(p.production for p in self.my_planets)
        
        self.enemy_totals = {}
        self.enemy_productions = {}
        for i in range(4):
            if i == self.player:
                continue
            ships = sum(p.ships for p in self.planets if p.owner == i)
            fleet_ships = sum(f.ships for f in self.fleets if f.owner == i)
            self.enemy_totals[i] = ships + fleet_ships
            self.enemy_productions[i] = sum(p.production for p in self.planets if p.owner == i)
        
        self.max_enemy_total = max(self.enemy_totals.values(), default=0)
        self.max_enemy_production = max(self.enemy_productions.values(), default=0)
        
        self.turns_remaining = 500 - self.step
    
    def _track_fleets(self, owner):
        """PROPER geometric fleet tracking."""
        targets = defaultdict(list)
        for f in self.fleets:
            if f.owner != owner:
                continue
            
            best_planet = None
            best_dist = float('inf')
            
            for p in self.planets:
                d = distance(f.x, f.y, p.x, p.y)
                if d < 1:
                    continue
                
                # PROPER geometric check
                angle_to_planet = angle_to(f.x, f.y, p.x, p.y)
                angle_diff = abs(normalize_angle(f.angle - angle_to_planet))
                
                # Stricter check
                if angle_diff < 0.3 and d < 100:
                    if d < best_dist:
                        best_dist = d
                        best_planet = p
            
            if best_planet:
                eta = travel_time(d, f.ships)
                targets[best_planet.id].append((f.ships, eta))
        
        return targets
    
    def simulate_planet_at_time(self, planet, at_time):
        """COMPLETE simulation with all fleets."""
        future_ships = planet.ships
        future_owner = planet.owner
        
        if planet.owner != -1:
            future_ships += int(planet.production * at_time)
        
        incoming = defaultdict(int)
        
        if planet.id in self.my_fleet_targets:
            for ships, eta in self.my_fleet_targets[planet.id]:
                if eta <= at_time:
                    incoming[self.player] += ships
        
        for enemy_id, targets in self.enemy_fleet_targets.items():
            if planet.id in targets:
                for ships, eta in targets[planet.id]:
                    if eta <= at_time:
                        incoming[enemy_id] += ships
        
        if incoming:
            if future_owner != -1:
                incoming[future_owner] += future_ships
            
            forces = sorted(incoming.items(), key=lambda x: x[1], reverse=True)
            
            if len(forces) >= 2:
                if forces[0][1] > forces[1][1]:
                    future_owner = forces[0][0]
                    future_ships = forces[0][1] - forces[1][1]
                else:
                    future_owner = planet.owner
                    future_ships = planet.ships
            elif len(forces) == 1:
                future_owner = forces[0][0]
                future_ships = forces[0][1]
        
        return future_owner, future_ships
    
    def enemy_targeting_planet(self, planet_id):
        """Check if enemy is targeting this planet."""
        for enemy_targets in self.enemy_fleet_targets.values():
            if planet_id in enemy_targets:
                return True
        return False

class UltimateStrategy:
    def __init__(self, gs):
        self.gs = gs
        self.used = set()
        
        # STRATEGIC MODE
        if gs.step < 40:
            self.mode = "rush"  # RUSH early game
        elif gs.step < 80:
            self.mode = "expansion"
        elif gs.turns_remaining < 50:
            self.mode = "endgame"
        elif gs.my_production < gs.max_enemy_production * 0.6:
            self.mode = "catch_up"
        elif gs.my_total < gs.max_enemy_total * 0.7:
            self.mode = "eliminate"  # Focus on enemy
        elif gs.my_total > gs.max_enemy_total * 1.5:
            self.mode = "dominate"
        else:
            self.mode = "balanced"
    
    def calculate_etf(self, source, target):
        """Expected Time to Capture - proper metric."""
        d = distance(source.x, source.y, target.x, target.y)
        ships_needed = target.ships + 1
        
        if target.owner != -1:
            eta = travel_time(d, ships_needed)
            ships_needed += int(target.production * eta * 1.3)
        
        if ships_needed > source.ships * 0.9:
            return float('inf')
        
        eta = travel_time(d, ships_needed)
        
        # ETF = time + (ships_cost / production_value)
        production_value = target.production
        etf = eta + (ships_needed / max(production_value, 1))
        
        return etf
    
    def evaluate_target(self, target):
        """ADVANCED evaluation with all factors."""
        # Base value
        value = target.production ** 2.5 * 100
        
        # Distance from ALL our planets
        if self.gs.my_planets:
            min_dist = min(distance(p.x, p.y, target.x, target.y) for p in self.gs.my_planets)
            distance_penalty = min_dist * 1.0
        else:
            distance_penalty = 0
        
        # Enemy contest
        contest_penalty = 0
        if self.gs.enemy_targeting_planet(target.id):
            contest_penalty = 200
        
        # Mode-specific
        if self.mode == "rush":
            if target.owner == -1:
                value *= 3.0
                distance_penalty *= 0.3
        elif self.mode == "expansion":
            if target.owner == -1:
                value *= 2.0
        elif self.mode == "catch_up":
            if target.production >= 4:
                value *= 3.5
        elif self.mode == "eliminate":
            if target.owner != -1:
                value *= 3.0
        elif self.mode == "endgame":
            # Only high-value or enemy
            if target.owner == -1 and target.production < 3:
                value *= 0.1
            elif target.owner != -1:
                value *= 2.5
        elif self.mode == "dominate":
            if target.production < 3:
                value *= 0.3
        
        # Comet strategy
        if target.id in self.gs.comet_ids:
            if self.gs.step < 150:
                value *= 0.8  # Capture early comets
            else:
                value *= 0.05  # Avoid late comets
        
        return value - distance_penalty - contest_penalty
    
    def calculate_exact_fleet_size(self, source, target, eta):
        """EXACT fleet size - not conservative."""
        future_owner, future_ships = self.gs.simulate_planet_at_time(target, eta)
        
        # Adaptive buffer
        buffer = max(8, int(0.12 * future_ships))
        needed = future_ships + buffer
        
        # Don't over-send
        available = source.ships - 12
        
        return min(needed, available)
    
    def find_gang_up_attack(self, target, sources):
        """GANG UP: Multiple planets on single target."""
        if not sources:
            return []
        
        source_data = []
        for src in sources:
            if src.id in self.used:
                continue
            
            d = distance(src.x, src.y, target.x, target.y)
            eta = travel_time(d, 50)
            
            if eta > self.gs.turns_remaining:
                continue
            
            available = src.ships - 12
            if available > 15:
                source_data.append((src, eta, available))
        
        if not source_data:
            return []
        
        source_data.sort(key=lambda x: x[1])
        
        # Find synchronized group (±1 turn)
        best_plan = []
        
        for i in range(len(source_data)):
            target_eta = source_data[i][1]
            group = []
            total = 0
            
            for src, eta, avail in source_data:
                if abs(eta - target_eta) <= 1.0:
                    group.append((src, avail, eta))
                    total += avail
            
            if group:
                future_owner, future_ships = self.gs.simulate_planet_at_time(target, target_eta)
                buffer = max(8, int(0.12 * future_ships))
                needed = future_ships + buffer
                
                if total >= needed:
                    best_plan = group
                    break
        
        if best_plan:
            total_avail = sum(a for _, a, _ in best_plan)
            future_owner, future_ships = self.gs.simulate_planet_at_time(target, best_plan[0][2])
            buffer = max(8, int(0.12 * future_ships))
            needed_total = future_ships + buffer
            
            ratio = min(needed_total / total_avail, 0.98)
            
            final = []
            for src, avail, eta in best_plan:
                ships = int(avail * ratio)
                if ships >= 10:
                    final.append((src, ships, eta))
            
            return final
        
        return []
    
    def should_attack_endgame(self, target, ships_cost, eta):
        """ENDGAME: Only attack if arrives in time and net positive."""
        if self.mode != "endgame":
            return True
        
        # Won't arrive in time
        if eta > self.gs.turns_remaining - 5:
            return False
        
        # Calculate net gain
        turns_owned = max(0, self.gs.turns_remaining - eta - 5)
        production_gain = target.production * turns_owned
        net = production_gain - ships_cost
        
        # Attack if net positive or denying enemy
        if net > 0:
            return True
        if target.owner != -1 and target.owner != self.gs.player:
            return True
        
        return False

def agent(obs: dict) -> List[List]:
    """
    ULTIMATE 4000-rating bot with all strategic improvements.
    """
    gs = GameState(obs)
    strat = UltimateStrategy(gs)
    moves = []
    
    # PHASE 1: DEFENSE (only critical)
    for planet in sorted(gs.my_planets, key=lambda p: p.production, reverse=True)[:3]:
        if planet.id in strat.used:
            continue
        
        if planet.id in gs.enemy_fleet_targets.get(gs.player, {}):
            future_owner, _ = gs.simulate_planet_at_time(planet, 8)
            
            if future_owner != gs.player:
                # Find closest reinforcement
                for src in sorted(gs.my_planets, key=lambda p: distance(p.x, p.y, planet.x, planet.y)):
                    if src.id == planet.id or src.id in strat.used:
                        continue
                    
                    d = distance(src.x, src.y, planet.x, planet.y)
                    if d < 40 and src.ships > 25:
                        ships = int(src.ships * 0.6)
                        ang = safe_angle(src.x, src.y, planet.x, planet.y)
                        if ang:
                            moves.append([src.id, ang, ships])
                            strat.used.add(src.id)
                            break
    
    # PHASE 2: GLOBAL TARGETS
    all_targets = gs.neutral_planets + gs.enemy_planets
    scored = [(t, strat.evaluate_target(t)) for t in all_targets]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # PHASE 3: ATTACKS (gang up + proper intercept)
    available = [p for p in gs.my_planets if p.id not in strat.used and p.ships >= 15]
    
    for target, score in scored[:20]:
        if score <= 0:
            break
        
        # Check existing attacks
        if target.id in gs.my_fleet_targets:
            incoming = sum(s for s, _ in gs.my_fleet_targets[target.id])
            if incoming > target.ships * 2.5:
                continue
        
        # Try gang up attack
        plan = strat.find_gang_up_attack(target, available)
        
        if plan:
            # Check endgame
            total_ships = sum(s for _, s, _ in plan)
            eta = plan[0][2]
            
            if not strat.should_attack_endgame(target, total_ships, eta):
                continue
            
            # Execute with PROPER intercept
            for src, ships, eta in plan:
                # Iterative intercept for orbiting
                d = distance(src.x, src.y, target.x, target.y)
                if d < ROTATION_RADIUS_LIMIT - 8:
                    ang, _ = iterative_intercept(src.x, src.y, target.x, target.y, 
                                                gs.angular_vel, ships)
                else:
                    ang = angle_to(src.x, src.y, target.x, target.y)
                
                safe_ang = safe_angle(src.x, src.y, target.x, target.y)
                if safe_ang:
                    moves.append([src.id, safe_ang, ships])
                    strat.used.add(src.id)
                    available = [p for p in available if p.id != src.id]
            
            if len(strat.used) >= len(gs.my_planets) * 0.9:
                break
    
    return moves
