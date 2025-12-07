# AutoCAD Integration Reference

## Quick Setup (5 minutes)

### 1. Create Directories
```
C:\CADObserver\
├── logs\      (command logs go here)
├── tasks\     (Claude's tasks go here)  
└── done\      (completed tasks)
```

### 2. Install LISP Plugin
Copy `cad-observer.lsp` to your AutoCAD support folder:
- Typical: `C:\Users\[You]\AppData\Roaming\Autodesk\AutoCAD [version]\R[xx]\enu\Support\`
- Or any folder in `OPTIONS > Files > Support File Search Path`

### 3. Auto-Load on Startup
Add this line to `acaddoc.lsp` (in same support folder):
```lisp
(load "cad-observer.lsp")
```

### 4. Start Observing
In AutoCAD command line:
```
CAD-OBSERVER-START
```

---

## What Gets Logged

Each command logs a JSON entry:
```json
{
  "timestamp": "2024-01-15T14:32:15",
  "session_id": "20240115_143200",
  "event_type": "COMMAND_START",
  "drawing": "roof-detail-01.dwg",
  "current_layer": "FLASH-DETAIL",
  "object_count": 847,
  "data": {
    "command": "PLINE",
    "cursor_x": 125.5000,
    "cursor_y": 48.2500
  }
}
```

**Event Types:**
- `SESSION_START` - Logging began
- `SESSION_END` - Logging stopped
- `COMMAND_START` - User initiated command
- `COMMAND_END` - Command completed
- `COMMAND_CANCEL` - User cancelled (ESC)
- `LAYER_CHANGE` - Active layer changed
- `OBJECT_ADDED` - New objects created
- `LISP_START` - LISP function called
- `CLAUDE_TASK` - Claude-sent task executed

---

## Method 1: Command Line Logger (Simplest)

AutoCAD's `.acad.lsp` file can log all commands. Add this to your AutoCAD support path:

```lisp
;; Add to acad.lsp or acaddoc.lsp
(defun log-command (reactor-object command-list)
  (setq cmd-name (car command-list))
  (setq log-file (open "C:/CADLogs/commands.log" "a"))
  (write-line 
    (strcat (rtos (getvar "CDATE") 2 6) "," cmd-name)
    log-file
  )
  (close log-file)
)

(vlr-command-reactor nil '((:vlr-commandWillStart . log-command)))
```

## Method 2: Python + pyautocad

```python
# pip install pyautocad
from pyautocad import Autocad, APoint
import time
import json

acad = Autocad(create_if_not_exists=False)

def monitor_document():
    """Monitor active document for changes."""
    last_count = 0
    log = []
    
    while True:
        try:
            doc = acad.ActiveDocument
            model = doc.ModelSpace
            current_count = model.Count
            
            if current_count != last_count:
                # Something changed
                log.append({
                    "time": time.time(),
                    "objects": current_count,
                    "delta": current_count - last_count,
                    "layers": [l.Name for l in doc.Layers]
                })
                last_count = current_count
                
                # Save periodically
                with open("cad_session.json", "w") as f:
                    json.dump(log, f, indent=2)
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
```

## Method 3: AutoCAD .NET Plugin (Most Complete)

For full command capture, create a .NET plugin:

```csharp
// CADLogger.cs
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.Runtime;
using System.IO;

public class CADLogger : IExtensionApplication
{
    private StreamWriter logWriter;
    
    public void Initialize()
    {
        logWriter = new StreamWriter("C:/CADLogs/session.log", true);
        
        Application.DocumentManager.DocumentCreated += OnDocumentCreated;
        
        foreach (Document doc in Application.DocumentManager)
        {
            HookDocument(doc);
        }
    }
    
    private void HookDocument(Document doc)
    {
        doc.CommandWillStart += (s, e) => 
        {
            logWriter.WriteLine($"{DateTime.Now:O},START,{e.GlobalCommandName}");
            logWriter.Flush();
        };
        
        doc.CommandEnded += (s, e) =>
        {
            logWriter.WriteLine($"{DateTime.Now:O},END,{e.GlobalCommandName}");
            logWriter.Flush();
        };
    }
    
    public void Terminate() => logWriter?.Close();
}
```

## Method 4: Screenshot + Vision Analysis

For style analysis without API integration:

1. Use OBS or ShareX to record CAD session
2. Extract keyframes every 5-10 seconds
3. Send to Claude for visual analysis

```python
# extract_frames.py
import cv2
import os

def extract_frames(video_path, output_dir, interval_seconds=5):
    """Extract frames from CAD recording."""
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval_seconds)
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            output_path = f"{output_dir}/frame_{saved_count:04d}.jpg"
            cv2.imwrite(output_path, frame)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"Extracted {saved_count} frames")
```

## Log Format for Claude Analysis

Structure your command logs like this for optimal Claude analysis:

```json
{
  "session_id": "uuid",
  "started": "ISO-8601",
  "project": "UMass Waterproofing",
  "drawing": "Roof-Detail-01.dwg",
  "commands": [
    {"time": "...", "cmd": "ZOOM", "params": "E"},
    {"time": "...", "cmd": "LAYER", "params": "MAKE", "value": "FLASH-DETAIL"},
    {"time": "...", "cmd": "PLINE", "points": [[0,0], [10,0], [10,5]]}
  ],
  "layer_states": {
    "before": ["0", "DIMS"],
    "after": ["0", "DIMS", "FLASH-DETAIL"]
  }
}
```

---

## Claude -> AutoCAD Task System

Claude can send tasks to AutoCAD via JSON files.

### Task Types

**1. Script Task (AutoCAD Commands)**
```json
{
  "task_type": "script",
  "commands": ["ZOOM", "E", "LINE", "0,0", "10,10", ""]
}
```

**2. LISP Task (Execute LISP Code)**
```json
{
  "task_type": "lisp", 
  "code": "(command \"CIRCLE\" \"0,0\" 5)"
}
```

**3. Query Task (Get Drawing Info)**
```json
{
  "task_type": "query",
  "query_type": "full"
}
```

### Python Helper Functions

```python
from cad_task import *

# Draw geometry
draw_line(0, 0, 10, 10, layer="DETAIL")
draw_rectangle(0, 0, 4, 2, layer="REGLET")

# Manage layers
create_layer("FLASH-DETAIL", color=5)
set_current_layer("FLASH-DETAIL")

# View control
zoom_extents()

# Read logs
entries = read_latest_session(limit=50)
analysis = analyze_commands(entries)

# Query current state
send_query_task()
result = read_query_results()
```

### Common AutoCAD Command Sequences

**Create Detail Layer + Draw:**
```python
send_script_task([
    "-LAYER", "M", "DETAIL-01", "C", "5", "DETAIL-01", "",
    "PLINE", "0,0", "4,0", "4,2", "0,2", "C"
])
```

**Offset + Trim Workflow:**
```python
send_script_task([
    "OFFSET", "0.5", "L", "",  # Offset last object 0.5"
    "TRIM", "", "L", ""        # Trim with last object
])
```

**Dimension Placement:**
```python
send_script_task([
    "-LAYER", "S", "DIMS", "",
    "DIMLINEAR", "0,0", "4,0", "0,-0.5"
])
```
