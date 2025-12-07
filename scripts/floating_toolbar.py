#!/usr/bin/env python3
"""
CAD Observer - Floating Toolbar
Always-on-top minimal control panel for CAD observation sessions.

Features:
- Always stays on top of other windows (including AutoCAD)
- Minimal footprint, draggable
- Quick buttons for capture modes
- Real-time stats display
- Hotkey indicators
- Collapsible to icon-only mode

Usage:
    python floating_toolbar.py --project "Project Name"
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable

# Install dependencies
def install_deps():
    deps = ["Pillow", "pynput"]
    for dep in deps:
        try:
            __import__(dep.lower().replace("-", "_"))
        except ImportError:
            print(f"Installing {dep}...")
            os.system(f"{sys.executable} -m pip install {dep}")

install_deps()

import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageGrab, ImageDraw, ImageTk
from pynput import mouse, keyboard

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path.home() / ".cad-observer" / "sessions"
AUTOCAD_LOG_PATH = Path("C:/CADObserver/logs")
AUTOCAD_TASK_PATH = Path("C:/CADObserver/tasks")

# Colors (Dark theme for minimal distraction)
COLORS = {
    "bg": "#1a1a2e",
    "bg_light": "#16213e",
    "accent": "#0f3460",
    "highlight": "#e94560",
    "text": "#eaeaea",
    "text_dim": "#888888",
    "success": "#00d26a",
    "warning": "#ffc107",
    "cad_mode": "#4fc3f7",
    "research_mode": "#ba68c8"
}

# ============================================================
# SESSION STATE
# ============================================================

@dataclass
class SessionState:
    project_name: str = "CAD Session"
    session_id: str = ""
    session_dir: Optional[Path] = None
    is_recording: bool = False
    mode: str = "cad"  # "cad" or "research"
    click_count: int = 0
    command_count: int = 0
    last_command: str = ""
    last_capture_time: float = 0
    start_time: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================
# FLOATING TOOLBAR
# ============================================================

class FloatingToolbar:
    def __init__(self, project_name: str = "CAD Session"):
        self.state = SessionState(project_name=project_name)
        self.callbacks = {}
        self.expanded = True
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Mouse/keyboard listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        self.ctrl_pressed = False
        self.shift_pressed = False
        
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
        self._position_window()
        self._setup_bindings()
    
    def _setup_window(self):
        """Configure the main window."""
        self.root = tk.Tk()
        self.root.title("CAD Observer")
        
        # Remove window decorations for minimal look
        self.root.overrideredirect(True)
        
        # Always on top
        self.root.attributes("-topmost", True)
        
        # Slight transparency
        self.root.attributes("-alpha", 0.95)
        
        # Background color
        self.root.configure(bg=COLORS["bg"])
        
        # Prevent window from being hidden
        self.root.lift()
    
    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure button style
        style.configure("Toolbar.TButton",
            background=COLORS["accent"],
            foreground=COLORS["text"],
            borderwidth=0,
            focuscolor="none",
            padding=(8, 4)
        )
        style.map("Toolbar.TButton",
            background=[("active", COLORS["highlight"])]
        )
        
        # Mode button styles
        style.configure("CAD.TButton",
            background=COLORS["cad_mode"],
            foreground="#000000"
        )
        style.configure("Research.TButton",
            background=COLORS["research_mode"],
            foreground="#000000"
        )
    
    def _create_widgets(self):
        """Create toolbar widgets."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS["bg"], padx=2, pady=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title bar (draggable)
        self.title_bar = tk.Frame(self.main_frame, bg=COLORS["bg_light"], height=24)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # Icon/Logo
        self.icon_label = tk.Label(
            self.title_bar, 
            text="🔍", 
            bg=COLORS["bg_light"], 
            fg=COLORS["text"],
            font=("Segoe UI Emoji", 10)
        )
        self.icon_label.pack(side=tk.LEFT, padx=4)
        
        # Title
        self.title_label = tk.Label(
            self.title_bar,
            text="CAD Observer",
            bg=COLORS["bg_light"],
            fg=COLORS["text"],
            font=("Segoe UI", 9, "bold")
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Close button
        self.close_btn = tk.Label(
            self.title_bar,
            text="✕",
            bg=COLORS["bg_light"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        self.close_btn.pack(side=tk.RIGHT, padx=4)
        self.close_btn.bind("<Button-1>", lambda e: self.quit())
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.configure(fg=COLORS["highlight"]))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.configure(fg=COLORS["text_dim"]))
        
        # Collapse button
        self.collapse_btn = tk.Label(
            self.title_bar,
            text="─",
            bg=COLORS["bg_light"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        self.collapse_btn.pack(side=tk.RIGHT, padx=2)
        self.collapse_btn.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Expandable content
        self.content_frame = tk.Frame(self.main_frame, bg=COLORS["bg"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        
        # Status row
        self.status_frame = tk.Frame(self.content_frame, bg=COLORS["bg"])
        self.status_frame.pack(fill=tk.X, padx=4)
        
        # Recording indicator
        self.record_indicator = tk.Label(
            self.status_frame,
            text="●",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 12)
        )
        self.record_indicator.pack(side=tk.LEFT)
        
        # Status text
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=4)
        
        # Mode indicator
        self.mode_label = tk.Label(
            self.status_frame,
            text="CAD",
            bg=COLORS["cad_mode"],
            fg="#000000",
            font=("Segoe UI", 8, "bold"),
            padx=6,
            pady=1
        )
        self.mode_label.pack(side=tk.RIGHT)
        
        # Button row
        self.button_frame = tk.Frame(self.content_frame, bg=COLORS["bg"])
        self.button_frame.pack(fill=tk.X, padx=4, pady=4)
        
        # Start/Stop button
        self.start_btn = tk.Button(
            self.button_frame,
            text="▶ Start",
            bg=COLORS["success"],
            fg="#000000",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            command=self.toggle_recording
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        # Mode toggle button
        self.mode_btn = tk.Button(
            self.button_frame,
            text="📚",
            bg=COLORS["accent"],
            fg=COLORS["text"],
            font=("Segoe UI Emoji", 9),
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self.toggle_mode
        )
        self.mode_btn.pack(side=tk.LEFT, padx=2)
        
        # Manual capture button
        self.capture_btn = tk.Button(
            self.button_frame,
            text="📸",
            bg=COLORS["accent"],
            fg=COLORS["text"],
            font=("Segoe UI Emoji", 9),
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self.manual_capture
        )
        self.capture_btn.pack(side=tk.LEFT, padx=2)
        
        # Stats row
        self.stats_frame = tk.Frame(self.content_frame, bg=COLORS["bg"])
        self.stats_frame.pack(fill=tk.X, padx=4)
        
        self.clicks_label = tk.Label(
            self.stats_frame,
            text="Clicks: 0",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 8)
        )
        self.clicks_label.pack(side=tk.LEFT)
        
        self.commands_label = tk.Label(
            self.stats_frame,
            text="Cmds: 0",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 8)
        )
        self.commands_label.pack(side=tk.LEFT, padx=8)
        
        self.time_label = tk.Label(
            self.stats_frame,
            text="00:00",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 8)
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Hotkey hint row
        self.hotkey_frame = tk.Frame(self.content_frame, bg=COLORS["bg"])
        self.hotkey_frame.pack(fill=tk.X, padx=4, pady=2)
        
        self.hotkey_label = tk.Label(
            self.hotkey_frame,
            text="Ctrl+Shift+R: Mode | Ctrl+Shift+Q: Stop",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 7)
        )
        self.hotkey_label.pack()
        
        # Border effect
        self.root.configure(highlightbackground=COLORS["accent"], highlightthickness=1)
    
    def _position_window(self):
        """Position window in top-right corner."""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        window_width = 220
        x = screen_width - window_width - 20
        y = 20
        self.root.geometry(f"{window_width}x140+{x}+{y}")
    
    def _setup_bindings(self):
        """Setup window bindings."""
        # Make title bar draggable
        self.title_bar.bind("<Button-1>", self._start_drag)
        self.title_bar.bind("<B1-Motion>", self._on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self._stop_drag)
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        self.icon_label.bind("<Button-1>", self._start_drag)
        self.icon_label.bind("<B1-Motion>", self._on_drag)
        
        # Periodically ensure we stay on top
        self._stay_on_top()
        
        # Update timer
        self._update_timer()
    
    def _start_drag(self, event):
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def _on_drag(self, event):
        if self.dragging:
            x = self.root.winfo_x() + event.x - self.drag_start_x
            y = self.root.winfo_y() + event.y - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
    
    def _stop_drag(self, event):
        self.dragging = False
    
    def _stay_on_top(self):
        """Periodically ensure window stays on top."""
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.after(1000, self._stay_on_top)
    
    def _update_timer(self):
        """Update session timer."""
        if self.state.is_recording and self.state.start_time:
            elapsed = datetime.now() - self.state.start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        self.root.after(1000, self._update_timer)
    
    def toggle_expand(self):
        """Toggle between expanded and collapsed view."""
        if self.expanded:
            self.content_frame.pack_forget()
            self.root.geometry(f"220x24")
            self.collapse_btn.configure(text="□")
        else:
            self.content_frame.pack(fill=tk.BOTH, expand=True, pady=4)
            self.root.geometry(f"220x140")
            self.collapse_btn.configure(text="─")
        self.expanded = not self.expanded
    
    def toggle_recording(self):
        """Start or stop recording session."""
        if self.state.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start a capture session."""
        self.state.is_recording = True
        self.state.start_time = datetime.now()
        self.state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state.session_dir = OUTPUT_DIR / f"{self.state.session_id}_{self.state.project_name.replace(' ', '_')}"
        self.state.session_dir.mkdir(parents=True, exist_ok=True)
        self.state.click_count = 0
        self.state.command_count = 0
        
        # Update UI
        self.start_btn.configure(text="■ Stop", bg=COLORS["highlight"])
        self.status_label.configure(text="Recording...")
        self.record_indicator.configure(fg=COLORS["highlight"])
        
        # Start listeners
        self._start_listeners()
        
        # Save session metadata
        self._save_session_meta()
    
    def stop_recording(self):
        """Stop the capture session."""
        self.state.is_recording = False
        
        # Update UI
        self.start_btn.configure(text="▶ Start", bg=COLORS["success"])
        self.status_label.configure(text="Ready")
        self.record_indicator.configure(fg=COLORS["text_dim"])
        
        # Stop listeners
        self._stop_listeners()
        
        # Final save
        self._save_session_meta(final=True)
    
    def toggle_mode(self):
        """Toggle between CAD and Research mode."""
        if self.state.mode == "cad":
            self.state.mode = "research"
            self.mode_label.configure(text="RESEARCH", bg=COLORS["research_mode"])
            self.mode_btn.configure(text="🖱️")
        else:
            self.state.mode = "cad"
            self.mode_label.configure(text="CAD", bg=COLORS["cad_mode"])
            self.mode_btn.configure(text="📚")
    
    def manual_capture(self):
        """Manually trigger a capture."""
        if self.state.is_recording:
            # Get mouse position
            x, y = self.root.winfo_pointerx(), self.root.winfo_pointery()
            self._capture_screenshot(x, y, "manual")
    
    def _start_listeners(self):
        """Start mouse and keyboard listeners."""
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.mouse_listener.start()
        self.keyboard_listener.start()
    
    def _stop_listeners(self):
        """Stop mouse and keyboard listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
    
    def _on_click(self, x, y, button, pressed):
        """Handle mouse clicks."""
        if not self.state.is_recording:
            return
        
        if pressed:
            # Debounce
            now = time.time() * 1000
            if now - self.state.last_capture_time < 300:
                return
            self.state.last_capture_time = now
            
            button_name = "left" if button == mouse.Button.left else "right"
            self._capture_screenshot(x, y, button_name)
    
    def _on_key_press(self, key):
        """Handle keyboard shortcuts."""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift:
                self.shift_pressed = True
            
            if self.ctrl_pressed and self.shift_pressed:
                if hasattr(key, 'char'):
                    char = key.char.lower() if key.char else None
                    if char == 'r':
                        self.root.after(0, self.toggle_mode)
                    elif char == 'q':
                        self.root.after(0, self.stop_recording)
        except:
            pass
    
    def _on_key_release(self, key):
        """Handle key releases."""
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        elif key == keyboard.Key.shift:
            self.shift_pressed = False
    
    def _capture_screenshot(self, x: int, y: int, button: str):
        """Capture a screenshot."""
        if not self.state.session_dir:
            return
        
        timestamp = datetime.now()
        screenshot = ImageGrab.grab()
        
        # Draw crosshair
        draw = ImageDraw.Draw(screenshot)
        draw.line([(x - 20, y), (x + 20, y)], fill=(255, 0, 0), width=2)
        draw.line([(x, y - 20), (x, y + 20)], fill=(255, 0, 0), width=2)
        draw.ellipse([(x-4, y-4), (x+4, y+4)], outline=(255, 0, 0), width=2)
        
        # Save
        filename = f"frame_{self.state.click_count:04d}_{self.state.mode}.png"
        filepath = self.state.session_dir / filename
        screenshot.save(filepath, "PNG")
        
        # Update state
        self.state.click_count += 1
        self.clicks_label.configure(text=f"Clicks: {self.state.click_count}")
        
        # Flash indicator
        self._flash_capture()
        
        # Save metadata
        self._save_session_meta()
    
    def _flash_capture(self):
        """Flash the record indicator on capture."""
        original_color = self.record_indicator.cget("fg")
        self.record_indicator.configure(fg=COLORS["success"])
        self.root.after(100, lambda: self.record_indicator.configure(fg=original_color))
    
    def _save_session_meta(self, final=False):
        """Save session metadata."""
        if not self.state.session_dir:
            return
        
        meta = {
            "session_id": self.state.session_id,
            "project": self.state.project_name,
            "started": self.state.start_time.isoformat() if self.state.start_time else None,
            "click_count": self.state.click_count,
            "command_count": self.state.command_count,
            "capture_type": "floating_toolbar"
        }
        
        if final:
            meta["ended"] = datetime.now().isoformat()
            meta["total_captures"] = self.state.click_count
        
        with open(self.state.session_dir / "session.json", "w") as f:
            json.dump(meta, f, indent=2)
    
    def quit(self):
        """Quit the application."""
        if self.state.is_recording:
            self.stop_recording()
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the toolbar."""
        self.root.mainloop()

# ============================================================
# MAIN
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CAD Observer Floating Toolbar")
    parser.add_argument("--project", "-p", type=str, default="CAD Session",
                        help="Project name")
    args = parser.parse_args()
    
    toolbar = FloatingToolbar(project_name=args.project)
    toolbar.run()

if __name__ == "__main__":
    main()
