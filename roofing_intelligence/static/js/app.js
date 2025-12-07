/**
 * Roofing Intelligence Platform
 * Modern JavaScript Application
 * Features: Real-time SSE, Project Management, Learning System
 */

// =============================================================================
// GLOBAL STATE
// =============================================================================

const AppState = {
    theme: localStorage.getItem('theme') || 'dark',
    currentView: 'cards',
    files: {
        drawings: [],
        assemblies: [],
        specs: [],
        scopes: []
    },
    results: null,
    workflowStates: JSON.parse(localStorage.getItem('workflowStates') || '{}'),
    sessionId: null,
    eventSource: null,
    currentProject: null,
    learningData: JSON.parse(localStorage.getItem('learningData') || '{"patterns": [], "corrections": []}')
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initFileInputs();
    initDragAndDrop();
    initForm();
    loadLastSession();
    console.log('Roofing Intelligence Platform initialized');
});

function initTheme() {
    document.documentElement.setAttribute('data-theme', AppState.theme);
}

function toggleTheme() {
    AppState.theme = AppState.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', AppState.theme);
    localStorage.setItem('theme', AppState.theme);
    showToast('Theme switched', 'info');
}

// =============================================================================
// FILE HANDLING
// =============================================================================

function initFileInputs() {
    const types = ['drawings', 'assemblies', 'specs', 'scopes'];

    types.forEach(type => {
        const input = document.getElementById(type);
        const label = document.querySelector(`label[for="${type}"]`);

        if (input) {
            // Handle file selection
            input.addEventListener('change', (e) => {
                const newFiles = Array.from(e.target.files);
                AppState.files[type] = [...AppState.files[type], ...newFiles];
                updateFileList(type);
                updateAnalyzeButton();
                showToast(`${newFiles.length} file(s) added`, 'success');
            });
        }

        // Explicit click handler for the label/button (fixes browser compatibility)
        if (label && input) {
            label.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                input.click();
            });
        }
    });

    // Also make entire card clickable
    document.querySelectorAll('.upload-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // Don't trigger if clicking on file list or remove button
            if (e.target.closest('.file-list') || e.target.closest('.remove')) {
                return;
            }
            const type = card.dataset.type;
            const input = document.getElementById(type);
            if (input) {
                input.click();
            }
        });
    });
}

function initDragAndDrop() {
    const cards = document.querySelectorAll('.upload-card');

    cards.forEach(card => {
        card.addEventListener('dragover', (e) => {
            e.preventDefault();
            card.classList.add('drag-over');
        });

        card.addEventListener('dragleave', () => {
            card.classList.remove('drag-over');
        });

        card.addEventListener('drop', (e) => {
            e.preventDefault();
            card.classList.remove('drag-over');

            const type = card.dataset.type;
            const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');

            if (files.length > 0) {
                AppState.files[type] = [...AppState.files[type], ...files];
                updateFileList(type);
                updateAnalyzeButton();
                showToast(`${files.length} file(s) added`, 'success');
            }
        });
    });
}

function updateFileList(type) {
    const list = document.getElementById(`${type}-list`);
    const card = document.querySelector(`.upload-card[data-type="${type}"]`);

    if (!list) return;

    if (AppState.files[type].length === 0) {
        list.innerHTML = '';
        card?.classList.remove('has-files');
        return;
    }

    card?.classList.add('has-files');

    list.innerHTML = AppState.files[type].map((file, index) => `
        <div class="file-item">
            <span>${file.name}</span>
            <span class="remove" onclick="removeFile('${type}', ${index})">×</span>
        </div>
    `).join('');
}

window.removeFile = function(type, index) {
    AppState.files[type].splice(index, 1);
    updateFileList(type);
    updateAnalyzeButton();
};

function updateAnalyzeButton() {
    const btn = document.getElementById('analyzeBtn');
    const hasFiles = Object.values(AppState.files).some(arr => arr.length > 0);
    btn.disabled = !hasFiles;
}

// =============================================================================
// FORM SUBMISSION & ANALYSIS
// =============================================================================

