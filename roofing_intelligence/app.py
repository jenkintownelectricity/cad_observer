"""
Roofing Intelligence Platform
A modern, unified tool for roofing document analysis and shop drawing generation.
Built for Division 07 professionals.

Features:
- Smart PDF filtering (cost optimization)
- Multi-layered element detection with confidence scoring
- Assembly letter parsing with DXF generation
- Real-time processing feedback via SSE
- Project management and export
"""

from flask import Flask, render_template, request, jsonify, Response, send_file, redirect
import os
import json
import time
import queue
import threading
from datetime import datetime
import PyPDF2

# Import API client for backend connection
api_client = None
API_AVAILABLE = False

def check_api_connection():
    """Check API connection and set agency ID"""
    global API_AVAILABLE, api_client
    try:
        import api_client as ac
        api_client = ac
        API_AVAILABLE = api_client.is_api_available()
        if API_AVAILABLE:
            # Set agency ID (use env var or default)
            agency_id = os.getenv('ROOFIO_AGENCY_ID', '3cfd5441-d5fc-4857-8fb9-3dc7be7a37d5')
            api_client.set_agency_id(agency_id)
            print(f"✓ Connected to ROOFIO Backend API (Agency: {agency_id})")
        else:
            print("⚠ Backend API not available, using local storage")
    except ImportError as e:
        print(f"⚠ API client import error: {e}")
    except Exception as e:
        print(f"⚠ API connection error: {e}")

# Try to connect on startup (will retry on each request if needed)
check_api_connection()

# Import parsers
from parsers.roof_page_filter import filter_roof_pages, get_roof_page_numbers
from parsers.arch_drawing_parser import parse_architectural_drawing
from parsers.assembly_parser import parse_assembly_letter
from parsers.text_cleaner import clean_rtf_text, deduplicate_list
from generators.dxf_generator import generate_assembly_dxf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'roofing-intelligence-2025'

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
PROJECTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'projects')

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, PROJECTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['PROJECTS_FOLDER'] = PROJECTS_FOLDER

# Progress tracking for SSE
progress_queues = {}


def get_progress_queue(session_id):
    """Get or create a progress queue for a session."""
    if session_id not in progress_queues:
        progress_queues[session_id] = queue.Queue()
    return progress_queues[session_id]


