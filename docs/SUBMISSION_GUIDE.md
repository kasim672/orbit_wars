# Kaggle Submission Guide

## Quick Submission (3 Steps)

### Option 1: Web Upload (Easiest)

1. Go to https://www.kaggle.com/competitions/orbit-wars
2. Click "Submit to Competition" → "File Upload" tab
3. Upload `submission.py` (or `advanced_bot.py` renamed to `submission.py`)
4. Add a message like "v1.0 - Initial greedy expansion bot"
5. Click Submit

### Option 2: Kaggle CLI

```bash
# Install Kaggle CLI
pip install kaggle

# Configure API credentials (one-time setup)
# 1. Go to https://www.kaggle.com/settings
# 2. Click "Create New API Token"
# 3. Save kaggle.json to ~/.kaggle/

# Submit
kaggle competitions submit -c orbit-wars -f submission.py -m "v1.0 - Initial submission"
```

### Option 3: Kaggle Notebook

1. Create a new notebook on Kaggle
2. Copy contents of `submission.py` into a code cell
3. Add a cell at the end:
```python
# Export for submission
with open('submission.py', 'w') as f:
    f.write(open('/kaggle/working/submission.py').read())
```
4. Click "Submit to Competition"

## Which Bot to Submit?

### submission.py (Recommended for First Submission)
- **Pros**: Simple, fast, reliable
- **Cons**: Basic strategy
- **Use when**: Getting started, testing submission process

### advanced_bot.py (Recommended for Competitive Play)
- **Pros**: Defense, orbital prediction, better targeting
- **Cons**: More complex, slightly slower
- **Use when**: You want to climb the leaderboard

To submit advanced_bot.py:
```bash
cp advanced_bot.py submission.py
kaggle competitions submit -c orbit-wars -f submission.py -m "v2.0 - Advanced bot"
```

## Submission Limits

- **5 submissions per day**
- **2 active bots** (latest 2 submissions play games)
- **Best bot shown** on leaderboard

## After Submission

### 1. Check Validation
- Wait 1-2 minutes
- Check if submission shows "Complete" or "Error"
- If error, download logs to debug

### 2. Monitor Performance
- Go to "My Submissions" tab
- Watch your skill rating (μ) update
- Check win/loss record

### 3. Analyze Replays
- Click on individual games
- Watch replays to see what worked/failed
- Look for patterns in losses

## Submission Checklist

Before each submission:

- [ ] Test locally if possible (`python test_local.py`)
- [ ] Check for syntax errors
- [ ] Verify no external dependencies (only stdlib)
- [ ] Ensure agent function returns list of moves
- [ ] Add version number in submission message
- [ ] Document what changed from previous version

## Common Submission Errors

### Error: "Module not found"
- **Cause**: Using external libraries
- **Fix**: Only use Python standard library (math, collections, etc.)

### Error: "Timeout"
- **Cause**: Agent takes >1 second per turn
- **Fix**: Optimize code, reduce search depth, profile performance

### Error: "Invalid return value"
- **Cause**: Not returning list of moves
- **Fix**: Ensure agent returns `[[planet_id, angle, ships], ...]`

### Error: "Invalid move"
- **Cause**: Trying to launch from planet you don't own, or more ships than available
- **Fix**: Validate moves before returning

## Version Control Strategy

Keep track of your submissions:

```
v1.0 - Basic greedy expansion
v1.1 - Added sun avoidance
v1.2 - Improved target selection
v2.0 - Added defense logic
v2.1 - Orbital prediction
v2.2 - Comet strategies
v3.0 - Search-based planning
```

## Testing Before Submission

### Local Testing (Recommended)
```bash
pip install kaggle-environments
python test_local.py --bot submission.py --games 10
```

### Quick Validation
```python
# Test that agent runs without errors
from submission import agent

# Mock observation
obs = {
    'player': 0,
    'planets': [[0, 0, 25, 25, 2, 50, 3]],
    'fleets': [],
    'angular_velocity': 0.03,
    'initial_planets': [[0, 0, 25, 25, 2, 50, 3]],
    'comet_planet_ids': [],
    'step': 0
}

moves = agent(obs)
print(f"Moves: {moves}")
print("✓ Agent runs successfully")
```

## Leaderboard Strategy

### Early Competition (Now - Week 2)
- Submit often to test different strategies
- Focus on learning what works
- Don't worry about rating drops

### Mid Competition (Week 3-6)
- Refine your best approach
- Submit 2-3 times per day
- Analyze losses carefully

### Late Competition (Week 7-8)
- Conservative submissions
- Only submit improvements
- Save submission slots for final push

### Final Week
- Test extensively before submitting
- Use all 5 daily submissions strategically
- Monitor opponent strategies

## Getting Help

- **Forum**: https://www.kaggle.com/competitions/orbit-wars/discussion
- **Rules**: See README.md
- **Code Issues**: Check DEVELOPMENT.md

## Next Steps After First Submission

1. **Watch your first game replay**
   - See how your bot behaves
   - Identify obvious mistakes

2. **Compare with baseline**
   - How does your bot compare to random?
   - What's your win rate?

3. **Iterate quickly**
   - Make small improvements
   - Test and submit
   - Learn from each version

4. **Study top bots**
   - Watch replays of top players
   - What strategies do they use?
   - Can you adapt their tactics?

Good luck! 🚀
