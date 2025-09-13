import time
import os

# --- Configuration ---
WORK_MINS = 25
SHORT_BREAK_MINS = 5
LONG_BREAK_MINS = 15
CYCLES_BEFORE_LONG_BREAK = 4

# --- ANSI Color Codes for Terminal Output ---
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def play_sound():
    """Plays a simple system beep sound."""
    # For Windows
    if os.name == 'nt':
        import winsound
        winsound.Beep(1000, 500) # Frequency 1000 Hz, Duration 500ms
    # For macOS and Linux
    else:
        os.system('echo -e "\\a"')

def countdown(minutes, session_type):
    """Runs a countdown timer for a given number of minutes."""
    seconds = minutes * 60
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        timer_display = f'{session_type}: {mins:02d}:{secs:02d}'
        print(timer_display, end="\r")
        time.sleep(1)
        seconds -= 1
    print() # Move to the next line after countdown finishes

def start_pomodoro():
    """Main function to run the Pomodoro timer."""
    print(f"{BOLD}🍅 Pomodoro Timer Started! 🍅{RESET}")
    for cycle in range(1, CYCLES_BEFORE_LONG_BREAK + 1):
        # Work Session
        print(f"\n{YELLOW}Cycle {cycle}: Time to focus!{RESET}")
        countdown(WORK_MINS, "Work")
        play_sound()

        # Break Session
        if cycle % CYCLES_BEFORE_LONG_BREAK == 0:
            print(f"\n{GREEN}Long break time! You've earned it.{RESET}")
            countdown(LONG_BREAK_MINS, "Long Break")
        else:
            print(f"\n{CYAN}Short break time! Relax.{RESET}")
            countdown(SHORT_BREAK_MINS, "Short Break")
        play_sound()

    print(f"\n{BOLD}All Pomodoro cycles complete! Great work.{RESET}")

if __name__ == "__main__":
    start_pomodoro()