def send_progress(session_id, step, progress, message, data=None):
    """Send progress update to the client."""
    q = get_progress_queue(session_id)
    update = {
        'step': step,
        'progress': progress,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    q.put(update)


# =============================================================================
# ROUTES - Pages
# =============================================================================

@app.route('/')
def home():
    """Landing page - marketing/pricing page."""
    return render_template('landing.html')


@app.route('/landing')
def landing():
    """Alias for landing page."""
    return render_template('landing.html')


@app.route('/dashboard')
def dashboard():
    """Company dashboard with role-based seats."""
    return render_template('dashboard.html')


@app.route('/analysis')
def analysis():
    """Document analysis page."""
    return render_template('index.html')


@app.route('/phone')
def phone():
    """Phone integration page (Hive 215)."""
    return render_template('phone.html')


@app.route('/roofio')
def roofio():
    """Roofio - Division 07 AI Expert."""
    return render_template('roofio.html')


@app.route('/digital-foreman')
def digital_foreman():
    """Digital Foreman - Risk Shield field documentation."""
    return render_template('digital_foreman.html')


@app.route('/inspector/<visit_id>')
def inspector_access(visit_id):
    """Guest inspector access for hold point inspections (no account required)."""
    return render_template('inspector.html')


@app.route('/control-center')
def control_center():
    """ROOFIO Control Center - All 8 positions with Full AI/Assist/Off toggles."""
    return render_template('control_center.html')


@app.route('/data-central')
def data_central():
    """Data Central - Project documents hub with AI extraction and version diff."""
    return render_template('data_central.html')


@app.route('/integrations')
def integrations():
    """Integrations Hub - Connect email, storage, accounting, and construction platforms."""
    return render_template('integrations.html')


@app.route('/projects')
def projects():
    """Project management page."""
    all_projects = []

    # 1. Try to fetch from API (Supabase-backed projects)
    if API_AVAILABLE and api_client:
        try:
            result = api_client.list_projects()
            for p in result.get('projects', []):
                all_projects.append({
                    'id': p['project_id'],
                    'filename': p['project_id'],  # Use ID as filename for compatibility
                    'name': p['name'],
                    'client': p.get('gc_contact', {}).get('name', '') if p.get('gc_contact') else '',
                    'value': f"${p.get('contract_amount', 0):,.0f}" if p.get('contract_amount') else '',
                    'status': p.get('status', 'bidding'),
                    'created': p.get('created_at', ''),
                    'documents': 0,
                    'source': 'api'
                })
        except Exception as e:
            print(f"Error fetching API projects: {e}")

    # 2. Also load local JSON files (analysis projects)
    for f in os.listdir(app.config['PROJECTS_FOLDER']):
        if f.endswith('.json'):
            filepath = os.path.join(app.config['PROJECTS_FOLDER'], f)
            try:
                with open(filepath, 'r') as pf:
                    project_data = json.load(pf)
                    all_projects.append({
                        'id': f,
                        'filename': f,
                        'name': project_data.get('name', f.replace('.json', '')),
                        'created': project_data.get('created', 'Unknown'),
                        'documents': len(project_data.get('documents', [])),
                        'source': 'local'
                    })
            except Exception as e:
                print(f"Error loading project {f}: {e}")

    return render_template('projects.html', projects=all_projects)


# =============================================================================
# ROUTES - API Endpoints
# =============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_documents():
    """
    Main analysis endpoint - processes all uploaded documents.
    Returns session_id for SSE progress tracking.
    """
    session_id = f"session_{int(time.time() * 1000)}"

    # Collect and SAVE files immediately (before thread starts)
    saved_files = {
        'drawings': [],
        'assemblies': [],
        'specs': [],
        'scopes': []
    }

    for file_type in saved_files.keys():
        files = request.files.getlist(file_type)
        for file in files:
            if file and file.filename:
                # Save file to disk immediately
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                saved_files[file_type].append({
                    'filename': file.filename,
                    'filepath': filepath
                })

    # Filter out empty file lists
    saved_files = {k: v for k, v in saved_files.items() if v}

    if not saved_files:
        return jsonify({'error': 'No files uploaded'}), 400

    # Start background processing with saved file paths (not file objects)
    thread = threading.Thread(
        target=process_documents_async,
        args=(session_id, saved_files, app.config['UPLOAD_FOLDER'])
    )
    thread.start()

    return jsonify({'session_id': session_id})


@app.route('/api/progress/<session_id>')
def progress_stream(session_id):
    """SSE endpoint for real-time progress updates."""
    def generate():
        q = get_progress_queue(session_id)

        while True:
            try:
                update = q.get(timeout=30)
                yield f"data: {json.dumps(update)}\n\n"

                # Check if processing is complete
                if update.get('step') == 'complete' or update.get('step') == 'error':
                    break
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'keepalive': True})}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/filter-preview', methods=['POST'])
def filter_preview():
    """Preview which pages would be filtered from a PDF."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    # Save temporarily
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Run filter
    result = filter_roof_pages(filepath, threshold=10, verbose=False)

    return jsonify({
        'filename': file.filename,
        'total_pages': result['total_pages'],
        'roof_pages_count': result['pages_to_process'],
        'savings_percent': result['savings_percent'],
        'roof_pages': [
            {
                'page': p['page_num'],
                'score': p['score'],
                'sheet': p['sheet_number'],
                'title': p['sheet_title'],
                'keywords': p['matches']['high'][:5] if p['matches'].get('high') else []
            }
            for p in result['roof_pages']
        ]
    })


@app.route('/api/generate-dxf', methods=['POST'])
def generate_dxf():
    """Generate DXF from assembly data."""
    data = request.json
    if not data:
        return jsonify({'error': 'No assembly data provided'}), 400

    try:
        output_files = generate_assembly_dxf(data, app.config['OUTPUT_FOLDER'])

        # Return first file for download
        if output_files:
            filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_files[0])
            if os.path.exists(filepath):
                return send_file(filepath, as_attachment=True)

        return jsonify({'files': output_files})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/save', methods=['POST'])
def save_project():
    """Save current analysis as a project."""
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name required'}), 400

    project_name = data['name'].replace(' ', '_').lower()
    filename = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(app.config['PROJECTS_FOLDER'], filename)

    project_data = {
        'name': data['name'],
        'created': datetime.now().isoformat(),
        'documents': data.get('documents', []),
        'results': data.get('results', {}),
        'notes': data.get('notes', '')
    }

    with open(filepath, 'w') as f:
        json.dump(project_data, f, indent=2)

    return jsonify({'success': True, 'filename': filename})


@app.route('/api/project/load/<filename>')
def load_project(filename):
    """Load a saved project."""
    filepath = os.path.join(app.config['PROJECTS_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Project not found'}), 404

    with open(filepath, 'r') as f:
        project_data = json.load(f)

    return jsonify(project_data)


@app.route('/api/project/delete/<filename>', methods=['DELETE'])
def delete_project(filename):
    """Delete a saved project."""
    filepath = os.path.join(app.config['PROJECTS_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Project not found'}), 404

    try:
        os.remove(filepath)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export analysis results as CSV."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Build CSV
    csv_lines = ['File,Sheet,Type,Drains,Scuppers,RTUs,Penetrations,Scale,Status']

    drawings = data.get('drawings', [])
    if not isinstance(drawings, list):
        drawings = [drawings]

    for drawing in drawings:
        if drawing.get('roof_plans'):
            for plan in drawing['roof_plans']:
                line = [
                    drawing.get('filename', ''),
                    plan.get('detail_number', ''),
                    plan.get('type', ''),
                    str(extract_count(plan.get('drains', ''))),
                    str(extract_count(plan.get('scuppers', ''))),
                    str(extract_count(plan.get('rtus_curbs', ''))),
                    str(extract_count(plan.get('penetrations', ''))),
                    plan.get('scale', ''),
                    plan.get('workflow_state', 'detected')
                ]
                csv_lines.append(','.join(f'"{v}"' for v in line))

    csv_content = '\n'.join(csv_lines)

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=roofing_analysis.csv'}
    )


# =============================================================================
# ROUTES - Company Dashboard API
# =============================================================================

# In-memory storage for company data (would be database in production)
COMPANY_DATA = {
    'projects': [],
    'activities': [],
    'seats': {
        'pm': {'user': 'Active', 'status': 'online'},
        'estimator': {'user': 'Active', 'status': 'online'},
        'operations': {'user': 'Active', 'status': 'online'},
        'accounting': {'user': 'Active', 'status': 'online'},
        'field': {'user': '3 Crews', 'status': 'online'},
        'shop-drawings': {'user': 'CAD Queue', 'status': 'online'}
    }
}


@app.route('/api/company/projects', methods=['GET'])
def get_company_projects():
    """Get all company projects."""
    if API_AVAILABLE and api_client:
        try:
            result = api_client.list_projects()
            # Transform API response to match frontend expectations
            projects = []
            for p in result.get('projects', []):
                projects.append({
                    'id': p['project_id'],
                    'name': p['name'],
                    'client': p.get('gc_contact', {}).get('name', '') if p.get('gc_contact') else '',
                    'value': f"${p.get('contract_amount', 0):,.0f}" if p.get('contract_amount') else '',
                    'status': 'green' if p.get('status') in ['complete', 'awarded'] else 'yellow' if p.get('status') == 'bidding' else 'red',
                    'progress': 100 if p.get('status') == 'complete' else 50 if p.get('status') == 'in_progress' else 0,
                    'phase': p.get('status', 'Bidding').replace('_', ' ').title(),
                    'assignee': 'Team',
                    'created': p.get('created_at', '')
                })
            return jsonify({'projects': projects})
        except Exception as e:
            print(f"API error: {e}, falling back to local")
    return jsonify({'projects': COMPANY_DATA['projects']})


@app.route('/api/company/projects', methods=['POST'])
def create_company_project():
    """Create a new company project."""
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name required'}), 400

    if API_AVAILABLE and api_client:
        try:
            # Build address from data
            address = {
                'street': data.get('address', ''),
                'city': data.get('city', ''),
                'state': data.get('state', ''),
                'zip': data.get('zip', '')
            }
            result = api_client.create_project(
                name=data['name'],
                address=address,
                project_type=data.get('project_type', 'commercial'),
                gc_contact={'name': data.get('client', '')},
                contract_amount=float(data.get('value', '0').replace('$', '').replace(',', '') or 0)
            )
            project = {
                'id': result['project_id'],
                'name': result['name'],
                'client': data.get('client', ''),
                'value': data.get('value', ''),
                'status': 'yellow',
                'progress': 0,
                'phase': 'Bidding',
                'assignee': data.get('pm', 'Unassigned'),
                'created': result.get('created_at', datetime.now().isoformat())
            }
            return jsonify({'success': True, 'project': project})
        except Exception as e:
            print(f"API error: {e}, falling back to local")

    # Fallback to local storage
    project = {
        'id': len(COMPANY_DATA['projects']) + 1,
        'name': data['name'],
        'client': data.get('client', ''),
        'value': data.get('value', ''),
        'status': 'yellow',
        'progress': 0,
        'phase': 'Bidding',
        'assignee': data.get('pm', 'Unassigned'),
        'created': datetime.now().isoformat()
    }

    COMPANY_DATA['projects'].append(project)

    # Log activity
    COMPANY_DATA['activities'].insert(0, {
        'type': 'info',
        'text': f'New project created: {project["name"]}',
        'time': datetime.now().isoformat(),
        'project': project['name']
    })

    return jsonify({'success': True, 'project': project})


@app.route('/api/company/projects/<project_id>', methods=['PUT'])
def update_company_project(project_id):
    """Update a company project."""
    data = request.json

    if API_AVAILABLE and api_client:
        try:
            # Map frontend fields to API fields
            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'status' in data:
                # Map traffic light status to project status
                status_map = {'green': 'complete', 'yellow': 'in_progress', 'red': 'bidding'}
                update_data['status'] = status_map.get(data['status'], data['status'])
            if 'phase' in data:
                update_data['status'] = data['phase'].lower().replace(' ', '_')

            result = api_client.update_project(str(project_id), **update_data)
            return jsonify({'success': True, 'project': result})
        except Exception as e:
            print(f"API error: {e}, falling back to local")

    # Fallback to local
    for project in COMPANY_DATA['projects']:
        if str(project['id']) == str(project_id):
            project.update(data)
            return jsonify({'success': True, 'project': project})
    return jsonify({'error': 'Project not found'}), 404


@app.route('/api/company/projects/<project_id>', methods=['DELETE'])
def delete_company_project(project_id):
    """Delete a company project."""
    if API_AVAILABLE and api_client:
        try:
            result = api_client.delete_project(str(project_id))
            if result:
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Failed to delete project'}), 500
        except Exception as e:
            print(f"API error: {e}, falling back to local")

    # Fallback to local
    for i, project in enumerate(COMPANY_DATA['projects']):
        if str(project['id']) == str(project_id):
            COMPANY_DATA['projects'].pop(i)
            return jsonify({'success': True})
    return jsonify({'error': 'Project not found'}), 404


@app.route('/api/company/activity', methods=['GET'])
def get_company_activity():
    """Get company activity feed."""
    limit = request.args.get('limit', 20, type=int)
    # Activities stay local for now (audit log integration later)
    return jsonify({'activities': COMPANY_DATA['activities'][:limit]})


@app.route('/api/company/activity', methods=['POST'])
def log_company_activity():
    """Log a new activity."""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Activity text required'}), 400

    activity = {
        'type': data.get('type', 'info'),
        'text': data['text'],
        'time': datetime.now().isoformat(),
        'project': data.get('project', 'System')
    }

    COMPANY_DATA['activities'].insert(0, activity)
    return jsonify({'success': True, 'activity': activity})


@app.route('/api/company/seats', methods=['GET'])
def get_company_seats():
    """Get all seat statuses."""
    if API_AVAILABLE and api_client:
        try:
            configs = api_client.list_position_configs()
            # Transform position configs to seats format
            seats = {}
            position_map = {
                'project_manager': 'pm',
                'estimator': 'estimator',
                'operations': 'operations',
                'accounting': 'accounting',
                'superintendent': 'field',
                'shop_drawings': 'shop-drawings'
            }
            for config in configs:
                pos = config.get('position', '')
                seat_key = position_map.get(pos, pos)
                seats[seat_key] = {
                    'user': 'Active' if config.get('mode') != 'off' else 'Offline',
                    'status': 'online' if config.get('mode') != 'off' else 'offline',
                    'mode': config.get('mode', 'assist')
                }
            # Fill in defaults for any missing seats
            for key in ['pm', 'estimator', 'operations', 'accounting', 'field', 'shop-drawings']:
                if key not in seats:
                    seats[key] = COMPANY_DATA['seats'].get(key, {'user': 'Active', 'status': 'online'})
            return jsonify({'seats': seats})
        except Exception as e:
            print(f"API error: {e}, falling back to local")
    return jsonify({'seats': COMPANY_DATA['seats']})


@app.route('/api/company/seats/<role>', methods=['PUT'])
def update_seat_status(role):
    """Update a seat's status."""
    data = request.json

    if API_AVAILABLE and api_client:
        try:
            # Map seat role to position name
            role_map = {
                'pm': 'project_manager',
                'estimator': 'estimator',
                'operations': 'operations',
                'accounting': 'accounting',
                'field': 'superintendent',
                'shop-drawings': 'shop_drawings'
            }
            position = role_map.get(role, role)

            if 'mode' in data:
                result = api_client.update_position_mode(position, data['mode'])
                return jsonify({'success': True, 'seat': result})
        except Exception as e:
            print(f"API error: {e}, falling back to local")

    # Fallback to local
    if role in COMPANY_DATA['seats']:
        COMPANY_DATA['seats'][role].update(data)
        return jsonify({'success': True, 'seat': COMPANY_DATA['seats'][role]})
    return jsonify({'error': 'Role not found'}), 404


