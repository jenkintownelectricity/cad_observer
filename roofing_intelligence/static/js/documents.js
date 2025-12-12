/**
 * ROOFIO Document Intelligence Center
 * Document management, versioning, and AI parsing
 */

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initDocumentStats();
    initDragAndDrop();
    console.log('Document Intelligence Center initialized');
});

// ============================================================================
// THEME
// ============================================================================

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// ============================================================================
// DOCUMENT STATS
// ============================================================================

function initDocumentStats() {
    // Count documents by state
    const allCards = document.querySelectorAll('.doc-card');
    const filledCards = document.querySelectorAll('.doc-card.filled');
    const parsedCards = document.querySelectorAll('.doc-card.parsed');
    const emptyCards = document.querySelectorAll('.doc-card.empty');

    document.getElementById('total-docs').textContent = filledCards.length;
    document.getElementById('parsed-docs').textContent = parsedCards.length;
    document.getElementById('missing-docs').textContent = emptyCards.length;
}

// ============================================================================
// PROJECT DOCUMENTS
// ============================================================================

function loadProjectDocuments(projectId) {
    if (!projectId) return;

    showToast(`Loading documents for project...`, 'info');

    // Simulate API call
    setTimeout(() => {
        showToast(`Documents loaded for ${projectId}`, 'success');
        initDocumentStats();
    }, 1000);
}

// ============================================================================
// DOCUMENT ACTIONS
// ============================================================================

function openDocument(docType) {
    const modal = document.getElementById('document-modal');
    const title = document.getElementById('doc-modal-title');
    const body = document.getElementById('doc-modal-body');

    const docData = getDocumentData(docType);

    title.textContent = docData.title;
    body.innerHTML = generateDocumentViewer(docData);

    modal.classList.remove('hidden');
}

function getDocumentData(docType) {
    const documents = {
        'contract': {
            title: 'Contract - JHU Library Roofing',
            type: 'contract',
            versions: [
                { version: 3, date: 'Dec 10, 2024', note: 'Final executed', status: 'current' },
                { version: 2, date: 'Dec 5, 2024', note: 'GC revisions', status: 'superseded' },
                { version: 1, date: 'Nov 28, 2024', note: 'Initial draft', status: 'superseded' }
            ],
            parsed: {
                'Contract Value': '$450,000.00',
                'Retainage': '10%',
                'Duration': '90 calendar days',
                'Start Date': 'December 15, 2024',
                'Liquidated Damages': '$500/day (FLAG)',
                'Insurance Required': '$2M General Liability',
                'Payment Terms': 'Net 30 from approval'
            },
            flags: [
                { type: 'warning', text: 'Liquidated damages clause: $500 per calendar day' },
                { type: 'warning', text: 'Flow-down clause references prime contract' },
                { type: 'info', text: 'Change order markup limited to 15%' }
            ]
        },
        'specs': {
            title: 'Specifications - 07 50 00 Membrane Roofing',
            type: 'specs',
            versions: [
                { version: 1, date: 'Dec 5, 2024', note: 'Bid set', status: 'current' }
            ],
            parsed: {
                'System Type': 'TPO 60 mil fully adhered',
                'Manufacturer': 'Carlisle SynTec',
                'Insulation': '2 layers polyiso R-30 min',
                'Attachment': 'Foam adhesive',
                'Cover Board': '1/2" DensDeck Prime',
                'Warranty': '20-year NDL required',
                'Wind Uplift': 'FM 1-90 minimum'
            },
            flags: []
        },
        'drawings': {
            title: 'Roof Plan - Sheet A-501',
            type: 'drawings',
            versions: [
                { version: 2, date: 'Dec 8, 2024', note: 'ASI #3 revision', status: 'current' },
                { version: 1, date: 'Nov 15, 2024', note: 'Bid set', status: 'superseded' }
            ],
            parsed: {
                'Total Roof Area': '45,000 SF',
                'Roof Drains': '12 primary + 4 overflow',
                'Coping': '850 LF aluminum',
                'RTUs': '24 units',
                'VTRs': '8 vent through roof',
                'Skylights': '4 units',
                'Roof Slope': '1/4":12"'
            },
            flags: [
                { type: 'info', text: 'ASI #3 added 2 roof drains at grid C-4' }
            ]
        },
        'assembly-letter': {
            title: 'Assembly Letter - Carlisle SureWeld TPO',
            type: 'assembly',
            versions: [
                { version: 1, date: 'Dec 9, 2024', note: 'Approved', status: 'current' }
            ],
            parsed: {
                'H1 - Membrane': 'Carlisle SureWeld 60 mil TPO White',
                'H2 - Substrate': 'Metal deck, mechanically attached',
                'H3 - Thermal Barrier': '1/2" DensDeck attached 32/16/8',
                'H4 - Insulation Layer 1': '2.6" Polyiso in foam adhesive 12/6/4',
                'H5 - Insulation Layer 2': '2.6" Polyiso in foam adhesive 12/6/4',
                'H6 - Cover Board': '5/8" DensDeck Prime in foam adhesive',
                'H7 - Membrane Attachment': 'Fully adhered with LVOC bonding adhesive'
            },
            flags: []
        },
        'sov': {
            title: 'Schedule of Values',
            type: 'sov',
            versions: [
                { version: 1, date: 'Dec 3, 2024', note: 'Approved', status: 'current' }
            ],
            parsed: {
                'Total Contract': '$450,000.00',
                'Mobilization': '$22,500.00 (5%)',
                'Tear-off': '$45,000.00 (10%)',
                'Insulation': '$112,500.00 (25%)',
                'Membrane': '$157,500.00 (35%)',
                'Sheet Metal': '$67,500.00 (15%)',
                'Closeout': '$45,000.00 (10%)',
                'Billed to Date': '$324,000.00 (72%)',
                'Retainage Held': '$32,400.00'
            },
            flags: []
        },
        'daily-reports': {
            title: 'Daily Reports Summary',
            type: 'daily',
            versions: [],
            parsed: {
                'Total Reports': '47',
                'SF Completed': '32,400 SF (72%)',
                'Total Man-Hours': '2,340',
                'Average Crew Size': '6 workers',
                'Weather Delay Days': '4',
                'Safety Incidents': '0'
            },
            flags: [
                { type: 'info', text: '4 weather delays documented for delay claim' }
            ]
        },
        'rfis': {
            title: 'RFIs',
            type: 'rfi',
            versions: [],
            parsed: {
                'Total RFIs': '8',
                'Open': '2',
                'Closed': '6',
                'Average Response Time': '3.2 days'
            },
            flags: [
                { type: 'warning', text: 'RFI #7: Drain location conflict - awaiting response 3 days' },
                { type: 'warning', text: 'RFI #8: Coping height clarification - awaiting response 1 day' }
            ]
        },
        'change-orders': {
            title: 'Change Orders',
            type: 'co',
            versions: [],
            parsed: {
                'Total COs': '2',
                'Total Value': '$18,500.00',
                'CO #1': 'Add drain at grid C-4 - $8,500',
                'CO #2': 'Coping upgrade to .050 aluminum - $10,000',
                'Net Schedule Impact': '+2 days'
            },
            flags: []
        }
    };

    return documents[docType] || {
        title: docType,
        type: docType,
        versions: [],
        parsed: {},
        flags: []
    };
}

