#!/usr/bin/env python3
"""
CAD Observer - Unified Session
Combines click capture + AutoCAD log monitoring for complete session tracking.

Usage:
    python unified_session.py --project "UMass Waterproofing"
    
This script:
1. Starts click capture (screenshots on mouse click)
2. Monitors AutoCAD command logs in real-time
3. Correlates screenshots with commands
4. Creates unified session file for Claude analysis
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue

# Install dependencies
def install_deps():
    deps = ["Pillow", "pynput", "watchdog"]
    for dep in deps:
        try:
            __import__(dep.lower().replace("-", "_"))
        except ImportError:
            print(f"Installing {dep}...")
            os.system(f"{sys.executable} -m pip install {dep}")

install_deps()

from PIL import Image, ImageGrab, ImageDraw, ImageFont
from pynput import mouse, keyboard

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Note: watchdog not available, log monitoring disabled")

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path.home() / ".cad-observer" / "unified_sessions"
AUTOCAD_LOG_PATH = Path("C:/CADObserver/logs")

# ============================================================
# LOG MONITOR
# ============================================================

class AutoCADLogMonitor(FileSystemEventHandler):
    """Monitor AutoCAD log files for new entries."""
    
    def __init__(self, event_queue: Queue):
        self.event_queue = event_queue
        self.current_file = None
        self.file_position = 0
    
    def on_modified(self, event):
        if event.src_path.endswith(".jsonl"):
            self._read_new_entries(event.src_path)
    
    def on_created(self, event):
        if event.src_path.endswith(".jsonl"):
            self.current_file = event.src_path
            self.file_position = 0
    
    def _read_new_entries(self, filepath):
        try:
            with open(filepath, "r") as f:
                f.seek(self.file_position)
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            self.event_queue.put(("autocad", entry))
                        except json.JSONDecodeError:
                            pass
                self.file_position = f.tell()
        except Exception as e:
            print(f"Log read error: {e}")

# ============================================================
# UNIFIED SESSION
# ============================================================

class UnifiedSession:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = OUTPUT_DIR / f"{self.session_id}_{project_name.replace(' ', '_')}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.events = []
        self.screenshots = []
        self.autocad_commands = []
        self.frame_index = 0
        self.running = True
        self.current_mode = "cad"
        self.last_capture_time = 0
        
        self.event_queue = Queue()
        
        # Session metadata
        self.session_meta = {
            "session_id": self.session_id,
            "project": project_name,
            "started": datetime.now().isoformat(),
            "type": "unified",
            "events": [],
            "screenshots": [],
            "autocad_commands": [],
            "correlations": []
        }
        self._save_meta()
    
    def _save_meta(self):
        with open(self.session_dir / "session.json", "w") as f:
            json.dump(self.session_meta, f, indent=2)
    
    def capture_screenshot(self, x: int, y: int, button: str):
        """Capture screenshot with click coordinates."""
        now = time.time() * 1000
        if now - self.last_capture_time < 300:  # 300ms debounce
            return
        self.last_capture_time = now
        
        timestamp = datetime.now()
        screenshot = ImageGrab.grab()
        
        # Draw crosshair and info
        draw = ImageDraw.Draw(screenshot)
        
        # Crosshair at click location
        draw.line([(x - 25, y), (x + 25, y)], fill=(255, 0, 0), width=2)
        draw.line([(x, y - 25), (x, y + 25)], fill=(255, 0, 0), width=2)
        draw.ellipse([(x-4, y-4), (x+4, y+4)], outline=(255, 0, 0), width=2)
        
        # Info overlay
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)
            except:
                font = ImageFont.load_default()
        
        info_text = f"X:{x} Y:{y} | {self.current_mode.upper()} | #{self.frame_index}"
        draw.rectangle([(5, 5), (250, 30)], fill=(0, 0, 0, 200))
        draw.text((10, 8), info_text, fill=(0, 255, 0), font=font)
        
        # Save
        filename = f"frame_{self.frame_index:04d}.png"
        filepath = self.session_dir / filename
        screenshot.save(filepath, "PNG")
        
        # Event record
        event = {
            "type": "screenshot",
            "index": self.frame_index,
            "timestamp": timestamp.isoformat(),
            "filename": filename,
            "click_x": x,
            "click_y": y,
            "button": button,
            "mode": self.current_mode,
            "pending_autocad_correlation": True
        }
        
        self.screenshots.append(event)
        self.events.append(event)
        self.session_meta["screenshots"].append(event)
        self.session_meta["events"].append(event)
        self._save_meta()
        
        # Console output
        mode_icon = "📚" if self.current_mode == "research" else "🖱️"
        print(f"{mode_icon} [{self.frame_index:04d}] Click ({x}, {y}) - {button}")
        
        self.frame_index += 1
        
        # Try to correlate with recent AutoCAD commands
        self._correlate_screenshot(event)
    
    def add_autocad_event(self, acad_event: dict):
        """Add AutoCAD event to session."""
        event = {
            "type": "autocad",
            "timestamp": acad_event.get("timestamp", datetime.now().isoformat()),
            "event_type": acad_event.get("event_type"),
            "command": acad_event.get("data", {}).get("command") if isinstance(acad_event.get("data"), dict) else None,
            "layer": acad_event.get("current_layer"),
            "raw": acad_event
        }
        
        self.autocad_commands.append(event)
        self.events.append(event)
        self.session_meta["autocad_commands"].append(event)
        self.session_meta["events"].append(event)
        self._save_meta()
        
        if event.get("command"):
            print(f"⌨️  AutoCAD: {event['command']} on layer {event.get('layer', '?')}")
    
    def _correlate_screenshot(self, screenshot_event):
        """Try to correlate screenshot with recent AutoCAD commands."""
        # Look at commands within last 2 seconds
        screenshot_time = datetime.fromisoformat(screenshot_event["timestamp"])
        
        recent_commands = []
        for cmd in reversed(self.autocad_commands[-10:]):
            try:
                cmd_time = datetime.fromisoformat(cmd["timestamp"])
                delta = (screenshot_time - cmd_time).total_seconds()
                if 0 <= delta <= 2:
                    recent_commands.append(cmd)
            except:
                pass
        
        if recent_commands:
            correlation = {
                "screenshot_index": screenshot_event["index"],
                "timestamp": screenshot_event["timestamp"],
                "correlated_commands": [c.get("command") for c in recent_commands if c.get("command")]
            }
            self.session_meta["correlations"].append(correlation)
            self._save_meta()
    
    def set_mode(self, mode: str):
        self.current_mode = mode
        print(f"🔄 Mode: {mode.upper()}")
    
    def process_queue(self):
        """Process events from the queue."""
        while not self.event_queue.empty():
            try:
                event_type, data = self.event_queue.get_nowait()
                if event_type == "autocad":
                    self.add_autocad_event(data)
            except:
                pass
    
    def stop(self):
        self.running = False
        self.session_meta["ended"] = datetime.now().isoformat()
        self.session_meta["total_screenshots"] = self.frame_index
        self.session_meta["total_autocad_events"] = len(self.autocad_commands)
        self._save_meta()
        
        print(f"\n{'='*60}")
        print(f"✓ Session saved: {self.session_dir}")
        print(f"✓ Screenshots: {self.frame_index}")
        print(f"✓ AutoCAD events: {len(self.autocad_commands)}")
        print(f"✓ Correlations: {len(self.session_meta['correlations'])}")
        print(f"{'='*60}")

# ============================================================
# INPUT LISTENERS
# ============================================================

class InputListener:
    def __init__(self, session: UnifiedSession):
        self.session = session
        self.ctrl_pressed = False
        self.shift_pressed = False
    
    def on_click(self, x, y, button, pressed):
        if not self.session.running:
            return False
        if pressed:
            button_name = "left" if button == mouse.Button.left else "right"
            self.session.capture_screenshot(x, y, button_name)
    
    def on_key_press(self, key):
        if not self.session.running:
            return False
        
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift:
                self.shift_pressed = True
            
            if self.ctrl_pressed and self.shift_pressed and hasattr(key, 'char'):
                char = key.char.lower() if key.char else None
                if char == 'r':
                    new_mode = "research" if self.session.current_mode == "cad" else "cad"
                    self.session.set_mode(new_mode)
                elif char == 'q':
                    self.session.stop()
                    return False
        except:
            pass
    
    def on_key_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        elif key == keyboard.Key.shift:
            self.shift_pressed = False

# ============================================================
# MAIN
# ============================================================

def start_unified_session(project_name: str):
    session = UnifiedSession(project_name)
    listener = InputListener(session)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🔗 Unified CAD Session Started                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Project: {project_name:<54} ║
║  Output: {str(session.session_dir):<55}║
╠══════════════════════════════════════════════════════════════════╣
║  CAPTURES:                                                        ║
║    🖱️  Mouse Click     → Screenshot with XY coordinates           ║
║    ⌨️  AutoCAD Logs    → Command tracking (if CAD-OBSERVER-START) ║
║    🔗 Correlation      → Screenshots linked to commands           ║
╠══════════════════════════════════════════════════════════════════╣
║  CONTROLS:                                                        ║
║    Ctrl+Shift+R  → Toggle Research mode                           ║
║    Ctrl+Shift+Q  → Stop session                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  TIP: Run CAD-OBSERVER-START in AutoCAD for command tracking      ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Start mouse/keyboard listeners
    mouse_listener = mouse.Listener(on_click=listener.on_click)
    keyboard_listener = keyboard.Listener(
        on_press=listener.on_key_press,
        on_release=listener.on_key_release
    )
    
    mouse_listener.start()
    keyboard_listener.start()
    
    # Start AutoCAD log monitor if available
    observer = None
    if WATCHDOG_AVAILABLE and AUTOCAD_LOG_PATH.exists():
        log_monitor = AutoCADLogMonitor(session.event_queue)
        observer = Observer()
        observer.schedule(log_monitor, str(AUTOCAD_LOG_PATH), recursive=False)
        observer.start()
        print(f"📁 Monitoring AutoCAD logs: {AUTOCAD_LOG_PATH}")
    else:
        print(f"⚠️  AutoCAD log monitoring not available")
    
    # Main loop
    try:
        while session.running:
            session.process_queue()
            time.sleep(0.1)
    except KeyboardInterrupt:
        session.stop()
    
    # Cleanup
    mouse_listener.stop()
    keyboard_listener.stop()
    if observer:
        observer.stop()
        observer.join()
    
    return session.session_dir

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Unified CAD capture session")
    parser.add_argument("--project", "-p", type=str, default="CAD Session")
    args = parser.parse_args()
    start_unified_session(args.project)