@app.route('/api/company/metrics', methods=['GET'])
def get_company_metrics():
    """Get company dashboard metrics."""
    if API_AVAILABLE and api_client:
        try:
            result = api_client.list_projects()
            projects = result.get('projects', [])

            active_projects = len([p for p in projects if p.get('status') not in ['complete', 'cancelled']])
            pending_bids = len([p for p in projects if p.get('status') in ['bidding']])
            roadblocks = len([p for p in projects if p.get('status') in ['cancelled']])

            # Calculate revenue from contract amounts
            total_value = sum(float(p.get('contract_amount') or 0) for p in projects if p.get('status') == 'in_progress')
            revenue_str = f"${total_value/1000:.0f}K" if total_value >= 1000 else f"${total_value:.0f}"

            return jsonify({
                'active_projects': active_projects,
                'pending_bids': pending_bids,
                'roadblocks': roadblocks,
                'revenue_mtd': revenue_str,
                'total_projects': result.get('total', len(projects))
            })
        except Exception as e:
            print(f"API error: {e}, falling back to local")

    # Fallback to local
    active_projects = len([p for p in COMPANY_DATA['projects'] if p.get('status') != 'completed'])
    pending_bids = len([p for p in COMPANY_DATA['projects'] if p.get('phase') in ['Bidding', 'Estimating']])
    roadblocks = len([p for p in COMPANY_DATA['projects'] if p.get('status') == 'red'])

    return jsonify({
        'active_projects': active_projects,
        'pending_bids': pending_bids,
        'roadblocks': roadblocks,
        'revenue_mtd': '$847K'
    })


