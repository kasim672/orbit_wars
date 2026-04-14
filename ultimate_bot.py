"""
ULTIMATE Orbit Wars Bot - Target: 3500-4000 Rating
Maximum competitive features for top leaderboard placement
"""

import math
from typing import List, Tuple, Optional, Dict
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
    d = distance(x, y, CENTER[0], CENTER[1])
    if d >= ROTATION_RADIUS_LIMIT - 5:
        return x, y
    angle = math.atan2(y-CENTER[1], x-CENTER[0]) + angular_vel * turns
    return CENTER[0] + d*math.cos(angle), CENTER[1] + d*math.sin(angle)

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
    direct = angle_to(sx, sy, tx, ty)
    if not crosses_sun(sx, sy, tx, ty):
        return direct
    for off in [0.25, -0.25, 0.5, -0.5, 0.75, -0.75, 1.0, -1.0, 1.3, -1.3]:
        test = direct + off
        test_x, test_y = sx + math.cos(test)*150, sy + math.sin(test)*150
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
        self.threats = self._analyze_threats()
        
        self.my_production = sum(p.production for p in self.my_planets)
        self.enemy_production = sum(p.production for p in self.enemy_planets)
        
        self.my_score = sum(p.ships for p in self.my_planets) + sum(f.ships for f in self.fleets if f.owner == self.player)
        self.max_enemy_score = max([sum(p.ships for p in self.planets if p.owner == i) + 
                                    sum(f.ships for f in self.fleets if f.owner == i) 
                                    for i in range(4) if i != self.player], default=0)
    
    def _analyze_threats(self):
        threats = defaultdict(list)
        for f in self.fleets:
            if f.owner == self.player:
                continue
            for p in self.my_planets:
                d = distance(f.x, f.y, p.x, p.y)
                ang_diff = abs(normalize_angle(f.angle - angle_to(f.x, f.y, p.x, p.y)))
                if ang_diff < 0.6 and d < 70:
                    eta = travel_time(d, f.ships)
                    threats[p.id].append((f.ships, eta, f.owner))
        return threats
    
    def phase(self):
        if self.step < 70:
            return "early"
        elif self.step < 320:
            return "mid"
        else:
            return "late"

