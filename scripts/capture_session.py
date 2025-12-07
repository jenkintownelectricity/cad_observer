#!/usr/bin/env python3
"""
CAD Session Capture - Quick Start Script
Takes periodic screenshots during CAD work for Claude analysis.

Usage:
    python capture_session.py --interval 30 --project "UMass Waterproofing"
    
Then share the screenshots with Claude and say "analyze my CAD session"
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# Try to import screenshot library
try:
    from PIL import ImageGrab
except ImportError:
    print("Installing Pillow...")
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import ImageGrab

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path.home() / ".cad-observer" / "sessions"

# ============================================================
# CAPTURE FUNCTIONS
# ============================================================

def capture_screenshot(session_dir: Path, index: int) -> dict:
    """Capture a screenshot and save metadata."""
    timestamp = datetime.now()
    filename = f"frame_{index:04d}.png"
    filepath = session_dir / filename
    
    # Capture screen
    screenshot = ImageGrab.grab()
    screenshot.save(filepath, "PNG")
    
    return {
        "index": index,
        "timestamp": timestamp.isoformat(),
        "filename": filename,
        "resolution": screenshot.size
    }

def start_capture_session(project_name: str, interval: int, duration: int = None):
    """Start a capture session."""
    
    # Create session directory
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = OUTPUT_DIR / f"{session_id}_{project_name.replace(' ', '_')}"
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║  CAD Session Capture Started                                  ║")
    print(f"╠══════════════════════════════════════════════════════════════╣")
    print(f"║  Project: {project_name:<50} ║")
    print(f"║  Interval: {interval} seconds{' ':<44}║")
    print(f"║  Output: {str(session_dir):<52}║")
    print(f"╠══════════════════════════════════════════════════════════════╣")
    print(f"║  Press Ctrl+C to stop capture                                 ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Session metadata
    session_meta = {
        "session_id": session_id,
        "project": project_name,
        "started": datetime.now().isoformat(),
        "interval_seconds": interval,
        "frames": []
    }
    
    frame_index = 0
    start_time = time.time()
    
    try:
        while True:
            # Check duration limit
            if duration and (time.time() - start_time) >= duration:
                print(f"\nDuration limit ({duration}s) reached.")
                break
            
            # Capture
            frame_meta = capture_screenshot(session_dir, frame_index)
            session_meta["frames"].append(frame_meta)
            
            print(f"[{frame_index:04d}] Captured at {frame_meta['timestamp']}")
            
            # Save metadata after each capture
            with open(session_dir / "session.json", "w") as f:
                json.dump(session_meta, f, indent=2)
            
            frame_index += 1
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nCapture stopped by user.")
    
    # Finalize session
    session_meta["ended"] = datetime.now().isoformat()
    session_meta["total_frames"] = frame_index
    
    with open(session_dir / "session.json", "w") as f:
        json.dump(session_meta, f, indent=2)
    
    print(f"\n✓ Session saved: {session_dir}")
    print(f"✓ Total frames: {frame_index}")
    print(f"\nNext steps:")
    print(f"  1. Open Claude")
    print(f"  2. Upload some frames from: {session_dir}")
    print(f"  3. Say: 'Analyze my CAD session and log observations'")
    
    return session_dir

def list_sessions():
    """List all captured sessions."""
    if not OUTPUT_DIR.exists():
        print("No sessions found.")
        return
    
    sessions = sorted(OUTPUT_DIR.iterdir())
    
    if not sessions:
        print("No sessions found.")
        return
    
    print(f"\nCaptured Sessions ({OUTPUT_DIR}):\n")
    
    for session_dir in sessions:
        if session_dir.is_dir():
            meta_file = session_dir / "session.json"
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                print(f"  {session_dir.name}")
                print(f"    Project: {meta.get('project', 'Unknown')}")
                print(f"    Frames: {meta.get('total_frames', len(meta.get('frames', [])))}")
                print(f"    Started: {meta.get('started', 'Unknown')}")
                print()

# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Capture CAD session screenshots for Claude analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python capture_session.py --project "Roof Details" --interval 30
  python capture_session.py --project "Shop Drawing" --interval 10 --duration 3600
  python capture_session.py --list
        """
    )
    
    parser.add_argument("--project", "-p", type=str, default="CAD Session",
                        help="Project name for this session")
    parser.add_argument("--interval", "-i", type=int, default=30,
                        help="Seconds between captures (default: 30)")
    parser.add_argument("--duration", "-d", type=int, default=None,
                        help="Maximum duration in seconds (default: unlimited)")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List all captured sessions")
    
    args = parser.parse_args()
    
    if args.list:
        list_sessions()
    else:
        start_capture_session(args.project, args.interval, args.duration)

if __name__ == "__main__":
    main()
