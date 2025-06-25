import time
import random
import sys
import os
from datetime import datetime

# For Windows compatibility of colors
try:
    import colorama
    colorama.init()
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False


class TimerGame:
    def __init__(self):
        self.target_time = 0
        self.start_time = 0
        self.elapsed = 0
        self.mode = "hidden"  # "hidden" or "visible"
        self.difficulty = "medium"  # "easy", "medium", "hard"
        self.player = None  # Will be set during registration
        self.leaderboard_file = "leaderboard.txt"
        self.ensure_leaderboard_file()
        
    def ensure_leaderboard_file(self):
        """Create leaderboard file if it doesn't exist"""
        if not os.path.exists(self.leaderboard_file):
            open(self.leaderboard_file, 'a').close()
    
    def register_player(self):
        """Register a new player"""
        self.clear_screen()
        print("\n" + " PLAYER REGISTRATION ".center(60, "="))
        
        while True:
            name = input("\nEnter your name: ").strip()
            if name:
                self.player = name
                print(f"\nWelcome, {self.player}!")
                time.sleep(1)
                break
            else:
                print("Please enter a valid name.")
    
    def save_to_leaderboard(self, score):
        """Save the current score to the leaderboard"""
        if not self.player:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"{self.player},{score:.3f},{self.difficulty},{self.mode},{timestamp}\n"
        
        # Add to leaderboard
        with open(self.leaderboard_file, 'a') as f:
            f.write(entry)
    
    def get_leaderboard(self):
        """Retrieve and sort leaderboard entries"""
        if not os.path.exists(self.leaderboard_file):
            return []
        
        leaderboard = []
        with open(self.leaderboard_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    try:
                        score = float(parts[1])
                        leaderboard.append({
                            'player': parts[0],
                            'score': score,
                            'difficulty': parts[2],
                            'mode': parts[3],
                            'date': parts[4]
                        })
                    except:
                        continue
        
        # Sort by score, ascending order
        leaderboard.sort(key=lambda x: x['score'])
        return leaderboard
    
    def display_leaderboard(self):
        """Display the leaderboard"""
        leaderboard = self.get_leaderboard()
        
        if COLORS_ENABLED:
            print("\033[1;35m" + " LEADERBOARD ".center(60, "=") + "\033[0m")
            print("\033[1;36mRank | Player          | Score   | Difficulty | Mode    | Date\033[0m")
            print("\033[1;36m" + "-" * 60 + "\033[0m")
        else:
            print(" LEADERBOARD ".center(60, "="))
            print("Rank | Player          | Score   | Difficulty | Mode    | Date")
            print("-" * 60)
        
        if not leaderboard:
            print("No records yet! Play some games to appear here.")
            return
            
        for i, entry in enumerate(leaderboard[:10], 1):
            player_display = entry['player'][:15] + (entry['player'][15:] and '..')
            score_display = f"{entry['score']:.3f}"
            print(f"{i:<4} | {player_display:<15} | {score_display:<7} | "
                  f"{entry['difficulty']:<10} | {entry['mode']:<7} | {entry['date']}")
    
    def clear_screen(self):
        """Clear the console screen"""
        print('\033c', end='')  # ANSI escape code to clear screen
        
    def print_header(self):
        """Print game header with title and stats"""
        player_display = self.player if self.player else "Guest"
        
        if COLORS_ENABLED:
            print("\033[1;35m" + "=" * 60)  # Purple
            print(f" TIMER COUNTDOWN GAME ".center(60))
            print("=" * 60)
            print(f" Player: {player_display} ".center(60))
            print(f" Mode: {self.mode.capitalize()} | Difficulty: {self.difficulty.capitalize()} ".center(60))
            print("=" * 60 + "\033[0m")  # Reset color
        else:
            print("=" * 60)
            print(f" TIMER COUNTDOWN GAME ".center(60))
            print("=" * 60)
            print(f" Player: {player_display} ".center(60))
            print(f" Mode: {self.mode.capitalize()} | Difficulty: {self.difficulty.capitalize()} ".center(60))
            print("=" * 60)
            
    def get_difficulty_range(self):
        """Get time range based on difficulty"""
        if self.difficulty == "easy":
            return (5, 10)
        elif self.difficulty == "medium":
            return (3, 15)
        else:  # hard
            return (1, 20)
            
    def generate_target(self):
        """Generate random target time based on difficulty"""
        min_time, max_time = self.get_difficulty_range()
        self.target_time = random.uniform(min_time, max_time)
        
    def display_target(self):
        """Display the target time if mode is visible"""
        if self.mode == "visible":
            if COLORS_ENABLED:
                print("\033[1;33m" + f" TARGET TIME: {self.target_time:.3f} seconds ".center(60) + "\033[0m")
            else:
                print(f" TARGET TIME: {self.target_time:.3f} seconds ".center(60))
        else:
            min_time, max_time = self.get_difficulty_range()
            if COLORS_ENABLED:
                print("\033[1;33m" + f" TARGET TIME: Hidden ({min_time}-{max_time} seconds) ".center(60) + "\033[0m")
            else:
                print(f" TARGET TIME: Hidden ({min_time}-{max_time} seconds) ".center(60))
                
    def draw_timer(self, elapsed, max_width=50):
        """Draw a visual representation of the timer"""
        # Calculate progress bar width
        progress = min(1.0, elapsed / self.target_time) if self.target_time > 0 else 0
        
        # Create progress bar
        bar_width = int(max_width * progress)
        progress_bar = "█" * bar_width + "-" * (max_width - bar_width)
        
        # Color coding
        if COLORS_ENABLED:
            if progress < 0.3:
                color_code = "\033[1;32m"  # Green
            elif progress < 0.7:
                color_code = "\033[1;33m"  # Yellow
            else:
                color_code = "\033[1;31m"  # Red
                
            print(f"{color_code}{progress_bar}\033[0m")
            print(f"{color_code}Elapsed: {elapsed:.3f}s | Target: {self.target_time:.3f}s\033[0m")
        else:
            print(progress_bar)
            print(f"Elapsed: {elapsed:.3f}s | Target: {self.target_time:.3f}s")
        
    def show_results(self, elapsed, difference):
        """Display game results with visual feedback"""
        print("\n" + " RESULTS ".center(60, "="))
        
        # Display timing information
        if COLORS_ENABLED:
            print(f"\033[1;34mTarget time was: {self.target_time:.3f} seconds\033[0m")
            print(f"\033[1;36mYou stopped at: {elapsed:.3f} seconds\033[0m")
            print(f"\033[1;35mDifference: {difference:.3f} seconds\033[0m")
        else:
            print(f"Target time was: {self.target_time:.3f} seconds")
            print(f"You stopped at: {elapsed:.3f} seconds")
            print(f"Difference: {difference:.3f} seconds")
        
        # Performance feedback
        if difference <= 0.05:
            feedback = "🎯 PERFECT HIT! You're a timing master! 🎯"
            color = "\033[1;32m"  # Green
        elif difference <= 0.1:
            feedback = "👍 EXCELLENT! Incredible precision! 👍"
            color = "\033[1;32m"  # Green
        elif difference <= 0.2:
            feedback = "👏 GREAT JOB! Very close! 👏"
            color = "\033[1;33m"  # Yellow
        elif difference <= 0.3:
            feedback = "🔔 Good effort! Within 0.3 seconds 🔔"
            color = "\033[1;33m"  # Yellow
        elif difference <= 0.5:
            feedback = "✨ Not bad! Practice makes perfect ✨"
            color = "\033[1;33m"  # Yellow
        else:
            feedback = "💤 Missed! Keep trying! 💤"
            color = "\033[1;31m"  # Red
            
        if COLORS_ENABLED:
            print(f"\n{color}{feedback.center(60)}\033[0m")
        else:
            print(f"\n{feedback.center(60)}")
            
    def play_round(self):
        """Play one round of the game"""
        self.clear_screen()
        self.print_header()
        self.generate_target()
        self.display_target()
        
        print("\nPress ENTER to START the timer...")
        input()
        
        self.start_time = time.time()
        last_update = time.time()
        
        print("\nTIMER RUNNING... Press ENTER to STOP!")
        print()
        
        # Real-time display loop
        while True:
            current_time = time.time()
            self.elapsed = current_time - self.start_time
            
            # Update display every 0.05 seconds for smooth animation
            if current_time - last_update >= 0.05:
                self.clear_screen()
                self.print_header()
                self.display_target()
                print()
                self.draw_timer(self.elapsed)
                print("\nTIMER RUNNING... Press ENTER to STOP!")
                last_update = current_time
            
            # Check for key press without blocking
            try:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = sys.stdin.readline()
                    if line:
                        break
            except:
                # Fallback for Windows if select doesn't work
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        if msvcrt.getch() == b'\r':  # Enter key
                            break
                except:
                    pass
        
        # Record final time
        stop_time = time.time()
        self.elapsed = stop_time - self.start_time
        difference = abs(self.elapsed - self.target_time)
        
        # Save to leaderboard
        if self.player:
            self.save_to_leaderboard(difference)
        
        # Show results
        self.clear_screen()
        self.print_header()
        self.show_results(self.elapsed, difference)
        
        return difference
        
    def settings_menu(self):
        """Display settings menu"""
        while True:
            self.clear_screen()
            self.print_header()
            
            print("\nSETTINGS MENU")
            print("1. Toggle Target Visibility (Current: {})".format(self.mode.capitalize()))
            print("2. Change Difficulty (Current: {})".format(self.difficulty.capitalize()))
            print("3. Change Player")
            print("4. Return to Main Menu")
            
            choice = input("\nSelect an option (1-4): ")
            
            if choice == "1":
                self.mode = "visible" if self.mode == "hidden" else "hidden"
                print(f"Target visibility set to: {self.mode}")
                time.sleep(1)
            elif choice == "2":
                print("\nSelect Difficulty:")
                print("1. Easy (5-10 seconds)")
                print("2. Medium (3-15 seconds)")
                print("3. Hard (1-20 seconds)")
                diff_choice = input("Select difficulty (1-3): ")
                
                if diff_choice == "1":
                    self.difficulty = "easy"
                elif diff_choice == "2":
                    self.difficulty = "medium"
                elif diff_choice == "3":
                    self.difficulty = "hard"
                else:
                    print("Invalid choice. Keeping current difficulty.")
                    
                time.sleep(1)
            elif choice == "3":
                self.register_player()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please select 1-4.")
                time.sleep(1)
                
    def main_menu(self):
        """Display main menu and handle game flow"""
        # Register player if not already registered
        if not self.player:
            self.register_player()
            
        while True:
            self.clear_screen()
            self.print_header()
            
            print("\nMAIN MENU")
            print("1. Play Game")
            print("2. Settings")
            print("3. View Leaderboard")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4): ")
            
            if choice == "1":
                self.play_round()
                print("\nPress ENTER to continue...")
                input()
            elif choice == "2":
                self.settings_menu()
            elif choice == "3":
                self.clear_screen()
                self.print_header()
                self.display_leaderboard()
                print("\nPress ENTER to continue...")
                input()
            elif choice == "4":
                print("\nThanks for playing!")
                break
            else:
                print("Invalid choice. Please select 1-4.")
                time.sleep(1)

# For platforms where select is available
try:
    import select
except ImportError:
    pass

if __name__ == "__main__":
    try:
        game = TimerGame()
        game.main_menu()
    except KeyboardInterrupt:
        print("\n\nGame exited")
    finally:
        # For EXE: Prevent window from closing immediately
        if sys.stdout.isatty():  # Only if running in terminal
            input("\nPress Enter to exit...")