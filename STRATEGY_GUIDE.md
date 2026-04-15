# Orbit Wars Strategy Guide

## Core Concepts

### 1. Economic Advantage
- **Production is king**: A planet with production 5 generates 5 ships/turn
- Over 100 turns, that's 500 ships
- Capturing high-production planets early pays off massively

### 2. Fleet Speed Mechanics
```
speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000)) ^ 1.5
```
- 1 ship: 1.0 units/turn
- 100 ships: ~3.5 units/turn
- 500 ships: ~5.0 units/turn
- 1000 ships: 6.0 units/turn (max)

**Key insight**: Larger fleets arrive faster, so sometimes sending more ships is better even if overkill.

### 3. Combat Resolution
```
1. Group fleets by owner
2. Largest vs second largest → difference survives
3. Survivor vs garrison → winner takes planet
```

**Example**:
- Planet has 50 ships (Player 1)
- Player 2 sends 60 ships
- Player 3 sends 55 ships
- Result: Player 2 wins with 5 ships (60-55), then fights garrison (5-50), Player 1 keeps planet with 45 ships

**Key insight**: Third-party interference can ruin your attacks!

### 4. Orbital Mechanics
- Planets close to center orbit at 0.025-0.05 rad/turn
- Must predict future position for accurate targeting
- Orbiting planets can "dodge" poorly aimed fleets

### 5. The Sun
- Radius 10 at center (50, 50)
- Destroys any fleet that crosses it
- Must path around it for certain routes

## Strategic Phases

### Early Game (Turns 0-100)

**Goal**: Expand rapidly

**Priorities**:
1. Capture nearby neutral planets
2. Focus on high-production targets
3. Don't worry about defense yet
4. Avoid costly battles with other players

**Key metrics**:
- Planets controlled
- Total production rate
- Map coverage

**Common mistakes**:
- Being too conservative (not expanding fast enough)
- Attacking other players too early
- Ignoring high-production planets

### Mid Game (Turns 100-350)

**Goal**: Consolidate and optimize

**Priorities**:
1. Defend your territory
2. Disrupt enemy production
3. Capture comets opportunistically
4. Build ship reserves

**Key metrics**:
- Total ships (planets + fleets)
- Production advantage
- Territory control

**Common mistakes**:
- Overextending (attacking too many targets)
- Ignoring defense
- Wasting ships on low-value targets

### Late Game (Turns 350-500)

**Goal**: Maximize final score

**Priorities**:
1. Count ships carefully
2. Disrupt leader if you're behind
3. Defend if you're ahead
4. Time attacks to arrive before turn 500

**Key metrics**:
- Total ships (this is the score!)
- Ships in transit (will they arrive in time?)
- Opponent ship counts

**Common mistakes**:
- Launching attacks that won't arrive in time
- Leaving ships idle on planets
- Not counting final scores correctly

## Advanced Tactics

### 1. Fleet Timing
- Coordinate multiple fleets to arrive simultaneously
- Overwhelm defenses with combined force
- Time attacks to arrive just after enemy production

### 2. Interception
- Send fleets to intercept enemy fleets
- Meet them at a neutral planet
- Force combat on your terms

### 3. Feints
- Threaten one planet to force defense
- Attack a different target
- Split enemy forces

### 4. Economic Warfare
- Target enemy's highest production planets
- Even if you can't hold them, deny production
- Force enemy to spend ships on recapture

### 5. Comet Strategies

**Comet spawns**: Turns 50, 150, 250, 350, 450

**Pros**:
- Free production if captured
- Can be used as forward bases
- Spawn with random ships (sometimes easy to capture)

**Cons**:
- Leave the board eventually
- Ships on departing comets are lost
- Unpredictable trajectories

**Strategy**:
- Capture early comets (turns 50-150) for production
- Ignore late comets (turn 450) unless desperate
- Use comet paths to predict positions
- Launch from comets before they leave

### 6. Sun Routing
- Direct paths may cross sun
- Route around sun adds distance
- Sometimes better to wait for orbital rotation