# =============================================================================
# ROUTES - Roofio AI API
# =============================================================================

# Try to import the architect AI rules engine
try:
    from architect_ai.rules_engine import route_query, handle_tier_0, Tier
    ROOFIO_RULES_LOADED = True
except ImportError:
    ROOFIO_RULES_LOADED = False
    print("Warning: Architect AI rules engine not loaded")

# Try to import Groq client
try:
    from roofio.groq_client import ask_groq, GROQ_AVAILABLE
    GROQ_CLIENT_LOADED = True
except ImportError:
    GROQ_CLIENT_LOADED = False
    GROQ_AVAILABLE = False
    print("Warning: Groq client not loaded")


@app.route('/api/roofio/ask', methods=['POST'])
def roofio_ask():
    """Roofio AI question endpoint - routes to appropriate tier."""
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'Question required'}), 400

    question = data['question']
    context = data.get('context', {})

    # Try to use rules engine if available
    if ROOFIO_RULES_LOADED:
        try:
            tier, reason, tier_context = route_query(question, context)

            if tier == Tier.PYTHON:
                # Handle with Python rules (free, fast)
                result = handle_tier_0(question, tier_context)
                return jsonify({
                    'response': result['response'],
                    'citations': result.get('citations', []),
                    'tier': 'python',
                    'cost': 0
                })
            elif GROQ_CLIENT_LOADED and GROQ_AVAILABLE:
                # Use Groq for GROQ tier (fast, cheap)
                result = ask_groq(question, tier_context)
                return jsonify({
                    'response': result['response'],
                    'citations': result.get('citations', []),
                    'tier': 'groq',
                    'cost': result.get('cost', 0),
                    'model': result.get('model'),
                    'tokens': result.get('tokens')
                })
            else:
                # Groq not available, use fallback
                return jsonify({
                    'response': generate_roofio_response(question),
                    'citations': get_relevant_citations(question),
                    'tier': 'fallback',
                    'cost': 0
                })
        except Exception as e:
            print(f"Rules engine error: {e}")

    # Fallback response if rules engine not available
    return jsonify({
        'response': generate_roofio_response(question),
        'citations': get_relevant_citations(question),
        'tier': 'fallback',
        'cost': 0
    })


