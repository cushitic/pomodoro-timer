import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os

# --- Constants ---
# Colors and styling for the GUI
BG_COLOR = "#2d2d2d"
FG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4a4a4a"
ACCENT_COLOR = "#ff6a6a"  # A reddish color for the timer
FONT_NAME = "Segoe UI"

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x550")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # --- Initialize Pygame Mixer for Sound ---
        try:
            pygame.mixer.init()
        except pygame.error:
            messagebox.showwarning("Audio Error", "Could not initialize audio player. Alerts will be silent.")
        
        # --- State Variables ---
        self.work_mins = tk.IntVar(value=25)
        self.short_break_mins = tk.IntVar(value=5)
        self.long_break_mins = tk.IntVar(value=15)
        self.total_cycles = tk.IntVar(value=4)
        self.task_names_str = tk.StringVar(value="Task 1, Task 2, Task 3, Task 4")
        self.alert_sound_path = tk.StringVar(value="")

        self.tasks = []
        self.current_cycle = 0
        self.current_session_type = "" # "Work", "Short Break", "Long Break"
        self.remaining_seconds = 0
        self.is_running = False
        self.timer_id = None

        # --- UI Setup ---
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_NAME, 10))
        style.configure("TButton", background=BUTTON_COLOR, foreground=FG_COLOR, font=(FONT_NAME, 10))
        style.configure("TEntry", fieldbackground="#3d3d3d", foreground=FG_COLOR, insertbackground=FG_COLOR, font=(FONT_NAME, 10))
        style.configure("TSpinbox", fieldbackground="#3d3d3d", foreground=FG_COLOR, insertbackground=FG_COLOR, font=(FONT_NAME, 10))

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Timer Display ---
        self.session_label = ttk.Label(main_frame, text="Ready to Start!", font=(FONT_NAME, 16, "bold"))
        self.session_label.pack(pady=(0, 5))
        
        self.timer_display = ttk.Label(main_frame, text="25:00", font=(FONT_NAME, 60, "bold"), foreground=ACCENT_COLOR)
        self.timer_display.pack(pady=10)

        self.task_label = ttk.Label(main_frame, text="Current Task: -", font=(FONT_NAME, 12))
        self.task_label.pack(pady=(0, 20))
        
        # --- Controls ---
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(pady=10)
        
        self.start_button = ttk.Button(controls_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(controls_frame, text="Pause", command=self.pause_timer)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = ttk.Button(controls_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=5)

        # --- Settings ---
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding=10)
        settings_frame.pack(pady=20, fill=tk.X)
        
        ttk.Label(settings_frame, text="Work (min):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(settings_frame, from_=1, to=90, textvariable=self.work_mins, width=5).grid(row=0, column=1, sticky="e")
        
        ttk.Label(settings_frame, text="Short Break (min):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(settings_frame, from_=1, to=30, textvariable=self.short_break_mins, width=5).grid(row=1, column=1, sticky="e")
        
        ttk.Label(settings_frame, text="Long Break (min):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.long_break_mins, width=5).grid(row=2, column=1, sticky="e")
        
        ttk.Label(settings_frame, text="Total Cycles:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Spinbox(settings_frame, from_=1, to=12, textvariable=self.total_cycles, width=5).grid(row=3, column=1, sticky="e")

        ttk.Label(settings_frame, text="Task Names (comma-separated):").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Entry(settings_frame, textvariable=self.task_names_str).grid(row=5, column=0, columnspan=2, sticky="ew", pady=2)
        
        ttk.Button(settings_frame, text="Browse for Alert Sound...", command=self.browse_sound).grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def browse_sound(self):
        filepath = filedialog.askopenfilename(
            title="Select Alert Sound",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        if filepath:
            self.alert_sound_path.set(filepath)
            self.root.title(f"Pomodoro Timer - {os.path.basename(filepath)}")

    def start_timer(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.tasks = [task.strip() for task in self.task_names_str.get().split(',') if task.strip()]
        
        if not self.tasks:
            messagebox.showerror("Error", "Please enter at least one task name.")
            self.reset_timer()
            return
            
        self.current_cycle = 0
        self.start_next_session()

    def start_next_session(self):
        if self.current_cycle >= self.total_cycles.get():
            self.session_label.config(text="All cycles complete!")
            self.task_label.config(text="Great work!")
            self.reset_timer(finished=True)
            return

        if self.current_session_type == "Work" or self.current_session_type == "":
            self.current_cycle += 1
            # It's time for a break
            if self.current_cycle % 4 == 0:
                self.current_session_type = "Long Break"
                self.remaining_seconds = self.long_break_mins.get() * 60
                self.session_label.config(text=f"Long Break ({self.current_cycle} / {self.total_cycles.get()})")
                self.task_label.config(text="Time to relax!")
            else:
                self.current_session_type = "Short Break"
                self.remaining_seconds = self.short_break_mins.get() * 60
                self.session_label.config(text=f"Short Break ({self.current_cycle} / {self.total_cycles.get()})")
                self.task_label.config(text="Quick break!")
        else: # If it was a break, start work
            self.current_session_type = "Work"
            self.remaining_seconds = self.work_mins.get() * 60
            task_index = (self.current_cycle - 1) % len(self.tasks)
            current_task = self.tasks[task_index]
            self.session_label.config(text=f"Work Cycle {self.current_cycle} / {self.total_cycles.get()}")
            self.task_label.config(text=f"Current Task: {current_task}")

        self.update_timer()

    def update_timer(self):
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            mins, secs = divmod(self.remaining_seconds, 60)
            self.timer_display.config(text=f"{mins:02d}:{secs:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.is_running and self.remaining_seconds == 0:
            self.play_alert()
            self.start_next_session()

    def pause_timer(self):
        if self.timer_id is None: # Can't pause if not started
            return
            
        self.is_running = not self.is_running
        if self.is_running:
            self.pause_button.config(text="Pause")
            self.update_timer()
        else:
            self.pause_button.config(text="Resume")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)

    def reset_timer(self, finished=False):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        self.is_running = False
        self.timer_id = None
        self.current_cycle = 0
        self.current_session_type = ""
        
        if not finished:
            self.session_label.config(text="Ready to Start!")
            self.task_label.config(text="Current Task: -")
        
        self.timer_display.config(text=f"{self.work_mins.get():02d}:00")
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(text="Pause")

    def play_alert(self):
        try:
            if self.alert_sound_path.get() and os.path.exists(self.alert_sound_path.get()):
                pygame.mixer.music.load(self.alert_sound_path.get())
                pygame.mixer.music.play()
            else:
                # Fallback to system beep if no sound file or pygame fails
                self.root.bell()
        except Exception:
            self.root.bell() # Fallback

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