function initForm() {
    const form = document.getElementById('analysisForm');
    if (form) {
        form.addEventListener('submit', handleAnalysis);
    }
}

async function handleAnalysis(e) {
    e.preventDefault();

    // Build form data
    const formData = new FormData();

    Object.entries(AppState.files).forEach(([type, files]) => {
        files.forEach(file => formData.append(type, file));
    });

    // Show progress section
    showProgressSection();

    try {
        // Start analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Analysis failed');

        const { session_id } = await response.json();
        AppState.sessionId = session_id;

        // Connect to SSE for progress
        connectProgressStream(session_id);

    } catch (error) {
        console.error('Analysis error:', error);
        showToast('Analysis failed: ' + error.message, 'error');
        hideProgressSection();
    }
}

function connectProgressStream(sessionId) {
    if (AppState.eventSource) {
        AppState.eventSource.close();
    }

    AppState.eventSource = new EventSource(`/api/progress/${sessionId}`);

    AppState.eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.keepalive) return;

        updateProgress(data);

        if (data.step === 'complete') {
            AppState.eventSource.close();
            AppState.results = data.data;
            saveSession();
            setTimeout(() => {
                hideProgressSection();
                showResults(data.data);
            }, 500);
        }

        if (data.step === 'error') {
            AppState.eventSource.close();
            showToast(data.message, 'error');
            hideProgressSection();
        }
    };

    AppState.eventSource.onerror = () => {
        console.error('SSE connection error');
        AppState.eventSource.close();
    };
}

function updateProgress(data) {
    const progressBar = document.getElementById('progressBar');
    const progressMessage = document.getElementById('progressMessage');

    if (progressBar && data.progress !== undefined) {
        progressBar.style.width = `${data.progress}%`;
    }

    if (progressMessage && data.message) {
        progressMessage.textContent = data.message;
    }

    // Update step indicators
    const steps = ['drawings', 'assemblies', 'specs', 'complete'];
    steps.forEach(step => {
        const stepEl = document.getElementById(`step-${step}`);
        if (stepEl) {
            stepEl.classList.remove('active', 'complete');

            if (step === data.step) {
                stepEl.classList.add('active');
            } else if (steps.indexOf(step) < steps.indexOf(data.step)) {
                stepEl.classList.add('complete');
            }
        }
    });

    // Show savings if available
    if (data.data?.filter_stats) {
        const stats = data.data.filter_stats;
        showSavings(stats.savings_percent, stats.roof_pages_found, stats.total_pages_scanned);
    }
}

function showSavings(percent, roofPages, totalPages) {
    const display = document.getElementById('savingsDisplay');
    const percentEl = document.getElementById('savingsPercent');
    const detailEl = document.getElementById('savingsDetail');

    if (display && percent > 0) {
        display.classList.remove('hidden');
        percentEl.textContent = `${percent}%`;
        detailEl.textContent = `Processing ${roofPages} of ${totalPages} pages`;
    }
}

function showProgressSection() {
    document.querySelector('.upload-section')?.classList.add('hidden');
    document.getElementById('progressSection')?.classList.remove('hidden');
    document.getElementById('resultsSection')?.classList.add('hidden');

    // Reset progress
    const progressBar = document.getElementById('progressBar');
    if (progressBar) progressBar.style.width = '0%';

    document.querySelectorAll('.step').forEach(s => s.classList.remove('active', 'complete'));
    document.getElementById('savingsDisplay')?.classList.add('hidden');
}

function hideProgressSection() {
    document.getElementById('progressSection')?.classList.add('hidden');
}

// =============================================================================
// RESULTS DISPLAY
// =============================================================================

function showResults(data) {
    document.getElementById('resultsSection')?.classList.remove('hidden');

    // Update stats
    renderStats(data);

    // Render results
    if (AppState.currentView === 'cards') {
        renderCardsView(data);
    } else {
        renderTableView(data);
    }

    showToast('Analysis complete!', 'success');

    // Record learning data
    recordPattern(data);
}