@app.route('/api/roofio/skills', methods=['GET'])
def roofio_skills():
    """List all available Roofio skills."""
    skills = {
        'codes': [
            {'id': 'asce-7', 'name': 'ASCE 7 Wind & Hazard', 'status': 'ready'},
            {'id': 'ibc', 'name': 'IBC Roofing', 'status': 'ready'},
            {'id': 'irc', 'name': 'IRC Residential', 'status': 'planned'},
            {'id': 'icc', 'name': 'ICC Standards', 'status': 'planned'},
        ],
        'standards': [
            {'id': 'fm-global', 'name': 'FM Global', 'status': 'ready'},
            {'id': 'nrca', 'name': 'NRCA Manual', 'status': 'ready'},
            {'id': 'spri', 'name': 'SPRI', 'status': 'planned'},
            {'id': 'iibec', 'name': 'IIBEC', 'status': 'planned'},
        ],
        'systems': [
            {'id': 'tpo', 'name': 'TPO Membrane', 'status': 'ready'},
            {'id': 'epdm', 'name': 'EPDM Rubber', 'status': 'ready'},
            {'id': 'pvc', 'name': 'PVC Membrane', 'status': 'ready'},
            {'id': 'mod-bit', 'name': 'Modified Bitumen', 'status': 'ready'},
            {'id': 'bur', 'name': 'Built-Up Roofing', 'status': 'planned'},
            {'id': 'metal', 'name': 'Metal Roofing', 'status': 'planned'},
        ],
        'manufacturers': [
            {'id': 'carlisle', 'name': 'Carlisle SynTec', 'status': 'ready'},
            {'id': 'firestone', 'name': 'Firestone BP', 'status': 'ready'},
            {'id': 'gaf', 'name': 'GAF', 'status': 'ready'},
            {'id': 'jm', 'name': 'Johns Manville', 'status': 'planned'},
            {'id': 'sika', 'name': 'Sika Sarnafil', 'status': 'planned'},
        ],
        'tools': [
            {'id': 'asce-hazard', 'name': 'ASCE 7 Hazard Tool', 'status': 'ready'},
            {'id': 'uplift-calc', 'name': 'Uplift Calculator', 'status': 'ready'},
            {'id': 'leak-detection', 'name': 'Leak Detection', 'status': 'ready'},
        ]
    }
    return jsonify({'skills': skills})


