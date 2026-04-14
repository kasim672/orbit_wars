"""
COMPETITIVE Bot - 3500+ Rating Target
Fixes: Multi-planet coordination, fleet tracking, global strategy, win condition awareness
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
    for off in [0.2, -0.2, 0.4, -0.4, 0.6, -0.6, 0.8, -0.8, 1.0, -1.0]:
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
        
        # CRITICAL: Track fleet destinations
        self.my_fleet_targets = self._track_my_fleets()
        self.enemy_fleet_targets = self._track_enemy_fleets()
        
        # Calculate scores and production
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
        
        # Threats
        self.threats = self._analyze_threats()
    
    def _track_my_fleets(self):
        """Track where our fleets are going and when they arrive."""
        targets = defaultdict(list)
        for f in self.fleets:
            if f.owner != self.player:
                continue
            # Find closest planet in direction of travel
            best_planet = None
            best_score = float('inf')
            for p in self.planets:
                d = distance(f.x, f.y, p.x, p.y)
                angle_to_planet = angle_to(f.x, f.y, p.x, p.y)
                angle_diff = abs(normalize_angle(f.angle - angle_to_planet))
                if angle_diff < 0.3 and d < 80:
                    score = d + angle_diff * 50
                    if score < best_score:
                        best_score = score
                        best_planet = p
            if best_planet:
                eta = travel_time(distance(f.x, f.y, best_planet.x, best_planet.y), f.ships)
                targets[best_planet.id].append((f.ships, eta))
        return targets
    
    def _track_enemy_fleets(self):
        """Track enemy fleet destinations."""
        targets = defaultdict(list)
        for f in self.fleets:
            if f.owner == self.player:
                continue
            for p in self.my_planets:
                d = distance(f.x, f.y, p.x, p.y)
                angle_diff = abs(normalize_angle(f.angle - angle_to(f.x, f.y, p.x, p.y)))
                if angle_diff < 0.4 and d < 70:
                    eta = travel_time(d, f.ships)
                    targets[p.id].append((f.ships, eta, f.owner))
        return targets
    
    def _analyze_threats(self):
        """Analyze threats to our planets."""
        threats = {}
        for p in self.my_planets:
            if p.id in self.enemy_fleet_targets:
                total_incoming = sum(t[0] for t in self.enemy_fleet_targets[p.id])
                min_eta = min(t[1] for t in self.enemy_fleet_targets[p.id])
                our_strength = p.ships + int(p.production * min_eta)
                if total_incoming > our_strength * 0.9:
                    threats[p.id] = (total_incoming, min_eta, our_strength)
        return threats
    
    def predict_planet_state(self, planet, turns):
        """Predict planet state after N turns including incoming fleets."""
        future_x, future_y = predict_position(planet.x, planet.y, self.angular_vel, turns)
        future_ships = planet.ships
        
        if planet.owner == self.player:
            future_ships += planet.production * turns
        
        # Account for our incoming fleets
        if planet.id in self.my_fleet_targets:
            for ships, eta in self.my_fleet_targets[planet.id]:
                if eta <= turns:
                    future_ships += ships
        
        return future_x, future_y, future_ships

class CompetitiveStrategy:
    def __init__(self, gs):
        self.gs = gs
        self.used = set()
        
        # Determine strategy based on game state
        self.turns_remaining = 500 - gs.step
        
        # WIN CONDITION AWARENESS
        if self.turns_remaining < 50:
            # Late game: maximize ships, avoid risky moves
            self.mode = "endgame"
        elif gs.step < 60:
            # Early: expand fast
            self.mode = "expansion"
        elif gs.my_production < gs.max_enemy_production * 0.7:
            # Behind in production: aggressive expansion
            self.mode = "catch_up"
        elif gs.my_total < gs.max_enemy_total * 0.8:
            # Behind in ships: disrupt enemy
            self.mode = "disrupt"
        elif gs.my_total > gs.max_enemy_total * 1.3:
            # Ahead: consolidate and defend
            self.mode = "consolidate"
        else:
            # Balanced: standard play
            self.mode = "balanced"
    
    def global_target_priority(self):
        """GLOBAL strategy: rank ALL targets by strategic value."""
        all_targets = self.gs.neutral_planets + self.gs.enemy_planets
        
        scored_targets = []
        for tgt in all_targets:
            # Base value: production is king
            value = tgt.production * 100
            
            # Strategic modifiers
            if self.mode == "expansion":
                # Prioritize close neutrals
                if tgt.owner == -1:
                    value *= 2.0
            elif self.mode == "catch_up":
                # Prioritize high production
                if tgt.production >= 4:
                    value *= 2.5
            elif self.mode == "disrupt":
                # Prioritize enemy high-production
                if tgt.owner != -1 and tgt.production >= 3:
                    value *= 2.0
            elif self.mode == "consolidate":
                # Only take very valuable targets
                if tgt.production < 3:
                    value *= 0.3
            elif self.mode == "endgame":
                # Only take if we can hold and it helps score
                if tgt.owner == -1:
                    value *= 0.5
                else:
                    value *= 1.5  # Deny enemy ships
            
            # Comet penalty
            if tgt.id in self.gs.comet_ids:
                value *= 0.2
            
            scored_targets.append((tgt, value))
        
        scored_targets.sort(key=lambda x: x[1], reverse=True)
        return scored_targets
    
    def can_capture(self, sources, target, turns_limit=None):
        """Check if we can capture target with given sources."""
        if not sources:
            return False, []
        
        # Calculate what we need
        base_needed = target.ships + 1
        
        # Find best source or combination
        best_plan = None
        best_cost = float('inf')
        
        # Try single source first
        for src in sources:
            if src.id in self.used:
                continue
            
            d = distance(src.x, src.y, target.x, target.y)
            eta = travel_time(d, base_needed)
            
            if turns_limit and eta > turns_limit:
                continue
            
            # Account for production during travel
            if target.owner != -1:
                needed = base_needed + int(target.production * eta * 1.3)
            else:
                needed = base_needed + 5
            
            # Check if we have enough
            available = src.ships - 10  # Keep reserve
            if src.id in self.gs.threats:
                available = int(src.ships * 0.4)
            
            if needed <= available:
                cost = needed / (src.production + 1)  # Prefer high-production sources
                if cost < best_cost:
                    best_cost = cost
                    best_plan = [(src, needed, eta)]
        
        # Try multi-source coordination
        if len(sources) >= 2 and not best_plan:
            # Find 2-3 closest sources
            sources_with_dist = []
            for src in sources:
                if src.id in self.used:
                    continue
                d = distance(src.x, src.y, target.x, target.y)
                sources_with_dist.append((src, d))
            
            sources_with_dist.sort(key=lambda x: x[1])
            top_sources = [s[0] for s in sources_with_dist[:3]]
            
            if len(top_sources) >= 2:
                # Calculate combined attack
                total_available = 0
                plan = []
                max_eta = 0
                
                for src in top_sources:
                    d = distance(src.x, src.y, target.x, target.y)
                    eta = travel_time(d, 50)  # Estimate
                    
                    if turns_limit and eta > turns_limit:
                        continue
                    
                    available = src.ships - 10
                    if src.id in self.gs.threats:
                        available = int(src.ships * 0.4)
                    
                    if available > 20:
                        total_available += available
                        plan.append((src, available, eta))
                        max_eta = max(max_eta, eta)
                
                # Check if combined force is enough
                if target.owner != -1:
                    needed_total = base_needed + int(target.production * max_eta * 1.3)
                else:
                    needed_total = base_needed + 5
                
                if total_available >= needed_total and len(plan) >= 2:
                    # Distribute ships proportionally
                    ratio = needed_total / total_available
                    final_plan = []
                    for src, avail, eta in plan:
                        ships = int(avail * ratio * 1.1)  # 10% buffer
                        if ships >= 10:
                            final_plan.append((src, ships, eta))
                    
                    if final_plan:
                        best_plan = final_plan
        
        if best_plan:
            return True, best_plan
        return False, []
    
    def defend_planet(self, planet):
        """Send reinforcements to threatened planet."""
        if planet.id not in self.gs.threats:
            return None
        
        incoming, eta, our_strength = self.gs.threats[planet.id]
        needed = int((incoming - our_strength) * 1.3)
        
        if needed <= 0:
            return None
        
        # Find best reinforcement source
        best_source = None
        best_score = -1
        
        for src in self.gs.my_planets:
            if src.id == planet.id or src.id in self.used:
                continue
            
            if src.ships < needed + 15:
                continue
            
            d = distance(src.x, src.y, planet.x, planet.y)
            time = travel_time(d, needed)
            
            if time > eta * 0.7:
                continue
            
            score = (src.ships * src.production) / (d + 1)
            if score > best_score:
                best_score = score
                best_source = src
        
        if best_source:
            return (best_source, needed)
        return None

def agent(obs: dict) -> List[List]:
    """
    Competitive bot with global strategy and multi-planet coordination.
    """
    gs = GameState(obs)
    strat = CompetitiveStrategy(gs)
    moves = []
    
    # PHASE 1: CRITICAL DEFENSE
    for planet in sorted(gs.my_planets, key=lambda p: p.production, reverse=True):
        if planet.id in strat.used:
            continue
        
        defense = strat.defend_planet(planet)
        if defense:
            src, ships = defense
            ang = safe_angle(src.x, src.y, planet.x, planet.y)
            if ang is not None:
                moves.append([src.id, ang, ships])
                strat.used.add(src.id)
    
    # PHASE 2: GLOBAL TARGET PRIORITIZATION
    priority_targets = strat.global_target_priority()
    
    # EXPANSION PRESSURE: In early game, ensure fast expansion
    if strat.mode == "expansion" and len(gs.my_planets) < 6:
        # Force aggressive expansion
        priority_targets = [(t, v*2) for t, v in priority_targets if t.owner == -1][:8]
    
    # PHASE 3: EXECUTE ATTACKS (with multi-planet coordination)
    available_sources = [p for p in gs.my_planets if p.id not in strat.used and p.ships >= 15]
    
    for target, value in priority_targets[:10]:  # Top 10 targets
        if value <= 0:
            break
        
        # Check if already being attacked by us
        if target.id in gs.my_fleet_targets:
            incoming = sum(s for s, _ in gs.my_fleet_targets[target.id])
            if incoming > target.ships * 1.5:
                continue  # Already sending enough
        
        # Try to capture this target
        can_capture, plan = strat.can_capture(available_sources, target, 
                                              turns_limit=strat.turns_remaining)
        
        if can_capture and plan:
            # Execute the plan
            for src, ships, eta in plan:
                # Predict target position
                d = distance(src.x, src.y, target.x, target.y)
                if d < ROTATION_RADIUS_LIMIT - 8:
                    future_x, future_y = predict_position(target.x, target.y, 
                                                         gs.angular_vel, int(eta))
                    ang = angle_to(src.x, src.y, future_x, future_y)
                else:
                    ang = angle_to(src.x, src.y, target.x, target.y)
                
                # Safe path
                safe_ang = safe_angle(src.x, src.y, target.x, target.y)
                if safe_ang is not None:
                    moves.append([src.id, safe_ang, ships])
                    strat.used.add(src.id)
                    available_sources = [p for p in available_sources if p.id != src.id]
            
            # Stop if we've used most planets
            if len(strat.used) >= len(gs.my_planets) * 0.8:
                break
    
    return moves
