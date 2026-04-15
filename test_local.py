"""
Local testing script for Orbit Wars bot
Requires: pip install kaggle-environments
"""

try:
    from kaggle_environments import make
    import importlib.util
    import sys
    
    def load_agent(filepath):
        """Load agent from file."""
        spec = importlib.util.spec_from_file_location("agent_module", filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules["agent_module"] = module
        spec.loader.exec_module(module)
        return module.agent
    
    def test_bot(bot_file="submission.py", opponent="random", num_games=5):
        """Test bot locally."""
        print(f"Testing {bot_file} against {opponent}...")
        print("=" * 60)
        
        wins = 0
        losses = 0
        ties = 0
        
        for game_num in range(num_games):
            print(f"\nGame {game_num + 1}/{num_games}")
            
            # Create environment
            env = make("orbit_wars", debug=False)
            
            # Run game
            if opponent == "self":
                result = env.run([bot_file, bot_file])
            else:
                result = env.run([bot_file, opponent])
            
            # Check result
            rewards = env.state[0]['reward']
            if rewards is None:
                print("  Result: Error or incomplete game")
                continue
            
            player_reward = rewards if isinstance(rewards, (int, float)) else rewards[0]
            
            if player_reward > 0:
                wins += 1
                print(f"  Result: WIN (reward: {player_reward})")
            elif player_reward < 0:
                losses += 1
                print(f"  Result: LOSS (reward: {player_reward})")
            else:
                ties += 1
                print(f"  Result: TIE")
        
        print("\n" + "=" * 60)
        print(f"Final Results: {wins} wins, {losses} losses, {ties} ties")
        print(f"Win Rate: {wins/num_games*100:.1f}%")
        
        return wins, losses, ties
    
    def visualize_game(bot_file="submission.py", opponent="random"):
        """Run and visualize a single game."""
        print(f"Running visualization: {bot_file} vs {opponent}")
        
        env = make("orbit_wars", debug=True)
        env.run([bot_file, opponent])
        
        # This will open in Jupyter or save HTML
        try:
            env.render(mode="ipython")
        except:
            print("Visualization requires Jupyter notebook")
            print("Game completed. Check env.state for results.")
        
        return env
    
    if __name__ == "__main__":
        import argparse
        
        parser = argparse.ArgumentParser(description="Test Orbit Wars bot locally")
        parser.add_argument("--bot", default="submission.py", help="Bot file to test")
        parser.add_argument("--opponent", default="random", help="Opponent (random, self, or file)")
        parser.add_argument("--games", type=int, default=5, help="Number of games")
        parser.add_argument("--visualize", action="store_true", help="Visualize one game")
        
        args = parser.parse_args()
        
        if args.visualize:
            visualize_game(args.bot, args.opponent)
        else:
            test_bot(args.bot, args.opponent, args.games)

except ImportError:
    print("Error: kaggle-environments not installed")
    print("Install with: pip install kaggle-environments")
    print("\nAlternatively, you can test by submitting directly to Kaggle")
