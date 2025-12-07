#!/usr/bin/env python3
"""
CAD Task Sender - Send commands from Claude to AutoCAD
Creates task files that the AutoCAD LISP plugin executes.

Usage:
    # Send AutoCAD commands
    python cad_task.py script "ZOOM E" "LAYER M FLASH-DETAIL" "PLINE"
    
    # Send LISP code
    python cad_task.py lisp "(command \"CIRCLE\" \"0,0\" 5)"
    
    # Query drawing info
    python cad_task.py query
    
    # Read command logs
    python cad_task.py read-logs --last 50
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ============================================================
# CONFIGURATION - Must match LISP plugin paths
# ============================================================

CAD_OBSERVER_ROOT = Path("C:/CADObserver")
TASK_PATH = CAD_OBSERVER_ROOT / "tasks"
LOG_PATH = CAD_OBSERVER_ROOT / "logs"
DONE_PATH = CAD_OBSERVER_ROOT / "done"

# ============================================================
# TASK CREATION
# ============================================================

def ensure_dirs():
    """Create required directories."""
    TASK_PATH.mkdir(parents=True, exist_ok=True)
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    DONE_PATH.mkdir(parents=True, exist_ok=True)

def create_task_id() -> str:
    """Generate unique task ID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def send_script_task(commands: List[str], description: str = "") -> dict:
    """
    Send AutoCAD script commands to execute.
    
    Args:
        commands: List of AutoCAD commands (e.g., ["ZOOM E", "LINE", "0,0", "10,10", ""])
        description: Optional description of what this task does
    
    Returns:
        Task metadata
    """
    ensure_dirs()
    
    task_id = create_task_id()
    task = {
        "task_id": task_id,
        "task_type": "script",
        "created": datetime.now().isoformat(),
        "description": description,
        "commands": commands
    }
    
    task_file = TASK_PATH / f"task_{task_id}.json"
    with open(task_file, "w") as f:
        json.dump(task, f, indent=2)
    
    print(f"✓ Task created: {task_file}")
    print(f"  Commands: {len(commands)}")
    print(f"  Waiting for AutoCAD to execute...")
    
    return {"task_id": task_id, "file": str(task_file), "commands": commands}

def send_lisp_task(code: str, description: str = "") -> dict:
    """
    Send LISP code to execute in AutoCAD.
    
    Args:
        code: LISP code to execute
        description: Optional description
    
    Returns:
        Task metadata
    """
    ensure_dirs()
    
    task_id = create_task_id()
    task = {
        "task_id": task_id,
        "task_type": "lisp",
        "created": datetime.now().isoformat(),
        "description": description,
        "code": code
    }
    
    task_file = TASK_PATH / f"task_{task_id}.json"
    with open(task_file, "w") as f:
        json.dump(task, f, indent=2)
    
    print(f"✓ LISP task created: {task_file}")
    
    return {"task_id": task_id, "file": str(task_file)}

def send_query_task(query_type: str = "full") -> dict:
    """
    Request drawing information from AutoCAD.
    
    Args:
        query_type: Type of query ("full", "layers", "objects")
    
    Returns:
        Task metadata
    """
    ensure_dirs()
    
    task_id = create_task_id()
    task = {
        "task_id": task_id,
        "task_type": "query",
        "created": datetime.now().isoformat(),
        "query_type": query_type
    }
    
    task_file = TASK_PATH / f"task_{task_id}.json"
    with open(task_file, "w") as f:
        json.dump(task, f, indent=2)
    
    print(f"✓ Query task created: {task_file}")
    print(f"  Check {LOG_PATH} for results after AutoCAD processes")
    
    return {"task_id": task_id, "file": str(task_file)}

# ============================================================
# LOG READING
# ============================================================

def read_latest_session(limit: int = 100) -> List[dict]:
    """Read entries from the latest session log."""
    ensure_dirs()
    
    # Find latest log file
    log_files = sorted(LOG_PATH.glob("session_*.jsonl"), reverse=True)
    
    if not log_files:
        print("No session logs found.")
        return []
    
    latest_log = log_files[0]
    print(f"Reading: {latest_log}")
    
    entries = []
    with open(latest_log, "r") as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    return entries[-limit:]