function generateDocumentViewer(docData) {
    let versionsHtml = '';
    if (docData.versions.length > 0) {
        versionsHtml = `
            <div class="doc-viewer-section">
                <h4>Version History</h4>
                <div class="version-list">
                    ${docData.versions.map(v => `
                        <div class="version-item ${v.status}">
                            <div class="version-info">
                                <span class="version-number">v${v.version}</span>
                                <span class="version-date">${v.date}</span>
                                <span class="version-note">${v.note}</span>
                            </div>
                            <div class="version-actions">
                                ${v.status === 'current' ? '<span class="badge current">Current</span>' : '<button class="btn-link">View</button>'}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    let parsedHtml = '';
    if (Object.keys(docData.parsed).length > 0) {
        parsedHtml = `
            <div class="doc-viewer-section">
                <h4>AI Extracted Data</h4>
                <div class="parsed-data-grid">
                    ${Object.entries(docData.parsed).map(([key, value]) => `
                        <div class="parsed-row">
                            <span class="parsed-key">${key}</span>
                            <span class="parsed-value ${value.includes('FLAG') ? 'flagged' : ''}">${value}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    let flagsHtml = '';
    if (docData.flags.length > 0) {
        flagsHtml = `
            <div class="doc-viewer-section">
                <h4>AI Flags & Notes</h4>
                <div class="flags-list">
                    ${docData.flags.map(f => `
                        <div class="flag-item ${f.type}">
                            <span class="flag-icon">${f.type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                            <span class="flag-text">${f.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    return `
        <div class="doc-viewer">
            <div class="doc-viewer-actions">
                <button class="btn-secondary" onclick="viewOriginalDocument('${docData.type}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                    View Original
                </button>
                <button class="btn-secondary" onclick="downloadDocument('${docData.type}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download
                </button>
                <button class="btn-primary" onclick="reparseDocument('${docData.type}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                    </svg>
                    Re-parse
                </button>
            </div>
            ${flagsHtml}
            ${parsedHtml}
            ${versionsHtml}
        </div>
    `;
}

function viewOriginalDocument(docType) {
    showToast('Opening original document...', 'info');
}

function downloadDocument(docType) {
    showToast('Preparing download...', 'info');
}

function reparseDocument(docType) {
    showToast('Re-parsing document with AI...', 'info');
    setTimeout(() => {
        showToast('Document re-parsed successfully!', 'success');
    }, 2000);
}

// ============================================================================
// PARSING
// ============================================================================

function parseDocument(docType) {
    const card = document.querySelector(`[data-doc-type="${docType}"]`);
    if (card) {
        card.classList.add('parsing');
    }

    showToast(`AI parsing ${docType}...`, 'info');

    // Simulate parsing
    setTimeout(() => {
        if (card) {
            card.classList.remove('parsing');
            card.classList.add('parsed');

            // Add sample parsed data
            const parsedData = document.createElement('div');
            parsedData.className = 'doc-parsed-data';
            parsedData.innerHTML = `
                <div class="parsed-item"><strong>Status:</strong> Parsed successfully</div>
                <div class="parsed-item"><strong>Extracted:</strong> 12 key fields</div>
            `;
            card.appendChild(parsedData);

            // Update the parse button to show parsed status
            const parseBtn = card.querySelector('.parse-btn');
            if (parseBtn) {
                parseBtn.outerHTML = '<span class="status-badge parsed">AI Parsed</span>';
            }
        }

        showToast(`${docType} parsed successfully!`, 'success');
        initDocumentStats();
    }, 2500);
}

// ============================================================================
// UPLOAD
// ============================================================================

function uploadDocument(docType) {
    const modal = document.getElementById('upload-modal');
    const title = document.getElementById('upload-modal-title');

    title.textContent = `Upload ${formatDocType(docType)}`;
    modal.classList.remove('hidden');

    // Store current doc type for processing
    modal.dataset.docType = docType;
}

function openUploadModal() {
    const modal = document.getElementById('upload-modal');
    document.getElementById('upload-modal-title').textContent = 'Upload Document';
    modal.classList.remove('hidden');
}

function processUpload() {
    const fileInput = document.getElementById('file-input');
    const autoParse = document.getElementById('auto-parse').checked;
    const modal = document.getElementById('upload-modal');
    const docType = modal.dataset.docType;

    if (fileInput.files.length === 0) {
        showToast('Please select a file to upload', 'warning');
        return;
    }

    showToast('Uploading document...', 'info');

    // Simulate upload
    setTimeout(() => {
        closeModal('upload-modal');
        showToast('Document uploaded successfully!', 'success');

        // Update the card state
        if (docType) {
            const card = document.querySelector(`[data-doc-type="${docType}"]`);
            if (card) {
                card.classList.remove('empty');
                card.classList.add('filled');
                // Update card content
                const docIcon = card.querySelector('.doc-icon');
                if (docIcon) {
                    docIcon.classList.remove('empty');
                    docIcon.classList.add(docType);
                }
            }
        }

        if (autoParse && docType) {
            setTimeout(() => parseDocument(docType), 500);
        }

        initDocumentStats();
    }, 1500);
}

function formatDocType(type) {
    return type.split('-').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// ============================================================================
// DRAG AND DROP
// ============================================================================

function initDragAndDrop() {
    const uploadArea = document.querySelector('.upload-area');
    if (!uploadArea) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    uploadArea.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    e.currentTarget.classList.add('highlight');
}

function unhighlight(e) {
    e.currentTarget.classList.remove('highlight');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    document.getElementById('file-input').files = files;
}

// ============================================================================
// CATEGORY TOGGLE
// ============================================================================

function toggleCategory(btn) {
    const category = btn.closest('.doc-category');
    category.classList.toggle('collapsed');
}

// ============================================================================
// PARSER MARKETPLACE
// ============================================================================

function openParserMarketplace() {
    document.getElementById('parser-modal').classList.remove('hidden');
}

function purchaseParser(parserId) {
    showToast(`Processing purchase for ${parserId}...`, 'info');
    setTimeout(() => {
        showToast('Parser skill purchased! It\'s now active.', 'success');
        closeModal('parser-modal');
    }, 1500);
}

function requestCustomParser() {
    showToast('Opening custom parser request form...', 'info');
    closeModal('parser-modal');
}

// ============================================================================
// MODAL UTILITIES
// ============================================================================

function closeModal(modalId) {
    document.getElementById(modalId)?.classList.add('hidden');
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.add('hidden');
    }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }
});

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