function renderStats(data) {
    const statsGrid = document.getElementById('statsGrid');
    if (!statsGrid) return;

    const drawings = data.drawings || [];
    const stats = calculateStats(drawings);

    statsGrid.innerHTML = `
        <div class="stat-card accent">
            <div class="stat-value">${stats.totalSheets}</div>
            <div class="stat-label">Roof Sheets</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.totalDrains}</div>
            <div class="stat-label">Drains</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.totalScuppers}</div>
            <div class="stat-label">Scuppers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.totalRTUs}</div>
            <div class="stat-label">RTUs/Curbs</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.totalPenetrations}</div>
            <div class="stat-label">Penetrations</div>
        </div>
        ${data.filter_stats ? `
        <div class="stat-card">
            <div class="stat-value" style="color: var(--success);">${data.filter_stats.savings_percent}%</div>
            <div class="stat-label">Cost Saved</div>
        </div>
        ` : ''}
    `;

    // Update toolbar stats
    const toolbarStats = document.getElementById('toolbarStats');
    if (toolbarStats) {
        toolbarStats.innerHTML = `
            <span>${drawings.length} files</span>
            <span>•</span>
            <span>${stats.totalSheets} sheets</span>
        `;
    }
}

function calculateStats(drawings) {
    let totalSheets = 0, totalDrains = 0, totalScuppers = 0, totalRTUs = 0, totalPenetrations = 0;

    drawings.forEach(drawing => {
        if (drawing.roof_plans) {
            drawing.roof_plans.forEach(plan => {
                totalSheets++;
                totalDrains += extractCount(plan.drains);
                totalScuppers += extractCount(plan.scuppers);
                totalRTUs += extractCount(plan.rtus_curbs);
                totalPenetrations += extractCount(plan.penetrations);
            });
        }
    });

    return { totalSheets, totalDrains, totalScuppers, totalRTUs, totalPenetrations };
}

function extractCount(str) {
    if (!str) return 0;
    const match = str.match(/\((\d+)\)/);
    return match ? parseInt(match[1]) : 0;
}

function getConfidence(str) {
    if (!str) return 'none';
    if (str.includes('✓✓✓')) return 'high';
    if (str.includes('✓✓')) return 'medium';
    if (str.includes('✓')) return 'low';
    return 'none';
}