def read_all_sessions(limit_per_session: int = 50) -> dict:
    """Read from all session logs."""
    ensure_dirs()
    
    log_files = sorted(LOG_PATH.glob("session_*.jsonl"), reverse=True)
    
    sessions = {}
    for log_file in log_files[:10]:  # Last 10 sessions max
        session_id = log_file.stem.replace("session_", "")
        entries = []
        with open(log_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
        sessions[session_id] = entries[-limit_per_session:]
    
    return sessions

def analyze_commands(entries: List[dict]) -> dict:
    """Analyze command patterns from log entries."""
    commands = {}
    layers_used = set()
    command_sequences = []
    last_cmd = None
    
    for entry in entries:
        if entry.get("event_type") == "COMMAND_START":
            cmd = entry.get("data", {})
            if isinstance(cmd, str):
                try:
                    cmd = json.loads(cmd)
                except:
                    cmd = {}
            
            cmd_name = cmd.get("command", "UNKNOWN")
            commands[cmd_name] = commands.get(cmd_name, 0) + 1
            
            if last_cmd:
                command_sequences.append((last_cmd, cmd_name))
            last_cmd = cmd_name
        
        if "current_layer" in entry:
            layers_used.add(entry["current_layer"])
    
    # Find common sequences
    seq_counts = {}
    for seq in command_sequences:
        seq_counts[seq] = seq_counts.get(seq, 0) + 1
    
    top_sequences = sorted(seq_counts.items(), key=lambda x: -x[1])[:10]
    
    return {
        "total_commands": sum(commands.values()),
        "unique_commands": len(commands),
        "top_commands": sorted(commands.items(), key=lambda x: -x[1])[:15],
        "layers_used": list(layers_used),
        "common_sequences": top_sequences
    }

def read_query_results() -> Optional[dict]:
    """Read the latest query result."""
    ensure_dirs()
    
    result_files = sorted(LOG_PATH.glob("query_result_*.json"), reverse=True)
    
    if not result_files:
        return None
    
    with open(result_files[0], "r") as f:
        return json.load(f)

# ============================================================
# HELPER FUNCTIONS FOR CLAUDE
# ============================================================

def draw_line(x1: float, y1: float, x2: float, y2: float, layer: str = None):
    """Helper to draw a line."""
    commands = []
    if layer:
        commands.append(f"LAYER M {layer} ")
    commands.extend([
        "LINE",
        f"{x1},{y1}",
        f"{x2},{y2}",
        ""  # Enter to finish
    ])
    return send_script_task(commands, f"Draw line from ({x1},{y1}) to ({x2},{y2})")

def draw_rectangle(x1: float, y1: float, x2: float, y2: float, layer: str = None):
    """Helper to draw a rectangle."""
    commands = []
    if layer:
        commands.append(f"LAYER M {layer} ")
    commands.extend([
        "RECTANG",
        f"{x1},{y1}",
        f"{x2},{y2}"
    ])
    return send_script_task(commands, f"Draw rectangle from ({x1},{y1}) to ({x2},{y2})")

def create_layer(name: str, color: int = 7):
    """Helper to create a layer."""
    commands = [
        f"-LAYER",
        "M",
        name,
        "C",
        str(color),
        name,
        ""
    ]
    return send_script_task(commands, f"Create layer {name} with color {color}")

def zoom_extents():
    """Helper to zoom to extents."""
    return send_script_task(["ZOOM", "E"], "Zoom to extents")

def set_current_layer(name: str):
    """Helper to set current layer."""
    return send_script_task([f"-LAYER", "S", name, ""], f"Set current layer to {name}")

# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Send tasks to AutoCAD from Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send AutoCAD commands
  python cad_task.py script "ZOOM E"
  python cad_task.py script "LINE" "0,0" "10,10" ""
  
  # Send LISP code  
  python cad_task.py lisp "(command \\"CIRCLE\\" \\"0,0\\" 5)"
  
  # Query drawing state
  python cad_task.py query
  
  # Read command logs
  python cad_task.py read-logs
  python cad_task.py read-logs --analyze
  
  # Read query results
  python cad_task.py read-query
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Script command
    script_parser = subparsers.add_parser("script", help="Send AutoCAD commands")
    script_parser.add_argument("commands", nargs="+", help="Commands to execute")
    script_parser.add_argument("--desc", "-d", default="", help="Description")
    
    # LISP command
    lisp_parser = subparsers.add_parser("lisp", help="Send LISP code")
    lisp_parser.add_argument("code", help="LISP code to execute")
    lisp_parser.add_argument("--desc", "-d", default="", help="Description")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query drawing info")
    query_parser.add_argument("--type", "-t", default="full", help="Query type")
    
    # Read logs command
    read_parser = subparsers.add_parser("read-logs", help="Read command logs")
    read_parser.add_argument("--last", "-n", type=int, default=50, help="Number of entries")
    read_parser.add_argument("--analyze", "-a", action="store_true", help="Analyze patterns")
    read_parser.add_argument("--all", action="store_true", help="Read all sessions")
    
    # Read query results
    query_result_parser = subparsers.add_parser("read-query", help="Read query results")
    
    args = parser.parse_args()
    
    if args.command == "script":
        result = send_script_task(args.commands, args.desc)
        print(json.dumps(result, indent=2))
    
    elif args.command == "lisp":
        result = send_lisp_task(args.code, args.desc)
        print(json.dumps(result, indent=2))
    
    elif args.command == "query":
        result = send_query_task(args.type)
        print(json.dumps(result, indent=2))
    
    elif args.command == "read-logs":
        if args.all:
            sessions = read_all_sessions(args.last)
            print(json.dumps(sessions, indent=2))
        else:
            entries = read_latest_session(args.last)
            if args.analyze:
                analysis = analyze_commands(entries)
                print(json.dumps(analysis, indent=2))
            else:
                print(json.dumps(entries, indent=2))
    
    elif args.command == "read-query":
        result = read_query_results()
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No query results found.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