class UltimateStrategy:
    def __init__(self, gs):
        self.gs = gs
        self.phase = gs.phase()
        self.used = set()
        
        # Aggression based on position
        self.aggression = 1.0
        if gs.my_score < gs.max_enemy_score * 0.8:
            self.aggression = 1.5  # More aggressive when behind
        elif gs.my_score > gs.max_enemy_score * 1.3:
            self.aggression = 0.7  # More defensive when ahead
    
    def evaluate_target(self, src, tgt):
        d = distance(src.x, src.y, tgt.x, tgt.y)
        
        base = tgt.ships + 1
        time = travel_time(d, base)
        
        if tgt.owner != -1:
            base += int(tgt.production * time * 1.4)
        
        if base > src.ships * 0.9:
            return -20000
        
        if crosses_sun(src.x, src.y, tgt.x, tgt.y):
            if safe_angle(src.x, src.y, tgt.x, tgt.y) is None:
                return -20000
        
        # Advanced scoring
        prod_val = tgt.production ** 2.2 * 100
        dist_pen = d * 1.0
        ship_cost = base * 0.7
        
        neutral_bonus = 120 if tgt.owner == -1 else 0
        high_prod_bonus = 200 if tgt.production >= 4 else (80 if tgt.production >= 3 else 0)
        enemy_bonus = 80 if tgt.owner != -1 and tgt.owner != self.gs.player else 0
        
        comet_pen = 250 if tgt.id in self.gs.comet_ids else 0
        far_pen = 80 if d > 55 else 0
        
        # Phase bonuses
        if self.phase == "early":
            neutral_bonus *= 2.0
            prod_val *= 1.8
            dist_pen *= 0.8
        elif self.phase == "mid":
            enemy_bonus *= 1.5
            high_prod_bonus *= 1.3
        else:  # late
            enemy_bonus *= 3.0
            dist_pen *= 0.4
            ship_cost *= 0.5
        
        # Production advantage bonus
        if self.gs.my_production > self.gs.enemy_production:
            neutral_bonus *= 1.2
        else:
            enemy_bonus *= 1.5
        
        # Position bonus
        if self.gs.my_score < self.gs.max_enemy_score:
            enemy_bonus *= 1.8
        
        score = (prod_val + neutral_bonus + high_prod_bonus + enemy_bonus 
                - dist_pen - ship_cost - comet_pen - far_pen) * self.aggression
        
        return score
    
    def calc_fleet_size(self, src, tgt):
        d = distance(src.x, src.y, tgt.x, tgt.y)
        base = tgt.ships + 1
        time = travel_time(d, base)
        
        prod_buffer = int(tgt.production * time * 1.5) if tgt.owner != -1 else 0
        safety = 20 if self.phase == "early" else 30
        
        total = base + prod_buffer + safety
        
        # Dynamic reserve based on threats
        if src.id in self.gs.threats:
            reserve_ratio = 0.45
        elif self.phase == "late" and self.gs.my_score > self.gs.max_enemy_score:
            reserve_ratio = 0.3  # Keep more when winning late
        else:
            reserve_ratio = 0.12
        
        max_send = int(src.ships * (1 - reserve_ratio))
        
        return min(total, max_send, src.ships - 10)
    
    def should_defend(self, planet):
        if planet.id not in self.gs.threats:
            return None
        
        threats = self.gs.threats[planet.id]
        if not threats:
            return None
        
        total_incoming = sum(t[0] for t in threats)
        min_eta = min(t[1] for t in threats)
        
        our_strength = planet.ships + int(planet.production * min_eta)
        
        # More aggressive defense for high-production planets
        threshold = 1.15 if planet.production >= 4 else 1.05
        
        if total_incoming > our_strength * threshold:
            needed = int((total_incoming - our_strength) * 1.4)
            return (needed, min_eta)
        
        return None
    
    def find_reinforcement(self, tgt, needed, urgency):
        candidates = []
        
        for p in self.gs.my_planets:
            if p.id == tgt.id or p.id in self.used:
                continue
            if p.ships < needed + 20:
                continue
            
            d = distance(p.x, p.y, tgt.x, tgt.y)
            time = travel_time(d, needed)
            
            if time > urgency * 0.75:
                continue
            
            score = (p.ships * p.production) / (d + 1)
            candidates.append((p, score, needed))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return (candidates[0][0], candidates[0][2])
        
        return None
    
    def select_targets(self, src):
        all_tgts = self.gs.neutral_planets + self.gs.enemy_planets
        
        scored = []
        for tgt in all_tgts:
            score = self.evaluate_target(src, tgt)
            if score > 0:
                scored.append((tgt, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:3]

def agent(obs: dict) -> List[List]:
    """
    Ultimate competitive bot for 3500-4000 rating.
    """
    gs = GameState(obs)
    strat = UltimateStrategy(gs)
    moves = []
    
    # CRITICAL: Defense first
    defense_planets = sorted(gs.my_planets, key=lambda p: p.production, reverse=True)
    
    for planet in defense_planets:
        if planet.id in strat.used:
            continue
        
        defense = strat.should_defend(planet)
        if defense:
            needed, urgency = defense
            
            reinf = strat.find_reinforcement(planet, needed, urgency)
            if reinf and urgency < 18:
                src, ships = reinf
                ang = safe_angle(src.x, src.y, planet.x, planet.y)
                
                if ang is not None:
                    moves.append([src.id, ang, ships])
                    strat.used.add(src.id)
    
    # Offense: prioritize high-production planets
    offense_planets = sorted([p for p in gs.my_planets if p.id not in strat.used],
                            key=lambda p: p.ships * p.production, reverse=True)
    
    for planet in offense_planets:
        if planet.id in strat.used:
            continue
        
        if planet.ships < 15:
            continue
        
        # Skip comets after early game
        if planet.id in gs.comet_ids and gs.step > 120:
            continue
        
        targets = strat.select_targets(planet)
        if not targets:
            continue
        
        tgt, score = targets[0]
        
        fleet_size = strat.calc_fleet_size(planet, tgt)
        if fleet_size < 8:
            continue
        
        # Orbital prediction
        d = distance(planet.x, planet.y, tgt.x, tgt.y)
        eta = travel_time(d, fleet_size)
        
        if d < ROTATION_RADIUS_LIMIT - 8:
            future_x, future_y = predict_position(tgt.x, tgt.y, gs.angular_vel, int(eta))
            ang = angle_to(planet.x, planet.y, future_x, future_y)
        else:
            ang = angle_to(planet.x, planet.y, tgt.x, tgt.y)
        
        # Safe path
        safe_ang = safe_angle(planet.x, planet.y, tgt.x, tgt.y)
        if safe_ang is not None:
            moves.append([planet.id, safe_ang, fleet_size])
            strat.used.add(planet.id)
    
    return moves