function renderCardsView(data) {
    const content = document.getElementById('resultsContent');
    if (!content) return;

    const drawings = data.drawings || [];
    let html = '<div class="cards-grid">';

    drawings.forEach((drawing, dIdx) => {
        if (drawing.filtered_out) {
            html += `
                <div class="result-card" style="opacity: 0.5;">
                    <div class="card-header">
                        <div>
                            <div class="card-title">${drawing.filename}</div>
                            <div class="card-subtitle">No roof content detected</div>
                        </div>
                        <span class="card-badge badge-detected">Filtered</span>
                    </div>
                    <p style="color: var(--text-muted); font-size: 0.875rem;">${drawing.message}</p>
                </div>
            `;
            return;
        }

        if (drawing.roof_plans) {
            drawing.roof_plans.forEach((plan, pIdx) => {
                const sheetId = `${dIdx}-${pIdx}`;
                const workflow = AppState.workflowStates[sheetId] || 'detected';

                html += `
                    <div class="result-card" data-sheet-id="${sheetId}">
                        <div class="card-header">
                            <div>
                                <div class="card-title">${drawing.filename}</div>
                                <div class="card-subtitle">Sheet: ${plan.detail_number || 'Unknown'}</div>
                            </div>
                            <span class="card-badge badge-${workflow}">${workflow}</span>
                        </div>

                        <div class="card-data">
                            ${plan.type ? `
                            <div class="data-row">
                                <span class="data-label">Type</span>
                                <span class="data-value">${plan.type}</span>
                            </div>
                            ` : ''}

                            <div class="data-row">
                                <span class="data-label">Drains</span>
                                <span class="data-value confidence-${getConfidence(plan.drains)}">${extractCount(plan.drains) || '-'}</span>
                            </div>

                            <div class="data-row">
                                <span class="data-label">Scuppers</span>
                                <span class="data-value confidence-${getConfidence(plan.scuppers)}">${extractCount(plan.scuppers) || '-'}</span>
                            </div>

                            <div class="data-row">
                                <span class="data-label">RTUs/Curbs</span>
                                <span class="data-value confidence-${getConfidence(plan.rtus_curbs)}">${extractCount(plan.rtus_curbs) || '-'}</span>
                            </div>

                            <div class="data-row">
                                <span class="data-label">Penetrations</span>
                                <span class="data-value confidence-${getConfidence(plan.penetrations)}">${extractCount(plan.penetrations) || '-'}</span>
                            </div>

                            ${plan.scale !== 'Not specified' && plan.scale ? `
                            <div class="data-row">
                                <span class="data-label">Scale</span>
                                <span class="data-value">${plan.scale}</span>
                            </div>
                            ` : ''}
                        </div>

                        <div class="card-actions">
                            ${getWorkflowButton(sheetId, workflow)}
                        </div>
                    </div>
                `;
            });
        }
    });

    // Add assemblies if present
    if (data.assemblies && data.assemblies.length > 0) {
        data.assemblies.forEach((assembly, idx) => {
            html += `
                <div class="result-card" style="--card-accent: var(--accent-orange);">
                    <div class="card-header">
                        <div>
                            <div class="card-title">${assembly.filename || 'Assembly Letter'}</div>
                            <div class="card-subtitle">${assembly.manufacturer || 'Unknown Manufacturer'}</div>
                        </div>
                        <span class="card-badge" style="background: rgba(249, 115, 22, 0.15); color: var(--accent-orange);">Assembly</span>
                    </div>

                    <div class="card-data">
                        ${assembly.system ? `
                        <div class="data-row">
                            <span class="data-label">System</span>
                            <span class="data-value">${assembly.system}</span>
                        </div>
                        ` : ''}

                        ${assembly.membrane_1 ? `
                        <div class="data-row">
                            <span class="data-label">Membrane</span>
                            <span class="data-value">${assembly.membrane_1.substring(0, 40)}...</span>
                        </div>
                        ` : ''}

                        ${assembly.insulation_layer_1 ? `
                        <div class="data-row">
                            <span class="data-label">Insulation</span>
                            <span class="data-value">${assembly.insulation_layer_1.substring(0, 40)}...</span>
                        </div>
                        ` : ''}
                    </div>

                    <div class="card-actions">
                        <button class="card-action action-verify" onclick="generateDXF(${idx})">
                            Generate DXF
                        </button>
                    </div>
                </div>
            `;
        });
    }

    html += '</div>';
    content.innerHTML = html;
}

