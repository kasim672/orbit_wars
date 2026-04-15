# 🚀 Quick Start - Get Running in 5 Minutes

## Step 1: Submit Your Bot (2 minutes)

### Web Upload (Easiest)
1. Open https://www.kaggle.com/competitions/orbit-wars
2. Click **"Submit to Competition"**
3. Click **"File Upload"** tab
4. Upload **`submission.py`**
5. Click **"Submit"**

✅ Done! Your bot is now competing!

## Step 2: Watch Your Bot (3 minutes)

1. Go to **"My Submissions"** tab
2. Wait 2-3 minutes for validation
3. Click on your submission
4. Click on a game to **watch replay**
5. See your bot in action! 🎮

## Step 3: Check Your Rank

1. Go to **"Leaderboard"** tab
2. Find your name
3. See your skill rating (μ)
4. Track your progress over time

## What's Next?

### Option A: Keep It Simple
- Watch more replays
- Identify obvious mistakes
- Make small tweaks to `submission.py`
- Submit again

### Option B: Level Up
1. Read `STRATEGY_GUIDE.md` (20 min)
2. Switch to `advanced_bot.py`:
   ```bash
   cp advanced_bot.py submission.py
   ```
3. Submit the advanced version
4. Compare performance

### Option C: Go Deep
1. Read all documentation
2. Test locally: `python test_local.py`
3. Implement custom strategies
4. Optimize and tune
5. Climb the leaderboard! 📈

## Files You Need to Know

| File | Purpose | When to Use |
|------|---------|-------------|
| `submission.py` | Basic bot | Submit this first |
| `advanced_bot.py` | Better bot | Use after first submission |
| `STRATEGY_GUIDE.md` | Learn tactics | Read to improve |
| `SUBMISSION_GUIDE.md` | How to submit | Reference as needed |
| `test_local.py` | Test locally | Before submitting |

## Common Questions

**Q: How many times can I submit?**
A: 5 times per day. Your latest 2 bots play games.

**Q: How long until I see results?**
A: 2-3 minutes for validation, 10-30 minutes for first games.

**Q: What if my bot errors?**
A: Download the error log, fix the issue, resubmit.

**Q: How do I improve my rank?**
A: Watch replays, read strategy guide, make improvements, repeat!

**Q: Can I test without submitting?**
A: Yes! Run `python test_local.py` (requires `pip install kaggle-environments`)

## Quick Tips

1. **Submit early** - Don't wait for perfection
2. **Watch replays** - They show what's working/failing
3. **Iterate fast** - Small improvements add up
4. **Read the docs** - Especially STRATEGY_GUIDE.md
5. **Have fun!** - It's a game! 🎮

## Need Help?

- **Rules unclear?** → Read `README.md`
- **How to submit?** → Read `SUBMISSION_GUIDE.md`
- **Strategy help?** → Read `STRATEGY_GUIDE.md`
- **Code questions?** → Check `example_usage.py`
- **Still stuck?** → Ask in Kaggle forums

## Your First Hour Checklist

- [ ] Submit `submission.py` to Kaggle
- [ ] Watch at least 3 game replays
- [ ] Read `STRATEGY_GUIDE.md`
- [ ] Identify one improvement to make
- [ ] Make the change
- [ ] Submit version 2
- [ ] Compare results

## Success Metrics

After your first submission:
- ✅ Bot validates successfully
- ✅ Bot plays games without errors
- ✅ Bot beats random opponent sometimes
- ✅ You understand what your bot is doing

After first day:
- ✅ Submitted 2-3 versions
- ✅ Identified strengths and weaknesses
- ✅ Have ideas for improvements
- ✅ Understand game mechanics

After first week:
- ✅ Consistent win rate against baseline
- ✅ Positive skill rating
- ✅ Bot handles most scenarios
- ✅ Climbing the leaderboard

## Ready? Let's Go! 🏁

```bash
# If you have Kaggle CLI installed:
kaggle competitions submit -c orbit-wars -f submission.py -m "v1.0 - First submission"

# Otherwise, use web upload at:
# https://www.kaggle.com/competitions/orbit-wars
```

**Good luck conquering the galaxy!** 🌌🚀

---

*Estimated time to first submission: 5 minutes*
*Estimated time to competitive bot: 1-2 hours*
*Estimated time to top 10%: 1-2 weeks*