def generate_roofio_response(question):
    """Generate a contextual Roofio response based on keywords."""
    question_lower = question.lower()

    # Wind uplift questions
    if any(kw in question_lower for kw in ['wind', 'uplift', 'asce', 'rating']):
        return """🏗️ **Wind Uplift Requirements**

For wind uplift calculations, I need a few details:
- **Building height** (affects exposure)
- **Location** (for basic wind speed from ASCE 7)
- **Roof zone** (field, perimeter, or corner)

**Quick Reference - FM Ratings:**
- **I-60**: Field zones, low wind areas
- **I-90**: Standard commercial, most field areas
- **I-120**: Perimeter zones, higher wind
- **I-165**: Corners, coastal/hurricane zones
- **I-240**: High-velocity hurricane zones (HVHZ)

**Code Citations:**
- ASCE 7-22, Chapter 30 - Components & Cladding
- FM Global DS 1-29 - Roof Deck Securement
- IBC 2021, Section 1504 - Performance Requirements

*What's your building height and location? I can calculate the specific requirements.*"""

    # TPO vs PVC questions
    elif any(kw in question_lower for kw in ['tpo', 'pvc', 'compare', 'vs']):
        return """🏗️ **TPO vs PVC Comparison**

| Feature | TPO | PVC |
|---------|-----|-----|
| **Chemical Resistance** | Moderate | Excellent |
| **Grease/Oil Resistance** | Poor | Excellent |
| **Cost** | Lower | Higher |
| **Weldability** | Good | Excellent |
| **Best Use** | General commercial | Restaurants, chemical plants |

**My Recommendation:**
- **TPO**: Standard commercial, warehouses, retail
- **PVC**: Kitchens, restaurants, chemical exposure, high-traffic

**Spec Sections:**
- 07 54 23 - Thermoplastic Polyolefin (TPO)
- 07 54 19 - Polyvinyl Chloride (PVC)

*What type of building is this for?*"""

    # Code/IBC questions
    elif any(kw in question_lower for kw in ['ibc', 'code', 'drainage', 'slope']):
        return """🏗️ **IBC Roofing Requirements**

**Drainage (IBC 1502, 1503):**
- Minimum slope: 1/4" per foot (1:48)
- Secondary drainage required when parapet height > 6"
- Overflow drains: 2" above primary drain

**Fire Classification (IBC 1505):**
- Class A, B, or C per ASTM E108
- Class A required within 3' of lot line
- Fire-retardant treatment for wood decks

**Wind Resistance (IBC 1504):**
- Must resist design wind loads per ASCE 7
- Edge securement per manufacturer specs

**Code Citations:**
- IBC 2021, Chapter 15 - Roof Assemblies
- ASCE 7-22, Chapter 30 - Wind Loads

*Which specific code requirement do you need help with?*"""

    # Leak detection
    elif any(kw in question_lower for kw in ['leak', 'detection', 'moisture', 'survey']):
        return """🏗️ **Leak Detection Methods**

**Non-Destructive Testing:**
1. **Electronic Leak Detection (ELD)**
   - Best for single-ply membranes
   - Pinpoints exact breach location
   - Requires wet roof surface

2. **Infrared (IR) Thermography**
   - Detects trapped moisture
   - Best performed at night after sunny day
   - Shows moisture patterns, not leak source

3. **Nuclear Moisture Gauge**
   - Quantifies moisture content
   - Grid pattern survey
   - Requires calibration

**Destructive Testing:**
4. **Core Cuts**
   - Confirms insulation condition
   - Visual moisture assessment
   - Patch required after

**Recommendation:**
Start with IR survey → ELD for pinpoint → Core cut to confirm

*What type of roof system are you investigating?*"""

    # Default response
    else:
        return f"""🏗️ **I can help with that!**

I'm Roofio, your Division 07 expert. I specialize in:

- **Codes**: ASCE 7, IBC, IRC, FM Global
- **Systems**: TPO, EPDM, PVC, Mod-Bit, BUR, Metal
- **Manufacturers**: Carlisle, Firestone, GAF (expanding weekly)
- **Calculations**: Wind uplift, drainage, R-values
- **Inspections**: Leak detection, moisture surveys, core analysis
- **Details**: Flashing, terminations, transitions

Your question: *"{question}"*

Could you provide more context? For example:
- Building location and height
- Roof system type
- Specific code or standard needed

*The more details you share, the better I can help!*"""