function renderTableView(data) {
    const content = document.getElementById('resultsContent');
    if (!content) return;

    const drawings = data.drawings || [];

    let html = `
        <div style="background: var(--bg-secondary); border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--glass-border);">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: var(--bg-tertiary);">
                        <th style="padding: 1rem; text-align: left; font-weight: 600; font-size: 0.875rem;">File</th>
                        <th style="padding: 1rem; text-align: left; font-weight: 600; font-size: 0.875rem;">Sheet</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">Status</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">Drains</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">Scuppers</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">RTUs</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">Pens</th>
                        <th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

    drawings.forEach((drawing, dIdx) => {
        if (drawing.roof_plans) {
            drawing.roof_plans.forEach((plan, pIdx) => {
                const sheetId = `${dIdx}-${pIdx}`;
                const workflow = AppState.workflowStates[sheetId] || 'detected';

                html += `
                    <tr style="border-bottom: 1px solid var(--glass-border);">
                        <td style="padding: 0.875rem; font-size: 0.875rem;">${drawing.filename}</td>
                        <td style="padding: 0.875rem; font-family: monospace; color: var(--accent);">${plan.detail_number || '-'}</td>
                        <td style="padding: 0.875rem; text-align: center;">
                            <span class="card-badge badge-${workflow}">${workflow}</span>
                        </td>
                        <td style="padding: 0.875rem; text-align: center; font-weight: 600;" class="confidence-${getConfidence(plan.drains)}">${extractCount(plan.drains) || '-'}</td>
                        <td style="padding: 0.875rem; text-align: center; font-weight: 600;" class="confidence-${getConfidence(plan.scuppers)}">${extractCount(plan.scuppers) || '-'}</td>
                        <td style="padding: 0.875rem; text-align: center; font-weight: 600;" class="confidence-${getConfidence(plan.rtus_curbs)}">${extractCount(plan.rtus_curbs) || '-'}</td>
                        <td style="padding: 0.875rem; text-align: center; font-weight: 600;" class="confidence-${getConfidence(plan.penetrations)}">${extractCount(plan.penetrations) || '-'}</td>
                        <td style="padding: 0.875rem; text-align: center;">
                            ${getWorkflowButton(sheetId, workflow)}
                        </td>
                    </tr>
                `;
            });
        }
    });

    html += '</tbody></table></div>';
    content.innerHTML = html;
}

function getWorkflowButton(sheetId, state) {
    const buttons = {
        'detected': `<button class="card-action action-verify" onclick="updateWorkflow('${sheetId}', 'reviewing')">Review</button>`,
        'reviewing': `<button class="card-action action-verify" onclick="updateWorkflow('${sheetId}', 'verified')">Verify</button>`,
        'verified': `<button class="card-action action-approve" onclick="updateWorkflow('${sheetId}', 'approved')">Approve</button>`,
        'approved': `<span style="color: var(--success); font-weight: 600;">Approved</span>`
    };
    return buttons[state] || buttons['detected'];
}

window.updateWorkflow = function(sheetId, newState) {
    AppState.workflowStates[sheetId] = newState;
    localStorage.setItem('workflowStates', JSON.stringify(AppState.workflowStates));

    // Re-render
    if (AppState.currentView === 'cards') {
        renderCardsView(AppState.results);
    } else {
        renderTableView(AppState.results);
    }

    showToast(`Status updated to ${newState}`, 'success');

    // Record correction for learning
    recordCorrection(sheetId, newState);
};

window.switchView = function(view) {
    AppState.currentView = view;

    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });

    if (AppState.results) {
        if (view === 'cards') {
            renderCardsView(AppState.results);
        } else {
            renderTableView(AppState.results);
        }
    }
};

window.filterResults = function(term) {
    const cards = document.querySelectorAll('.result-card');
    const rows = document.querySelectorAll('tbody tr');
    const searchTerm = term.toLowerCase();

    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? '' : 'none';
    });

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
};

// =============================================================================
// EXPORT & PROJECT MANAGEMENT
// =============================================================================

window.exportCSV = async function() {
    if (!AppState.results) {
        showToast('No data to export', 'error');
        return;
    }

    try {
        const response = await fetch('/api/export/csv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(AppState.results)
        });

        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `roofing_analysis_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);

        showToast('CSV exported successfully', 'success');
    } catch (error) {
        showToast('Export failed: ' + error.message, 'error');
    }
};

window.saveProject = function() {
    if (!AppState.results) {
        showToast('No data to save', 'error');
        return;
    }

    const name = prompt('Enter project name:');
    if (!name) return;

    fetch('/api/project/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: name,
            results: AppState.results,
            workflowStates: AppState.workflowStates
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`Project "${name}" saved!`, 'success');
        }
    })
    .catch(error => {
        showToast('Save failed: ' + error.message, 'error');
    });
};

window.generateDXF = async function(assemblyIndex) {
    if (!AppState.results?.assemblies?.[assemblyIndex]) {
        showToast('No assembly data', 'error');
        return;
    }

    showToast('Generating DXF...', 'info');

    try {
        const response = await fetch('/api/generate-dxf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(AppState.results.assemblies[assemblyIndex])
        });

        if (!response.ok) throw new Error('DXF generation failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'assembly_detail.dxf';
        a.click();
        window.URL.revokeObjectURL(url);

        showToast('DXF generated!', 'success');
    } catch (error) {
        showToast('DXF generation failed', 'error');
    }
};

// =============================================================================
// SESSION MANAGEMENT
// =============================================================================

