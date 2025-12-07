#!/usr/bin/env python3
"""
Research Capture Tool
Capture what you're reading/researching with annotations.

Usage:
    python research_capture.py --project "UMass Waterproofing"
    
Hotkeys:
    Ctrl+Shift+C  - Capture current screen as research
    Ctrl+Shift+H  - Capture with highlight (draws attention box)
    Ctrl+Shift+T  - Add text annotation to last capture
    Ctrl+Shift+Q  - Quit

Use this while reading specs, details, literature, manufacturer docs, etc.
Claude will understand this is reference material influencing your CAD decisions.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Install dependencies
def install_deps():
    deps = ["Pillow", "pynput"]
    for dep in deps:
        try:
            __import__(dep.lower())
        except ImportError:
            print(f"Installing {dep}...")
            os.system(f"{sys.executable} -m pip install {dep}")

install_deps()

from PIL import Image, ImageGrab, ImageDraw, ImageFont
from pynput import keyboard

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path.home() / ".cad-observer" / "research"

# ============================================================
# RESEARCH SESSION
# ============================================================

class ResearchSession:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = OUTPUT_DIR / f"{self.session_id}_{project_name.replace(' ', '_')}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.captures = []
        self.capture_index = 0
        self.running = True
        self.highlight_mode = False
        self.highlight_start = None
        
        self.session_meta = {
            "session_id": self.session_id,
            "project": project_name,
            "type": "research",
            "started": datetime.now().isoformat(),
            "captures": [],
            "topics": [],
            "sources": []
        }
        self._save_meta()
    
    def _save_meta(self):
        with open(self.session_dir / "session.json", "w") as f:
            json.dump(self.session_meta, f, indent=2)
    
    def capture(self, highlight_region=None, annotation=None):
        """Capture research screenshot."""
        timestamp = datetime.now()
        screenshot = ImageGrab.grab()
        
        # Add visual markers
        draw = ImageDraw.Draw(screenshot)
        
        # Research mode banner
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 20)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Banner at top
        banner_height = 40
        draw.rectangle([(0, 0), (screenshot.width, banner_height)], fill=(0, 100, 150))
        draw.text((10, 10), f"📚 RESEARCH CAPTURE #{self.capture_index}", fill=(255, 255, 255), font=font)
        draw.text((screenshot.width - 200, 12), timestamp.strftime("%H:%M:%S"), fill=(200, 200, 200), font=small_font)
        
        # Highlight region if specified
        if highlight_region:
            x1, y1, x2, y2 = highlight_region
            draw.rectangle([(x1, y1), (x2, y2)], outline=(255, 255, 0), width=3)
        
        # Save
        filename = f"research_{self.capture_index:04d}.png"
        filepath = self.session_dir / filename
        screenshot.save(filepath, "PNG")
        
        # Metadata
        capture_meta = {
            "index": self.capture_index,
            "timestamp": timestamp.isoformat(),
            "filename": filename,
            "highlight_region": highlight_region,
            "annotation": annotation,
            "source_type": None,  # To be filled by user: "spec", "detail", "manufacturer", "code", etc.
            "relevance_note": None,
            "questions": []
        }
        
        self.captures.append(capture_meta)
        self.session_meta["captures"] = self.captures
        self._save_meta()
        
        print(f"📚 [{self.capture_index:04d}] Research captured")
        self.capture_index += 1
        
        return capture_meta
    
    def add_annotation(self, text: str):
        """Add annotation to last capture."""
        if self.captures:
            self.captures[-1]["annotation"] = text
            self._save_meta()
            print(f"📝 Annotation added: {text[:50]}...")
    
    def add_source_type(self, source_type: str):
        """Tag the source type of last capture."""
        if self.captures:
            self.captures[-1]["source_type"] = source_type
            if source_type not in self.session_meta["sources"]:
                self.session_meta["sources"].append(source_type)
            self._save_meta()
            print(f"🏷️ Tagged as: {source_type}")
    
    def stop(self):
        self.running = False
        self.session_meta["ended"] = datetime.now().isoformat()
        self.session_meta["total_captures"] = self.capture_index
        self._save_meta()
        
        print(f"\n{'='*60}")
        print(f"✓ Research session saved: {self.session_dir}")
        print(f"✓ Total captures: {self.capture_index}")
        print(f"{'='*60}")

# ============================================================
# KEYBOARD LISTENER
# ============================================================

class ResearchListener:
    def __init__(self, session: ResearchSession):
        self.session = session
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.awaiting_input = None
    
    def on_press(self, key):
        if not self.session.running:
            return False
        
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift:
                self.shift_pressed = True
            
            if self.ctrl_pressed and self.shift_pressed:
                if hasattr(key, 'char'):
                    char = key.char.lower() if key.char else None
                    
                    if char == 'c':
                        # Simple capture
                        self.session.capture()
                    
                    elif char == 's':
                        # Capture and prompt for source type
                        self.session.capture()
                        print("\n📂 Enter source type (spec/detail/manufacturer/code/other):")
                        self.awaiting_input = "source"
                    
                    elif char == 't':
                        # Add text annotation
                        print("\n📝 Enter annotation for last capture:")
                        self.awaiting_input = "annotation"
                    
                    elif char == 'q':
                        self.session.stop()
                        return False
                        
        except AttributeError:
            pass
    
    def on_release(self, key):
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.ctrl_pressed = False
        elif key == keyboard.Key.shift:
            self.shift_pressed = False

# ============================================================
# MAIN
# ============================================================

def start_research_capture(project_name: str):
    session = ResearchSession(project_name)
    listener = ResearchListener(session)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  📚 Research Capture Started                                      ║
╠══════════════════════════════════════════════════════════════════╣
║  Project: {project_name:<54} ║
║  Output: {str(session.session_dir):<55}║
╠══════════════════════════════════════════════════════════════════╣
║  CONTROLS:                                                        ║
║    Ctrl+Shift+C  → Capture current screen                         ║
║    Ctrl+Shift+S  → Capture + tag source type                      ║
║    Ctrl+Shift+T  → Add annotation to last capture                 ║
║    Ctrl+Shift+Q  → Stop session                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Use while reading: specs, details, manufacturer docs, codes      ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    kb_listener = keyboard.Listener(
        on_press=listener.on_press,
        on_release=listener.on_release
    )
    kb_listener.start()
    
    try:
        while session.running:
            # Handle console input for annotations
            if listener.awaiting_input == "annotation":
                try:
                    text = input()
                    session.add_annotation(text)
                except:
                    pass
                listener.awaiting_input = None
            elif listener.awaiting_input == "source":
                try:
                    text = input()
                    session.add_source_type(text)
                except:
                    pass
                listener.awaiting_input = None
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        session.stop()
    
    kb_listener.stop()
    return session.session_dir

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Research/literature capture")
    parser.add_argument("--project", "-p", type=str, default="Research Session")
    args = parser.parse_args()
    start_research_capture(args.project)