def get_relevant_citations(question):
    """Return relevant code citations based on question keywords."""
    question_lower = question.lower()
    citations = []

    if any(kw in question_lower for kw in ['wind', 'uplift', 'asce']):
        citations.extend(['ASCE 7-22', 'FM DS 1-29', 'IBC 1504'])

    if any(kw in question_lower for kw in ['tpo', 'pvc', 'membrane']):
        citations.extend(['ASTM D6878 (TPO)', 'ASTM D4434 (PVC)', 'SPRI'])

    if any(kw in question_lower for kw in ['ibc', 'code', 'building']):
        citations.extend(['IBC 2021 Ch.15', 'IRC R905'])

    if any(kw in question_lower for kw in ['fm', 'factory mutual']):
        citations.extend(['FM 4470', 'FM DS 1-28', 'FM DS 1-29'])

    if any(kw in question_lower for kw in ['nrca', 'manual']):
        citations.extend(['NRCA Roofing Manual'])

    return citations[:5] if citations else ['NRCA Manual', 'IBC 2021']


# =============================================================================
# Background Processing
# =============================================================================

def process_documents_async(session_id, files_data, upload_folder):
    """Process documents in background with progress updates.

    files_data format: {'drawings': [{'filename': 'x.pdf', 'filepath': '/path/to/x.pdf'}, ...], ...}
    Files are already saved to disk before this function is called.
    """
    results = {
        'drawings': [],
        'assemblies': [],
        'specs': [],
        'scopes': [],
        'filter_stats': {
            'total_pages_scanned': 0,
            'roof_pages_found': 0,
            'savings_percent': 0
        }
    }

    total_files = sum(len(v) for v in files_data.values())
    processed = 0

    try:
        # Process drawings with filter
        if 'drawings' in files_data:
            send_progress(session_id, 'drawings', 0, 'Starting drawing analysis...')

            for i, file_info in enumerate(files_data['drawings']):
                filename = file_info['filename']
                filepath = file_info['filepath']

                send_progress(
                    session_id, 'drawings',
                    int((i / len(files_data['drawings'])) * 100),
                    f'Analyzing {filename}...'
                )

                # Run filter first
                filter_result = filter_roof_pages(filepath, threshold=10, verbose=False)
                results['filter_stats']['total_pages_scanned'] += filter_result['total_pages']
                results['filter_stats']['roof_pages_found'] += filter_result['pages_to_process']

                if filter_result['pages_to_process'] > 0:
                    # Extract only roof pages
                    roof_page_nums = [p['page_num'] for p in filter_result['roof_pages']]
                    text = extract_text_from_pdf_filtered(filepath, roof_page_nums)

                    # Parse
                    parsed = parse_architectural_drawing(text)
                    parsed['filename'] = filename
                    parsed['filter_stats'] = {
                        'total_pages': filter_result['total_pages'],
                        'roof_pages': filter_result['pages_to_process'],
                        'savings_percent': filter_result['savings_percent']
                    }
                    results['drawings'].append(parsed)
                else:
                    results['drawings'].append({
                        'filename': filename,
                        'filtered_out': True,
                        'message': 'No roof content detected'
                    })

                processed += 1

            # Calculate overall savings
            if results['filter_stats']['total_pages_scanned'] > 0:
                results['filter_stats']['savings_percent'] = round(
                    (1 - results['filter_stats']['roof_pages_found'] /
                     results['filter_stats']['total_pages_scanned']) * 100, 1
                )

        # Process assemblies
        if 'assemblies' in files_data:
            send_progress(session_id, 'assemblies', 0, 'Parsing assembly letters...')

            for i, file_info in enumerate(files_data['assemblies']):
                filename = file_info['filename']
                filepath = file_info['filepath']

                send_progress(
                    session_id, 'assemblies',
                    int((i / len(files_data['assemblies'])) * 100),
                    f'Parsing {filename}...'
                )

                text = extract_text_from_pdf(filepath)
                parsed = parse_assembly_letter(text)
                parsed['filename'] = filename
                results['assemblies'].append(parsed)

                processed += 1

        # Process specs
        if 'specs' in files_data:
            send_progress(session_id, 'specs', 0, 'Analyzing specifications...')

            for i, file_info in enumerate(files_data['specs']):
                filename = file_info['filename']
                filepath = file_info['filepath']

                text = extract_text_from_pdf(filepath)
                parsed = parse_specification(text)
                parsed['filename'] = filename
                results['specs'].append(parsed)

                processed += 1

        # Process scopes
        if 'scopes' in files_data:
            send_progress(session_id, 'scopes', 0, 'Analyzing scope of work...')

            for i, file_info in enumerate(files_data['scopes']):
                filename = file_info['filename']
                filepath = file_info['filepath']

                text = extract_text_from_pdf(filepath)
                parsed = parse_scope_of_work(text)
                parsed['filename'] = filename
                results['scopes'].append(parsed)

                processed += 1

        # Complete
        send_progress(session_id, 'complete', 100, 'Analysis complete!', results)

    except Exception as e:
        import traceback
        error_msg = f'Error: {str(e)}'
        print(f"Processing error: {error_msg}")
        traceback.print_exc()
        send_progress(session_id, 'error', 0, error_msg)


# =============================================================================
# Utility Functions
# =============================================================================

def extract_text_from_pdf(filepath):
    """Extract all text from PDF."""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text