function saveSession() {
    if (AppState.results) {
        localStorage.setItem('lastSession', JSON.stringify({
            results: AppState.results,
            timestamp: new Date().toISOString()
        }));
    }
}

function loadLastSession() {
    const saved = localStorage.getItem('lastSession');
    if (saved) {
        try {
            const session = JSON.parse(saved);
            const daysSince = (new Date() - new Date(session.timestamp)) / (1000 * 60 * 60 * 24);

            if (daysSince < 7) {
                // Could auto-load or show prompt
                console.log('Previous session available');
            }
        } catch (e) {
            console.error('Failed to load session', e);
        }
    }
}

// =============================================================================
// LEARNING SYSTEM
// =============================================================================

function recordPattern(data) {
    // Record successful patterns for learning
    if (data.drawings) {
        data.drawings.forEach(drawing => {
            if (drawing.roof_plans) {
                drawing.roof_plans.forEach(plan => {
                    AppState.learningData.patterns.push({
                        timestamp: new Date().toISOString(),
                        sheetPattern: plan.detail_number,
                        type: plan.type,
                        drains: extractCount(plan.drains),
                        scuppers: extractCount(plan.scuppers),
                        rtus: extractCount(plan.rtus_curbs),
                        penetrations: extractCount(plan.penetrations)
                    });
                });
            }
        });

        // Keep last 1000 patterns
        if (AppState.learningData.patterns.length > 1000) {
            AppState.learningData.patterns = AppState.learningData.patterns.slice(-1000);
        }

        localStorage.setItem('learningData', JSON.stringify(AppState.learningData));
    }
}

function recordCorrection(sheetId, newState) {
    // Record user corrections for learning
    AppState.learningData.corrections.push({
        timestamp: new Date().toISOString(),
        sheetId: sheetId,
        correctedTo: newState
    });

    // Keep last 500 corrections
    if (AppState.learningData.corrections.length > 500) {
        AppState.learningData.corrections = AppState.learningData.corrections.slice(-500);
    }

    localStorage.setItem('learningData', JSON.stringify(AppState.learningData));
}

// =============================================================================
// UI HELPERS
// =============================================================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px;">
            ${type === 'success' ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>' :
              type === 'error' ? '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>' :
              '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>'}
        </svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

window.closeModal = function() {
    document.getElementById('modal')?.classList.add('hidden');
};

window.showHelp = function() {
    const modal = document.getElementById('modal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');

    if (modal && title && body) {
        title.textContent = 'Help & Keyboard Shortcuts';
        body.innerHTML = `
            <div style="line-height: 1.8;">
                <h4 style="margin-bottom: 1rem; color: var(--accent);">Getting Started</h4>
                <p style="margin-bottom: 1rem; color: var(--text-secondary);">
                    Upload your roofing documents (PDFs) to analyze roof plans, assembly letters, and specifications.
                    The AI will automatically detect roof-related pages and extract key information.
                </p>

                <h4 style="margin-bottom: 1rem; color: var(--accent);">Document Types</h4>
                <ul style="color: var(--text-secondary); margin-bottom: 1.5rem; padding-left: 1.5rem;">
                    <li><strong>Architectural Drawings:</strong> Roof plans, details, sections</li>
                    <li><strong>Assembly Letters:</strong> Manufacturer system specifications</li>
                    <li><strong>Specifications:</strong> Division 07 specs</li>
                    <li><strong>Scope of Work:</strong> Project requirements</li>
                </ul>

                <h4 style="margin-bottom: 1rem; color: var(--accent);">Features</h4>
                <ul style="color: var(--text-secondary); padding-left: 1.5rem;">
                    <li>Smart filtering saves up to 90% on processing</li>
                    <li>Multi-layered detection with confidence scoring</li>
                    <li>DXF generation from assembly letters</li>
                    <li>Export to CSV</li>
                    <li>Project saving and management</li>
                </ul>
            </div>
        `;
        modal.classList.remove('hidden');
    }
};

console.log('Roofing Intelligence Platform v1.0 loaded');
