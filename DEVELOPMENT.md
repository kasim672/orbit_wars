# Orbit Wars Bot - Development Guide

## Quick Start

### 1. Submit to Kaggle

You can submit directly using the Kaggle CLI:

```bash
kaggle competitions submit -c orbit-wars -f submission.py -m "Initial submission"
```

Or upload via the web interface:
1. Go to https://www.kaggle.com/competitions/orbit-wars
2. Click "Submit to Competition"
3. Upload `submission.py`

### 2. Test Locally

Install kaggle-environments:
```bash
pip install kaggle-environments
```

Test your bot:
```python
from kaggle_environments import make

env = make("orbit_wars", debug=True)
env.run(["submission.py", "submission.py"])
env.render(mode="ipython")
```

## Current Bot Strategy

The current implementation is a **greedy expansion bot**:

1. **Target Selection**: Evaluates all neutral and enemy planets based on:
   - Production value (higher production = better)
   - Distance (closer = better)
   - Ship cost (fewer ships needed = better)
   - Neutral bonus (neutral planets preferred)

2. **Fleet Sizing**: Calculates ships needed to:
   - Overcome current garrison
   - Account for production during travel
   - Add safety margin

3. **Safety Checks**:
   - Avoids paths that cross the sun
   - Keeps 20% garrison for defense
   - Skips planets with too few ships

## Architecture

```
submission.py
├── Constants (CENTER, SUN_RADIUS, etc.)
├── Data Structures (Planet, Fleet classes)
├── Math Utilities (distance, angles, predictions)
├── Game State (parsing and categorization)
├── Strategy (target selection, fleet sizing)
└── Agent (main entry point)
```

## Improvement Roadmap

### Phase 1: Enhanced Basics (Week 1)
- [ ] Implement orbital prediction for moving planets
- [ ] Add defense logic (respond to incoming threats)
- [ ] Improve fleet sizing with combat simulation
- [ ] Add multi-target coordination

### Phase 2: Advanced Strategy (Week 2)
- [ ] Implement comet capture strategies
- [ ] Add opponent modeling
- [ ] Optimize resource allocation
- [ ] Handle 2-player vs 4-player differently

### Phase 3: Search & Optimization (Week 3)
- [ ] Add minimax search for tactical decisions
- [ ] Implement Monte Carlo tree search
- [ ] Optimize performance (profiling)
- [ ] Parameter tuning

### Phase 4: ML Integration (Week 4+)
- [ ] Feature extraction from game state
- [ ] Train evaluation function
- [ ] Reinforcement learning via self-play
- [ ] Ensemble methods

## Key Metrics to Track

- **Win Rate**: Against baseline bots
- **Average Score**: Total ships at game end
- **Expansion Speed**: Planets captured per turn
- **Efficiency**: Ships lost vs ships gained
- **Leaderboard Position**: Skill rating on Kaggle

## Testing Strategy

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test full agent
3. **Replay Analysis**: Study losing games
4. **A/B Testing**: Compare strategy variants

## Performance Optimization

Current time budget: 1 second per turn

Tips:
- Precompute static data
- Use efficient data structures
- Profile hot paths
- Cache expensive calculations
- Limit search depth

## Common Issues

### Bot Times Out
- Reduce search depth
- Optimize expensive calculations
- Add early termination

### Bot Loses to Baseline
- Improve target selection
- Add defense logic
- Better fleet sizing

### Bot Makes Illegal Moves
- Validate ship counts
- Check planet ownership
- Verify angles are in radians

## Resources

- Competition: https://www.kaggle.com/competitions/orbit-wars
- Rules: See README.md
- Forum: https://www.kaggle.com/competitions/orbit-wars/discussion
- Leaderboard: https://www.kaggle.com/competitions/orbit-wars/leaderboard

## Submission Checklist

Before each submission:
- [ ] Test locally with kaggle-environments
- [ ] Verify no syntax errors
- [ ] Check time performance (<1 second)
- [ ] Update submission message
- [ ] Track version number
- [ ] Document changes

## Version History

### v1.0 - Initial Submission
- Basic greedy expansion strategy
- Target evaluation based on production/distance
- Sun avoidance
- Simple fleet sizing