def extract_text_from_pdf_filtered(filepath, page_numbers=None):
    """Extract text from specific pages only."""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            if page_numbers is None:
                pages_to_extract = range(total_pages)
            else:
                pages_to_extract = [p - 1 for p in page_numbers if 0 < p <= total_pages]

            for i in pages_to_extract:
                page_text = pdf_reader.pages[i].extract_text() or ""
                text += f"\n--- PAGE {i+1} ---\n" + page_text + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text


def parse_specification(text):
    """Parse specification document."""
    text = clean_rtf_text(text)

    manufacturers = []
    mfr_patterns = [
        r'(?i)manufacturer[s]?:\s*([^\n]+)',
        r'(?i)(?:Carlisle|GAF|Firestone|Johns Manville|Versico|Siplast|SOPREMA|Sika|Barrett|Tremco)',
    ]

    for pattern in mfr_patterns:
        matches = re.findall(pattern, text) if 're' in dir() else []
        manufacturers.extend(matches)

    manufacturers = deduplicate_list(manufacturers)

    return {
        'manufacturers': manufacturers[:10] if manufacturers else None,
        'type': 'Specification'
    }


def parse_scope_of_work(text):
    """Parse scope of work document."""
    text = clean_rtf_text(text)

    materials = []
    requirements = []

    # Create summary
    sentences = text.split('.')[:3]
    summary = '. '.join(sentences).strip()

    return {
        'summary': summary[:500] if summary else None,
        'materials': materials[:15] if materials else None,
        'requirements': requirements if requirements else None,
        'type': 'Scope of Work'
    }


def extract_count(detection_string):
    """Extract count from detection string like '(5) drains'."""
    if not detection_string:
        return 0
    import re
    match = re.search(r'\((\d+)\)', detection_string)
    return int(match.group(1)) if match else 0


# Need re for parse functions
import re


# =============================================================================
# ROUTES - Form Templates API (Proxy to FastAPI Backend)
# =============================================================================

@app.route('/api/forms/templates', methods=['GET'])
def get_form_templates():
    """Get all form templates from backend API."""
    if API_AVAILABLE and api_client:
        try:
            form_type = request.args.get('form_type')
            status = request.args.get('status', 'active')
            result = api_client.list_form_templates(form_type=form_type, status=status)
            return jsonify(result)
        except Exception as e:
            print(f"API error fetching form templates: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Backend API not available'}), 503


@app.route('/api/forms/templates', methods=['POST'])
def create_form_template():
    """Create a new form template."""
    if API_AVAILABLE and api_client:
        try:
            data = request.json
            result = api_client.create_form_template(
                name=data['name'],
                form_type=data['form_type'],
                is_custom=data.get('is_custom', True),
                description=data.get('description'),
                fields=data.get('fields'),
                roofio_additions=data.get('roofio_additions')
            )
            return jsonify(result), 201
        except Exception as e:
            print(f"API error creating form template: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Backend API not available'}), 503


@app.route('/api/forms/templates/<template_id>', methods=['GET'])
def get_form_template(template_id):
    """Get a specific form template."""
    if API_AVAILABLE and api_client:
        try:
            result = api_client.get_form_template(template_id)
            if result:
                return jsonify(result)
            return jsonify({'error': 'Template not found'}), 404
        except Exception as e:
            print(f"API error: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Backend API not available'}), 503


@app.route('/api/forms/types', methods=['GET'])
def get_form_types():
    """Get available form types."""
    if API_AVAILABLE and api_client:
        try:
            result = api_client.list_form_types()
            return jsonify(result)
        except Exception as e:
            print(f"API error: {e}")
            return jsonify({'error': str(e)}), 500
    # Return default form types if API unavailable
    return jsonify({
        'form_types': [
            {'id': 'daily_report', 'name': 'Daily Report', 'category': 'Field'},
            {'id': 'jha', 'name': 'Job Hazard Analysis', 'category': 'Safety'},
            {'id': 'rfi', 'name': 'Request for Information', 'category': 'Documentation'},
            {'id': 'moisture_survey', 'name': 'Moisture Survey', 'category': 'Inspection'},
            {'id': 'change_order', 'name': 'Change Order', 'category': 'Documentation'}
        ]
    })


@app.route('/api/forms/preference/<form_type>', methods=['GET'])
def get_form_preference(form_type):
    """Get user's preference for a form type."""
    if API_AVAILABLE and api_client:
        try:
            result = api_client.get_form_preference(form_type)
            return jsonify(result)
        except Exception as e:
            print(f"API error: {e}")
            # Return default preference
            return jsonify({
                'first_time_setup': True,
                'has_preference': False,
                'use_custom': False
            })
    return jsonify({
        'first_time_setup': True,
        'has_preference': False,
        'use_custom': False
    })


# =============================================================================
# Run App
# =============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  ROOFING INTELLIGENCE PLATFORM")
    print("  Modern Analysis Tool for Division 07")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000, threaded=True)
