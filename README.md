# CAD Observer

AI-powered CAD workflow observation and learning system for AutoCAD. Works with Claude Code to learn your drafting patterns and assist with roofing/waterproofing shop drawings.

## Quick Start

### 1. Install Dependencies
```bash
pip install pillow pynput keyboard pyperclip
```

### 2. Run Setup (Windows)
```bash
cd scripts
setup_windows.bat
```

### 3. Load LISP in AutoCAD
1. Open AutoCAD
2. Type `APPLOAD`
3. Browse to `scripts/cad-observer.lsp` → Load
4. Type `CAD-OBSERVER-START`

### 4. Start Capture
```bash
python scripts/click_capture.py -p "Your Project Name"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `click_capture.py` | Capture screenshots on every click with XY coordinates |
| `floating_toolbar.py` | All-in-one control panel |
| `research_capture.py` | Capture specs/literature you're reading |
| `cad_task.py` | Send commands from Claude to AutoCAD |
| `cad-observer.lsp` | AutoCAD plugin for command logging |

## Controls

### Click Capture
- **Mouse Click** → Capture screenshot with XY coordinates
- **Ctrl+Shift+R** → Toggle Research mode
- **Ctrl+Shift+Q** → Stop

### AutoCAD Commands
```
CAD-OBSERVER-START   - Start logging
CAD-OBSERVER-STOP    - Stop logging
CAD-OBSERVER-STATUS  - Show status
CAD-OBSERVER-TASK    - Check for Claude tasks
CAD-OBSERVER-AUTO    - Toggle auto-task execution
```

## Storage Locations

- Sessions: `~/.cad-observer/sessions/`
- Research: `~/.cad-observer/research/`
- Observations: `~/.cad-observer/observations.jsonl`
- AutoCAD logs: `C:/CADObserver/logs/`

## Using with Claude Code

This project includes `CLAUDE.md` which gives Claude Code context about:
- Your drafting background and preferences
- Question-first observation protocol
- How to log observations properly
- How to send tasks to AutoCAD

Just run `claude` in this directory and start sharing screenshots.

## License

MIT