**Pathfinding**:
```
If direct path crosses sun:
  Try angles ±π/8, ±π/4, ±π/3
  Pick first safe angle
  If none safe, skip target
```

### 7. Orbital Prediction

For orbiting planets:
```python
# Current angle
angle = atan2(planet.y - 50, planet.x - 50)

# Future angle
future_angle = angle + angular_velocity * turns

# Future position
future_x = 50 + radius * cos(future_angle)
future_y = 50 + radius * sin(future_angle)
```

**Lead the target**: Aim where planet will be, not where it is.

## Player Count Strategies

### 2-Player Games
- More aggressive
- Direct confrontation inevitable
- Economy matters more (longer games)
- Control center of map

### 4-Player Games
- More chaotic
- Avoid early fights
- Let others weaken each other
- Expand into empty quadrants
- Watch for kingmaker scenarios

## Common Patterns

### The Snowball
- Get early economic lead
- Use production advantage to expand faster
- Compound advantage over time
- Hard to stop once started

**Counter**: Disrupt early, target high-production planets

### The Turtle
- Defend heavily
- Build massive reserves
- Strike late with overwhelming force

**Counter**: Deny expansion, force them to fight

### The Swarm
- Constant small attacks
- Keep enemy off balance
- Death by a thousand cuts

**Counter**: Consolidate defenses, ignore small threats

### The Opportunist
- Wait for others to fight
- Capture weakened targets
- Third-party interference

**Counter**: Secure planets quickly, don't leave openings

## Optimization Checklist

### Target Selection
- [ ] Prioritize high production
- [ ] Consider distance
- [ ] Account for travel time
- [ ] Check sun collision
- [ ] Predict orbital position
- [ ] Evaluate competition (other players targeting same planet?)

### Fleet Sizing
- [ ] Enough to overcome garrison
- [ ] Buffer for production during travel
- [ ] Safety margin for errors
- [ ] Keep defensive reserve
- [ ] Consider fleet speed benefits

### Defense
- [ ] Track incoming enemy fleets
- [ ] Calculate arrival times
- [ ] Send reinforcements if needed
- [ ] Abandon lost causes
- [ ] Prioritize high-value planets

### Resource Allocation
- [ ] Don't leave ships idle
- [ ] Balance offense and defense
- [ ] Keep production planets safe
- [ ] Use low-production planets as staging areas

## Metrics to Track

### Economic
- Total production rate
- Production per planet (average)
- Planets controlled

### Military
- Total ships (planets + fleets)
- Ships in fleets (offensive capability)
- Ships on planets (defensive capability)
- Fleet count

### Positional
- Map coverage
- Distance to neutral planets
- Distance to enemy planets
- Control of center

## Debugging Your Strategy

### If you're losing early:
- Expand faster
- Target closer planets
- Improve fleet sizing
- Check for illegal moves

### If you're losing mid-game:
- Add defense logic
- Better target prioritization
- Avoid overextending
- Track enemy fleets

### If you're losing late:
- Count ships more carefully
- Time attacks better
- Defend when ahead
- Attack when behind

## Advanced Topics

### Search Algorithms
- Minimax: Evaluate move sequences
- Alpha-beta pruning: Optimize search
- Monte Carlo: Simulate random games
- Beam search: Explore top N options

### Machine Learning
- Feature extraction: Convert game state to numbers
- Evaluation function: Score positions
- Policy network: Choose actions
- Self-play: Train by playing against yourself

### Opponent Modeling
- Track opponent behavior
- Predict their moves
- Exploit patterns
- Adapt strategy

## Resources

- Watch top player replays
- Study forum discussions
- Test against different opponents
- Iterate quickly

## Final Tips

1. **Start simple**: Get something working first
2. **Test often**: Submit early and often
3. **Learn from losses**: Every loss teaches something
4. **Optimize incrementally**: Small improvements add up
5. **Have fun**: It's a game!

Good luck conquering the galaxy! 🌌
