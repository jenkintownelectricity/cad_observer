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
    """Redirect to dashboard as the main page."""
    return redirect('/dashboard')


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


@app.route('/projects')
def projects():
    """Project management page."""
    project_files = []
    for f in os.listdir(app.config['PROJECTS_FOLDER']):
        if f.endswith('.json'):
            filepath = os.path.join(app.config['PROJECTS_FOLDER'], f)
            with open(filepath, 'r') as pf:
                project_data = json.load(pf)
                project_files.append({
                    'filename': f,
                    'name': project_data.get('name', f.replace('.json', '')),
                    'created': project_data.get('created', 'Unknown'),
                    'documents': len(project_data.get('documents', []))
                })
    return render_template('projects.html', projects=project_files)


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
    return jsonify({'projects': COMPANY_DATA['projects']})


@app.route('/api/company/projects', methods=['POST'])
def create_company_project():
    """Create a new company project."""
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name required'}), 400

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


@app.route('/api/company/projects/<int:project_id>', methods=['PUT'])
def update_company_project(project_id):
    """Update a company project."""
    data = request.json
    for project in COMPANY_DATA['projects']:
        if project['id'] == project_id:
            project.update(data)
            return jsonify({'success': True, 'project': project})
    return jsonify({'error': 'Project not found'}), 404


@app.route('/api/company/activity', methods=['GET'])
def get_company_activity():
    """Get company activity feed."""
    limit = request.args.get('limit', 20, type=int)
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
    return jsonify({'seats': COMPANY_DATA['seats']})


@app.route('/api/company/seats/<role>', methods=['PUT'])
def update_seat_status(role):
    """Update a seat's status."""
    data = request.json
    if role in COMPANY_DATA['seats']:
        COMPANY_DATA['seats'][role].update(data)
        return jsonify({'success': True, 'seat': COMPANY_DATA['seats'][role]})
    return jsonify({'error': 'Role not found'}), 404


@app.route('/api/company/metrics', methods=['GET'])
def get_company_metrics():
    """Get company dashboard metrics."""
    active_projects = len([p for p in COMPANY_DATA['projects'] if p.get('status') != 'completed'])
    pending_bids = len([p for p in COMPANY_DATA['projects'] if p.get('phase') in ['Bidding', 'Estimating']])
    roadblocks = len([p for p in COMPANY_DATA['projects'] if p.get('status') == 'red'])

    return jsonify({
        'active_projects': active_projects,
        'pending_bids': pending_bids,
        'roadblocks': roadblocks,
        'revenue_mtd': '$847K'  # Would calculate from actual data
    })


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
# Run App
# =============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  ROOFING INTELLIGENCE PLATFORM")
    print("  Modern Analysis Tool for Division 07")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000, threaded=True)
