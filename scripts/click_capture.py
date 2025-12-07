#!/usr/bin/env python3
"""
CAD Click Capture - Screenshot on Mouse Click
Captures screenshots every time you click, with XY coordinates logged.

Usage:
    python click_capture.py --project "UMass Waterproofing"
    
Hotkeys:
    Left/Right Click  - Capture screenshot with coordinates
    Ctrl+Shift+R      - Mark as "Research" capture (for literature/references)
    Ctrl+Shift+N      - Add a note to the last capture
    Ctrl+Shift+Q      - Stop capture session
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# Install dependencies if needed
def install_deps():
    deps = ["Pillow", "pynput"]
    for dep in deps:
        try:
            __import__(dep.lower().replace("-", "_").split("[")[0])
        except ImportError:
            print(f"Installing {dep}...")
            os.system(f"{sys.executable} -m pip install {dep}")

install_deps()

from PIL import Image, ImageGrab, ImageDraw, ImageFont
from pynput import mouse, keyboard

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path.home() / ".cad-observer" / "sessions"

# Capture settings
SHOW_CROSSHAIR = True           # Draw crosshair at click location
CROSSHAIR_SIZE = 30             # Size of crosshair in pixels
CROSSHAIR_COLOR = (255, 0, 0)   # Red
SHOW_COORDS_ON_IMAGE = True     # Overlay XY text on image
DEBOUNCE_MS = 300               # Ignore clicks within this time window

# ============================================================
# CAPTURE SESSION CLASS
# ============================================================

class ClickCaptureSession:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = OUTPUT_DIR / f"{self.session_id}_{project_name.replace(' ', '_')}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.frames = []
        self.frame_index = 0
        self.last_capture_time = 0
        self.running = True
        self.current_mode = "cad"  # "cad" or "research"
        self.pending_note = None
        
        # Session metadata
        self.session_meta = {
            "session_id": self.session_id,
            "project": project_name,
            "started": datetime.now().isoformat(),
            "capture_type": "click_triggered",
            "frames": []
        }
        
        self._save_meta()
        
    def _save_meta(self):
        """Save session metadata to JSON."""
        with open(self.session_dir / "session.json", "w") as f:
            json.dump(self.session_meta, f, indent=2)
    
    def capture(self, x: int, y: int, button: str, mode: str = None):
        """Capture screenshot with click coordinates."""
        # Debounce rapid clicks
        now = time.time() * 1000
        if now - self.last_capture_time < DEBOUNCE_MS:
            return
        self.last_capture_time = now
        
        capture_mode = mode or self.current_mode
        timestamp = datetime.now()
        
        # Capture screen
        screenshot = ImageGrab.grab()
        
        # Draw crosshair and coordinates if enabled
        if SHOW_CROSSHAIR or SHOW_COORDS_ON_IMAGE:
            draw = ImageDraw.Draw(screenshot)
            
            if SHOW_CROSSHAIR:
                # Horizontal line
                draw.line([(x - CROSSHAIR_SIZE, y), (x + CROSSHAIR_SIZE, y)], 
                         fill=CROSSHAIR_COLOR, width=2)
                # Vertical line
                draw.line([(x, y - CROSSHAIR_SIZE), (x, y + CROSSHAIR_SIZE)], 
                         fill=CROSSHAIR_COLOR, width=2)
                # Circle
                draw.ellipse([(x-5, y-5), (x+5, y+5)], outline=CROSSHAIR_COLOR, width=2)
            
            if SHOW_COORDS_ON_IMAGE:
                # Try to load a font, fall back to default
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                coord_text = f"X: {x}  Y: {y}"
                mode_text = f"[{capture_mode.upper()}]"
                
                # Draw background for text
                draw.rectangle([(10, 10), (200, 60)], fill=(0, 0, 0, 180))
                draw.text((15, 15), coord_text, fill=(0, 255, 0), font=font)
                draw.text((15, 35), mode_text, fill=(255, 255, 0), font=font)
        
        # Save screenshot
        filename = f"frame_{self.frame_index:04d}_{capture_mode}.png"
        filepath = self.session_dir / filename
        screenshot.save(filepath, "PNG")
        
        # Frame metadata
        frame_meta = {
            "index": self.frame_index,
            "timestamp": timestamp.isoformat(),
            "filename": filename,
            "click_x": x,
            "click_y": y,
            "button": button,
            "mode": capture_mode,
            "resolution": screenshot.size,
            "note": None,
            "questions_for_claude": []
        }
        
        self.frames.append(frame_meta)
        self.session_meta["frames"] = self.frames
        self._save_meta()
        
        # Console output
        mode_indicator = "📚" if capture_mode == "research" else "🖱️"
        print(f"{mode_indicator} [{self.frame_index:04d}] Click at ({x}, {y}) - {button} - {capture_mode}")
        
        self.frame_index += 1
        return frame_meta
    
    def add_note(self, note: str):
        """Add a note to the last capture."""
        if self.frames:
            self.frames[-1]["note"] = note
            self.session_meta["frames"] = self.frames
            self._save_meta()
            print(f"📝 Note added to frame {self.frame_index - 1}: {note[:50]}...")
    
    def set_mode(self, mode: str):
        """Switch capture mode."""
        self.current_mode = mode
        print(f"🔄 Switched to {mode.upper()} mode")
    
    def stop(self):
        """Stop the capture session."""
        self.running = False
        self.session_meta["ended"] = datetime.now().isoformat()
        self.session_meta["total_frames"] = self.frame_index
        self._save_meta()
        
        print(f"\n{'='*60}")
        print(f"✓ Session saved: {self.session_dir}")
        print(f"✓ Total frames: {self.frame_index}")
        print(f"{'='*60}")

# ============================================================
# INPUT LISTENERS
# ============================================================

class InputListener:
    def __init__(self, session: ClickCaptureSession):
        self.session = session
        self.ctrl_pressed = False
        self.shift_pressed = False
        
    def on_click(self, x, y, button, pressed):
        """Handle mouse clicks."""
        if not self.session.running:
            return False
            
        if pressed:  # Only capture on press, not release
            button_name = "left" if button == mouse.Button.left else "right"
            self.session.capture(x, y, button_name)
    
    def on_key_press(self, key):
        """Handle keyboard shortcuts."""
        if not self.session.running:
            return False
            
        try:
            # Track modifier keys
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift:
                self.shift_pressed = True
            
            # Check hotkey combinations
            if self.ctrl_pressed and self.shift_pressed:
                if hasattr(key, 'char'):
                    if key.char == 'r' or key.char == 'R':
                        # Toggle research mode
                        new_mode = "research" if self.session.current_mode == "cad" else "cad"
                        self.session.set_mode(new_mode)
                    elif key.char == 'n' or key.char == 'N':
                        # Prompt for note
                        print("\n📝 Enter note for last capture (press Enter when done):")
                        # Note: This blocks - for production, use async input
                    elif key.char == 'q' or key.char == 'Q':
                        # Quit
                        self.session.stop()
                        return False
                        
        except AttributeError:
            pass
    
    def on_key_release(self, key):
        """Track modifier key releases."""
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        elif key == keyboard.Key.shift:
            self.shift_pressed = False

# ============================================================
# MAIN
# ============================================================

def start_click_capture(project_name: str):
    """Start click-triggered capture session."""
    
    session = ClickCaptureSession(project_name)
    listener = InputListener(session)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  CAD Click Capture Started                                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Project: {project_name:<54} ║
║  Output: {str(session.session_dir):<55}║
╠══════════════════════════════════════════════════════════════════╣
║  CONTROLS:                                                        ║
║    Mouse Click      → Capture screenshot with XY coordinates      ║
║    Ctrl+Shift+R     → Toggle Research mode (for literature)       ║
║    Ctrl+Shift+Q     → Stop capture session                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Current Mode: CAD                                                ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Start listeners
    mouse_listener = mouse.Listener(on_click=listener.on_click)
    keyboard_listener = keyboard.Listener(
        on_press=listener.on_key_press,
        on_release=listener.on_key_release
    )
    
    mouse_listener.start()
    keyboard_listener.start()
    
    # Keep running until stopped
    try:
        while session.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        session.stop()
    
    mouse_listener.stop()
    keyboard_listener.stop()
    
    return session.session_dir

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Click-triggered CAD capture")
    parser.add_argument("--project", "-p", type=str, default="CAD Session",
                        help="Project name")
    
    args = parser.parse_args()
    start_click_capture(args.project)
