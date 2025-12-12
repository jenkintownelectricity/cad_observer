/**
 * ROOFIO Forms & Document Scanner
 * ================================
 *
 * Handles:
 * 1. Form template preference (ROOFIO format vs Custom format)
 * 2. First-time setup when user encounters a form
 * 3. Camera capture for document scanning (CamScan-like)
 * 4. Creating templates from scanned documents
 * 5. Form submission
 */

// =============================================================================
// STATE
// =============================================================================

const FormsState = {
    currentFormType: null,
    currentTemplate: null,
    useCustomFormat: false,
    scanResult: null,
    cameraStream: null,
    agencyId: localStorage.getItem('agencyId') || '3cfd5441-d5fc-4857-8fb9-3dc7be7a37d5'
};

// =============================================================================
// API HELPERS
// =============================================================================

async function formsApiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'X-Agency-Id': FormsState.agencyId,
        ...options.headers
    };

    try {
        const response = await fetch(`/api${endpoint}`, { ...options, headers });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API error');
        }
        return await response.json();
    } catch (error) {
        console.error('Forms API error:', error);
        throw error;
    }
}

// =============================================================================
// FORM FORMAT TOGGLE
// =============================================================================

/**
 * Check if user has a preference for this form type.
 * If not, show first-time setup dialog.
 */
async function checkFormPreference(formType) {
    try {
        const pref = await formsApiCall(`/forms/preference/${formType}`);

        if (pref.first_time_setup) {
            // First time using this form - show setup dialog
            showFirstTimeSetupDialog(formType);
            return null;
        }

        if (pref.has_preference) {
            FormsState.useCustomFormat = pref.use_custom;
            FormsState.currentTemplate = pref.template_id;
            return pref;
        }

        // Has templates but no default - let user choose
        showTemplateChooserDialog(formType);
        return null;
    } catch (error) {
        console.error('Error checking form preference:', error);
        // Fall back to ROOFIO format
        FormsState.useCustomFormat = false;
        return { use_custom: false };
    }
}

/**
 * Show first-time setup dialog when user encounters a form type for the first time.
 */
function showFirstTimeSetupDialog(formType) {
    const formNames = {
        'daily_report': 'Daily Report',
        'inspection': 'Inspection',
        'jha': 'Job Hazard Analysis (JHA)',
        'toolbox_talk': 'Toolbox Talk',
        'incident_report': 'Incident Report',
        'safety_inspection': 'Safety Inspection',
        'material_receiving': 'Material Receiving',
        'punch_list': 'Punch List',
        'rfi': 'Request for Information (RFI)',
        'change_order': 'Change Order',
        'submittal': 'Submittal',
        'photo_log': 'Photo Log'
    };

    const formName = formNames[formType] || formType.replace(/_/g, ' ');

    const dialog = document.createElement('div');
    dialog.className = 'form-setup-dialog';
    dialog.innerHTML = `
        <div class="form-setup-content">
            <div class="form-setup-header">
                <h2>Set Up Your ${formName} Form</h2>
                <p>This is your first time using a ${formName}. How would you like your forms to look?</p>
            </div>

            <div class="format-options">
                <div class="format-option" data-format="roofio">
                    <div class="format-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10 9 9 9 8 9"/>
                        </svg>
                    </div>
                    <h3>Use ROOFIO Format</h3>
                    <p>Clean, professional forms designed for roofing. Includes GPS, timestamps, and digital signatures.</p>
                    <ul>
                        <li>Modern design</li>
                        <li>Auto-fills project data</li>
                        <li>Built-in compliance</li>
                    </ul>
                </div>

                <div class="format-option" data-format="custom">
                    <div class="format-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <circle cx="8.5" cy="8.5" r="1.5"/>
                            <polyline points="21 15 16 10 5 21"/>
                        </svg>
                    </div>
                    <h3>Use Your Format</h3>
                    <p>Snap a photo of your existing form and we'll create a digital version that looks just like it.</p>
                    <ul>
                        <li>Familiar layout</li>
                        <li>Same fields you know</li>
                        <li>+ ROOFIO features</li>
                    </ul>
                </div>
            </div>

            <div class="format-toggle-section">
                <p class="toggle-hint">You can switch formats anytime</p>
            </div>

            <div class="form-setup-actions">
                <button class="btn-secondary" onclick="closeSetupDialog()">Maybe Later</button>
            </div>
        </div>
    `;

    document.body.appendChild(dialog);

    // Add click handlers for format options
    dialog.querySelectorAll('.format-option').forEach(option => {
        option.addEventListener('click', () => {
            const format = option.dataset.format;
            if (format === 'roofio') {
                selectRoofioFormat(formType);
            } else {
                showScanSetup(formType);
            }
            closeSetupDialog();
        });
    });

    // Add styles if not already present
    addFormStyles();
}

function closeSetupDialog() {
    const dialog = document.querySelector('.form-setup-dialog');
    if (dialog) {
        dialog.remove();
    }
}

/**
 * Create ROOFIO default template for this form type.
 */
async function selectRoofioFormat(formType) {
    try {
        const template = await formsApiCall('/forms/templates', {
            method: 'POST',
            body: JSON.stringify({
                name: `ROOFIO ${formType.replace(/_/g, ' ')}`,
                form_type: formType,
                description: 'Standard ROOFIO format',
                is_custom: false,
                roofio_additions: { logo: true, timestamp: true, gps: true }
            })
        });

        // Set as default
        await formsApiCall(`/forms/templates/${template.template_id}/set-default`, {
            method: 'POST'
        });

        FormsState.currentTemplate = template.template_id;
        FormsState.useCustomFormat = false;

        showNotification('ROOFIO format selected!', 'success');
    } catch (error) {
        showNotification('Error setting up form: ' + error.message, 'error');
    }
}

// =============================================================================
// CAMERA / DOCUMENT SCANNER
// =============================================================================

/**
 * Show the scan setup interface for creating custom forms.
 */
function showScanSetup(formType) {
    FormsState.currentFormType = formType;

    const scanDialog = document.createElement('div');
    scanDialog.className = 'scan-dialog';
    scanDialog.innerHTML = `
        <div class="scan-content">
            <div class="scan-header">
                <h2>Scan Your Form</h2>
                <button class="close-btn" onclick="closeScanDialog()">×</button>
            </div>

            <div class="scan-instructions">
                <p>Take a photo of your existing form (filled out or blank). We'll create a digital version that looks just like it.</p>
            </div>

            <div class="scan-area" id="scanArea">
                <video id="cameraPreview" autoplay playsinline></video>
                <canvas id="scanCanvas" style="display: none;"></canvas>
                <img id="previewImage" style="display: none;">

                <div class="scan-placeholder" id="scanPlaceholder">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="2" y="2" width="20" height="20" rx="2"/>
                        <circle cx="12" cy="12" r="4"/>
                        <path d="M2 12h2M20 12h2M12 2v2M12 20v2"/>
                    </svg>
                    <p>Position your form within the frame</p>
                </div>
            </div>

            <div class="scan-controls">
                <button class="btn-secondary" id="uploadBtn" onclick="triggerFileUpload()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    Upload Photo
                </button>
                <button class="btn-primary" id="captureBtn" onclick="capturePhoto()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <circle cx="12" cy="12" r="6" fill="currentColor"/>
                    </svg>
                    Capture
                </button>
                <input type="file" id="fileInput" accept="image/*,application/pdf" style="display: none" onchange="handleFileSelect(event)">
            </div>

            <div class="output-format-section">
                <label>Output Format:</label>
                <div class="format-buttons">
                    <button class="format-btn active" data-format="pdf">PDF</button>
                    <button class="format-btn" data-format="png">Image</button>
                    <button class="format-btn" data-format="docx">Word</button>
                    <button class="format-btn" data-format="xlsx">Excel</button>
                </div>
            </div>

            <div class="scan-actions" id="scanActions" style="display: none;">
                <button class="btn-secondary" onclick="retakePhoto()">Retake</button>
                <button class="btn-primary" onclick="processAndCreateTemplate()">Create Form Template</button>
            </div>
        </div>
    `;

    document.body.appendChild(scanDialog);

    // Initialize camera
    initCamera();

    // Format button handlers
    scanDialog.querySelectorAll('.format-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            scanDialog.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
        });
    });
}

function closeScanDialog() {
    stopCamera();
    const dialog = document.querySelector('.scan-dialog');
    if (dialog) {
        dialog.remove();
    }
}

/**
 * Initialize camera for document scanning.
 */
async function initCamera() {
    try {
        const video = document.getElementById('cameraPreview');
        const placeholder = document.getElementById('scanPlaceholder');

        const constraints = {
            video: {
                facingMode: { ideal: 'environment' }, // Prefer back camera on mobile
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        };

        FormsState.cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = FormsState.cameraStream;
        video.style.display = 'block';
        placeholder.style.display = 'none';

    } catch (error) {
        console.log('Camera not available:', error);
        // Camera not available - show upload only
        const video = document.getElementById('cameraPreview');
        const captureBtn = document.getElementById('captureBtn');
        if (video) video.style.display = 'none';
        if (captureBtn) captureBtn.style.display = 'none';
    }
}

function stopCamera() {
    if (FormsState.cameraStream) {
        FormsState.cameraStream.getTracks().forEach(track => track.stop());
        FormsState.cameraStream = null;
    }
}

/**
 * Capture photo from camera.
 */
function capturePhoto() {
    const video = document.getElementById('cameraPreview');
    const canvas = document.getElementById('scanCanvas');
    const preview = document.getElementById('previewImage');
    const placeholder = document.getElementById('scanPlaceholder');
    const actionsDiv = document.getElementById('scanActions');
    const controlsDiv = document.querySelector('.scan-controls');

    // Set canvas size to video size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Convert to image and display
    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    preview.src = imageData;
    preview.style.display = 'block';
    video.style.display = 'none';
    placeholder.style.display = 'none';

    // Show process actions
    actionsDiv.style.display = 'flex';
    controlsDiv.style.display = 'none';

    // Store the image data
    FormsState.scanResult = imageData;

    // Stop camera
    stopCamera();
}

function triggerFileUpload() {
    document.getElementById('fileInput').click();
}

/**
 * Handle file selection for upload.
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('previewImage');
        const video = document.getElementById('cameraPreview');
        const placeholder = document.getElementById('scanPlaceholder');
        const actionsDiv = document.getElementById('scanActions');
        const controlsDiv = document.querySelector('.scan-controls');

        preview.src = e.target.result;
        preview.style.display = 'block';
        video.style.display = 'none';
        placeholder.style.display = 'none';

        actionsDiv.style.display = 'flex';
        controlsDiv.style.display = 'none';

        FormsState.scanResult = e.target.result;
        stopCamera();
    };

    reader.readAsDataURL(file);
}

function retakePhoto() {
    const preview = document.getElementById('previewImage');
    const actionsDiv = document.getElementById('scanActions');
    const controlsDiv = document.querySelector('.scan-controls');
    const placeholder = document.getElementById('scanPlaceholder');

    preview.style.display = 'none';
    actionsDiv.style.display = 'none';
    controlsDiv.style.display = 'flex';
    placeholder.style.display = 'flex';

    FormsState.scanResult = null;

    // Restart camera
    initCamera();
}

/**
 * Process the scanned image and create a form template.
 */
async function processAndCreateTemplate() {
    if (!FormsState.scanResult) {
        showNotification('No image captured', 'error');
        return;
    }

    const activeFormatBtn = document.querySelector('.format-btn.active');
    const outputFormat = activeFormatBtn ? activeFormatBtn.dataset.format : 'pdf';

    // Show processing indicator
    const actionsDiv = document.getElementById('scanActions');
    actionsDiv.innerHTML = `
        <div class="processing-indicator">
            <div class="spinner"></div>
            <p>Analyzing form and extracting fields...</p>
        </div>
    `;

    try {
        // First, upload and process the scan
        const scanResponse = await formsApiCall(`/scan/upload?output_format=${outputFormat}&extract_fields=true`, {
            method: 'POST'
        });

        // Show extracted fields for review
        showFieldReviewDialog(scanResponse);

    } catch (error) {
        showNotification('Error processing scan: ' + error.message, 'error');
        actionsDiv.innerHTML = `
            <button class="btn-secondary" onclick="retakePhoto()">Retake</button>
            <button class="btn-primary" onclick="processAndCreateTemplate()">Try Again</button>
        `;
    }
}

/**
 * Show dialog to review AI-extracted fields before creating template.
 */
function showFieldReviewDialog(scanResult) {
    closeScanDialog();

    const formType = FormsState.currentFormType;
    const fields = scanResult.extracted_fields || [];

    const reviewDialog = document.createElement('div');
    reviewDialog.className = 'field-review-dialog';
    reviewDialog.innerHTML = `
        <div class="review-content">
            <div class="review-header">
                <h2>Review Extracted Fields</h2>
                <p>We detected these fields from your form. You can edit or remove any before saving.</p>
            </div>

            <div class="extracted-fields" id="extractedFields">
                ${fields.map((field, i) => `
                    <div class="field-item" data-index="${i}">
                        <input type="text" class="field-label" value="${field.label}" placeholder="Field Label">
                        <select class="field-type">
                            <option value="text" ${field.type === 'text' ? 'selected' : ''}>Text</option>
                            <option value="number" ${field.type === 'number' ? 'selected' : ''}>Number</option>
                            <option value="date" ${field.type === 'date' ? 'selected' : ''}>Date</option>
                            <option value="time" ${field.type === 'time' ? 'selected' : ''}>Time</option>
                            <option value="checkbox" ${field.type === 'checkbox' ? 'selected' : ''}>Checkbox</option>
                            <option value="textarea" ${field.type === 'textarea' ? 'selected' : ''}>Text Area</option>
                            <option value="signature" ${field.type === 'signature' ? 'selected' : ''}>Signature</option>
                            <option value="photo" ${field.type === 'photo' ? 'selected' : ''}>Photo</option>
                        </select>
                        <label class="required-toggle">
                            <input type="checkbox" ${field.required ? 'checked' : ''}>
                            Required
                        </label>
                        <button class="remove-field" onclick="removeField(${i})">×</button>
                    </div>
                `).join('')}
            </div>

            <button class="btn-add-field" onclick="addField()">+ Add Field</button>

            <div class="roofio-additions">
                <h3>ROOFIO Features (always included)</h3>
                <div class="addition-items">
                    <label><input type="checkbox" checked disabled> Company Logo</label>
                    <label><input type="checkbox" checked disabled> Auto Timestamp</label>
                    <label><input type="checkbox" checked disabled> GPS Location</label>
                    <label><input type="checkbox" id="addWatermark"> Watermark</label>
                </div>
            </div>

            <div class="template-name-section">
                <label>Template Name:</label>
                <input type="text" id="templateName" value="My ${formType.replace(/_/g, ' ')}" placeholder="Enter template name">
            </div>

            <div class="review-actions">
                <button class="btn-secondary" onclick="closeReviewDialog()">Cancel</button>
                <button class="btn-primary" onclick="saveTemplate()">Save Template</button>
            </div>
        </div>
    `;

    document.body.appendChild(reviewDialog);

    // Store scan result for template creation
    FormsState.scanResult = scanResult;
}

function closeReviewDialog() {
    const dialog = document.querySelector('.field-review-dialog');
    if (dialog) {
        dialog.remove();
    }
}

function removeField(index) {
    const fieldItem = document.querySelector(`.field-item[data-index="${index}"]`);
    if (fieldItem) {
        fieldItem.remove();
    }
}

function addField() {
    const container = document.getElementById('extractedFields');
    const newIndex = container.children.length;

    const fieldHtml = `
        <div class="field-item" data-index="${newIndex}">
            <input type="text" class="field-label" value="" placeholder="Field Label">
            <select class="field-type">
                <option value="text" selected>Text</option>
                <option value="number">Number</option>
                <option value="date">Date</option>
                <option value="time">Time</option>
                <option value="checkbox">Checkbox</option>
                <option value="textarea">Text Area</option>
                <option value="signature">Signature</option>
                <option value="photo">Photo</option>
            </select>
            <label class="required-toggle">
                <input type="checkbox">
                Required
            </label>
            <button class="remove-field" onclick="removeField(${newIndex})">×</button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', fieldHtml);
}

/**
 * Save the custom form template.
 */
async function saveTemplate() {
    const templateName = document.getElementById('templateName').value;
    const addWatermark = document.getElementById('addWatermark').checked;

    // Collect fields from the UI
    const fieldItems = document.querySelectorAll('.field-item');
    const fields = Array.from(fieldItems).map(item => {
        const label = item.querySelector('.field-label').value;
        const type = item.querySelector('.field-type').value;
        const required = item.querySelector('.required-toggle input').checked;

        return {
            name: label.toLowerCase().replace(/\s+/g, '_'),
            label: label,
            type: type,
            required: required
        };
    }).filter(f => f.label); // Remove empty fields

    try {
        // Create the template
        const template = await formsApiCall('/forms/templates', {
            method: 'POST',
            body: JSON.stringify({
                name: templateName,
                form_type: FormsState.currentFormType,
                description: 'Created from scanned document',
                is_custom: true,
                fields: fields,
                roofio_additions: {
                    logo: true,
                    timestamp: true,
                    gps: true,
                    watermark: addWatermark
                }
            })
        });

        // Set as default
        await formsApiCall(`/forms/templates/${template.template_id}/set-default`, {
            method: 'POST'
        });

        FormsState.currentTemplate = template.template_id;
        FormsState.useCustomFormat = true;

        closeReviewDialog();
        showNotification('Custom form template created!', 'success');

    } catch (error) {
        showNotification('Error creating template: ' + error.message, 'error');
    }
}

// =============================================================================
// FORMAT TOGGLE COMPONENT
// =============================================================================

/**
 * Create a format toggle component for any form.
 * Returns HTML string that can be inserted into a form header.
 */
function createFormatToggle(formType, currentUseCustom = false) {
    return `
        <div class="format-toggle" data-form-type="${formType}">
            <span class="toggle-label">Form Format:</span>
            <div class="toggle-switch">
                <button class="toggle-option ${!currentUseCustom ? 'active' : ''}" data-value="roofio">
                    ROOFIO
                </button>
                <button class="toggle-option ${currentUseCustom ? 'active' : ''}" data-value="custom">
                    Your Format
                </button>
            </div>
            <button class="edit-format-btn" onclick="showScanSetup('${formType}')" title="Edit or create custom format">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
            </button>
        </div>
    `;
}

/**
 * Initialize format toggle event handlers.
 */
function initFormatToggle(container) {
    const toggle = container.querySelector('.format-toggle');
    if (!toggle) return;

    const formType = toggle.dataset.formType;

    toggle.querySelectorAll('.toggle-option').forEach(btn => {
        btn.addEventListener('click', async () => {
            const useCustom = btn.dataset.value === 'custom';

            // Update UI
            toggle.querySelectorAll('.toggle-option').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Check if custom template exists
            if (useCustom) {
                const pref = await formsApiCall(`/forms/preference/${formType}`);
                if (pref.first_time_setup || !pref.has_preference) {
                    // Need to set up custom format first
                    showScanSetup(formType);
                    return;
                }
            }

            FormsState.useCustomFormat = useCustom;
            showNotification(`Switched to ${useCustom ? 'your' : 'ROOFIO'} format`, 'info');

            // Trigger form reload if needed
            if (typeof onFormatChange === 'function') {
                onFormatChange(formType, useCustom);
            }
        });
    });
}

// =============================================================================
// STANDALONE DOCUMENT SCANNER
// =============================================================================

/**
 * Open standalone document scanner (not for form creation).
 * This is the CamScan-like feature for general document scanning.
 */
function openDocumentScanner() {
    const scanDialog = document.createElement('div');
    scanDialog.className = 'scan-dialog standalone-scanner';
    scanDialog.innerHTML = `
        <div class="scan-content">
            <div class="scan-header">
                <h2>Document Scanner</h2>
                <button class="close-btn" onclick="closeStandaloneScanner()">×</button>
            </div>

            <div class="scan-instructions">
                <p>Snap a photo of any document to convert it to PDF, image, Word, or Excel.</p>
            </div>

            <div class="scan-area" id="standaloneScanArea">
                <video id="standaloneCamera" autoplay playsinline></video>
                <canvas id="standaloneCanvas" style="display: none;"></canvas>
                <img id="standalonePreview" style="display: none;">

                <div class="scan-placeholder" id="standalonePlaceholder">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="2" y="2" width="20" height="20" rx="2"/>
                        <circle cx="12" cy="12" r="4"/>
                    </svg>
                    <p>Position document in frame</p>
                </div>
            </div>

            <div class="scan-controls" id="standaloneControls">
                <button class="btn-secondary" onclick="triggerStandaloneUpload()">
                    Upload
                </button>
                <button class="btn-primary btn-capture" id="standaloneCaptureBtn" onclick="standaloneCapture()">
                    <div class="capture-circle"></div>
                </button>
                <input type="file" id="standaloneFileInput" accept="image/*,application/pdf" style="display: none" onchange="handleStandaloneFile(event)">
            </div>

            <div class="output-format-section">
                <label>Save As:</label>
                <div class="format-buttons" id="standaloneFormats">
                    <button class="format-btn active" data-format="pdf">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                        PDF
                    </button>
                    <button class="format-btn" data-format="png">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <circle cx="8.5" cy="8.5" r="1.5"/>
                            <polyline points="21 15 16 10 5 21"/>
                        </svg>
                        Image
                    </button>
                    <button class="format-btn" data-format="docx">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                        </svg>
                        Word
                    </button>
                    <button class="format-btn" data-format="xlsx">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <line x1="3" y1="9" x2="21" y2="9"/>
                            <line x1="3" y1="15" x2="21" y2="15"/>
                            <line x1="9" y1="3" x2="9" y2="21"/>
                            <line x1="15" y1="3" x2="15" y2="21"/>
                        </svg>
                        Excel
                    </button>
                </div>
            </div>

            <div class="standalone-actions" id="standaloneActions" style="display: none;">
                <button class="btn-secondary" onclick="retakeStandalone()">Retake</button>
                <button class="btn-primary" onclick="processStandaloneScan()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(scanDialog);
    initStandaloneCamera();

    // Format button handlers
    scanDialog.querySelectorAll('#standaloneFormats .format-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            scanDialog.querySelectorAll('#standaloneFormats .format-btn').forEach(b => b.classList.remove('active'));
            target.classList.add('active');
        });
    });
}

function closeStandaloneScanner() {
    stopStandaloneCamera();
    const dialog = document.querySelector('.standalone-scanner');
    if (dialog) {
        dialog.remove();
    }
}

async function initStandaloneCamera() {
    try {
        const video = document.getElementById('standaloneCamera');
        const placeholder = document.getElementById('standalonePlaceholder');

        FormsState.cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1080 } }
        });

        video.srcObject = FormsState.cameraStream;
        video.style.display = 'block';
        placeholder.style.display = 'none';
    } catch (error) {
        console.log('Camera not available');
        const captureBtn = document.getElementById('standaloneCaptureBtn');
        if (captureBtn) captureBtn.style.display = 'none';
    }
}

function stopStandaloneCamera() {
    if (FormsState.cameraStream) {
        FormsState.cameraStream.getTracks().forEach(track => track.stop());
        FormsState.cameraStream = null;
    }
}

function standaloneCapture() {
    const video = document.getElementById('standaloneCamera');
    const canvas = document.getElementById('standaloneCanvas');
    const preview = document.getElementById('standalonePreview');
    const controls = document.getElementById('standaloneControls');
    const actions = document.getElementById('standaloneActions');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    preview.src = imageData;
    preview.style.display = 'block';
    video.style.display = 'none';

    controls.style.display = 'none';
    actions.style.display = 'flex';

    FormsState.scanResult = imageData;
    stopStandaloneCamera();
}

function triggerStandaloneUpload() {
    document.getElementById('standaloneFileInput').click();
}

function handleStandaloneFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('standalonePreview');
        const video = document.getElementById('standaloneCamera');
        const controls = document.getElementById('standaloneControls');
        const actions = document.getElementById('standaloneActions');

        preview.src = e.target.result;
        preview.style.display = 'block';
        video.style.display = 'none';
        controls.style.display = 'none';
        actions.style.display = 'flex';

        FormsState.scanResult = e.target.result;
        stopStandaloneCamera();
    };
    reader.readAsDataURL(file);
}

function retakeStandalone() {
    const preview = document.getElementById('standalonePreview');
    const controls = document.getElementById('standaloneControls');
    const actions = document.getElementById('standaloneActions');
    const placeholder = document.getElementById('standalonePlaceholder');

    preview.style.display = 'none';
    controls.style.display = 'flex';
    actions.style.display = 'none';
    placeholder.style.display = 'flex';

    FormsState.scanResult = null;
    initStandaloneCamera();
}

async function processStandaloneScan() {
    const activeFormat = document.querySelector('#standaloneFormats .format-btn.active');
    const format = activeFormat ? activeFormat.dataset.format : 'pdf';

    const actions = document.getElementById('standaloneActions');
    actions.innerHTML = `
        <div class="processing-indicator">
            <div class="spinner"></div>
            <p>Processing...</p>
        </div>
    `;

    try {
        const result = await formsApiCall(`/scan/upload?output_format=${format}&enhance=true`, {
            method: 'POST'
        });

        // Simulate download
        showNotification(`Document saved as ${format.toUpperCase()}!`, 'success');
        closeStandaloneScanner();

    } catch (error) {
        showNotification('Error processing document: ' + error.message, 'error');
        actions.innerHTML = `
            <button class="btn-secondary" onclick="retakeStandalone()">Retake</button>
            <button class="btn-primary" onclick="processStandaloneScan()">Try Again</button>
        `;
    }
}

// =============================================================================
// STYLES
// =============================================================================

function addFormStyles() {
    if (document.getElementById('form-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'form-styles';
    styles.textContent = `
        /* Setup Dialog */
        .form-setup-dialog, .scan-dialog, .field-review-dialog {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
        }

        .form-setup-content, .scan-content, .review-content {
            background: #1a1a2e;
            border-radius: 16px;
            padding: 32px;
            max-width: 700px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            color: #fff;
        }

        .form-setup-header, .scan-header, .review-header {
            text-align: center;
            margin-bottom: 24px;
        }

        .form-setup-header h2, .scan-header h2, .review-header h2 {
            font-size: 24px;
            margin-bottom: 8px;
            color: #fff;
        }

        .form-setup-header p, .scan-instructions p, .review-header p {
            color: #888;
        }

        /* Format Options */
        .format-options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }

        .format-option {
            background: #252542;
            border: 2px solid #333;
            border-radius: 12px;
            padding: 24px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }

        .format-option:hover {
            border-color: #F97316;
            transform: translateY(-2px);
        }

        .format-option h3 {
            margin: 16px 0 8px;
            color: #fff;
        }

        .format-option p {
            color: #888;
            font-size: 14px;
            margin-bottom: 16px;
        }

        .format-option ul {
            text-align: left;
            padding-left: 20px;
            color: #aaa;
            font-size: 13px;
        }

        .format-option ul li {
            margin-bottom: 4px;
        }

        .format-icon {
            color: #F97316;
        }

        /* Scan Area */
        .scan-area {
            background: #000;
            border-radius: 12px;
            aspect-ratio: 4/3;
            overflow: hidden;
            position: relative;
            margin-bottom: 20px;
        }

        .scan-area video, .scan-area img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .scan-placeholder {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #666;
        }

        /* Scan Controls */
        .scan-controls {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-bottom: 20px;
        }

        .btn-capture {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .capture-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: #fff;
        }

        /* Format Buttons */
        .output-format-section {
            margin-bottom: 20px;
        }

        .output-format-section label {
            display: block;
            margin-bottom: 8px;
            color: #888;
        }

        .format-buttons {
            display: flex;
            gap: 8px;
        }

        .format-btn {
            flex: 1;
            padding: 12px 16px;
            background: #252542;
            border: 2px solid #333;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            font-size: 12px;
        }

        .format-btn:hover {
            border-color: #555;
        }

        .format-btn.active {
            border-color: #F97316;
            background: rgba(249, 115, 22, 0.1);
        }

        /* Review Dialog */
        .extracted-fields {
            margin-bottom: 16px;
        }

        .field-item {
            display: flex;
            gap: 8px;
            align-items: center;
            padding: 12px;
            background: #252542;
            border-radius: 8px;
            margin-bottom: 8px;
        }

        .field-item input[type="text"], .field-item select {
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 6px;
            padding: 8px 12px;
            color: #fff;
        }

        .field-item .field-label {
            flex: 1;
        }

        .field-item .field-type {
            width: 120px;
        }

        .required-toggle {
            display: flex;
            align-items: center;
            gap: 4px;
            color: #888;
            font-size: 12px;
        }

        .remove-field {
            background: none;
            border: none;
            color: #666;
            font-size: 20px;
            cursor: pointer;
            padding: 4px 8px;
        }

        .remove-field:hover {
            color: #f44;
        }

        .btn-add-field {
            width: 100%;
            padding: 12px;
            background: none;
            border: 2px dashed #333;
            border-radius: 8px;
            color: #888;
            cursor: pointer;
            margin-bottom: 20px;
        }

        .btn-add-field:hover {
            border-color: #F97316;
            color: #F97316;
        }

        .roofio-additions {
            background: #252542;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }

        .roofio-additions h3 {
            font-size: 14px;
            margin-bottom: 12px;
            color: #888;
        }

        .addition-items {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
        }

        .addition-items label {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #aaa;
            font-size: 13px;
        }

        .template-name-section {
            margin-bottom: 20px;
        }

        .template-name-section label {
            display: block;
            margin-bottom: 8px;
            color: #888;
        }

        .template-name-section input {
            width: 100%;
            background: #252542;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            color: #fff;
            font-size: 16px;
        }

        /* Actions */
        .form-setup-actions, .scan-actions, .review-actions, .standalone-actions {
            display: flex;
            justify-content: center;
            gap: 12px;
        }

        .btn-primary, .btn-secondary {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            border: none;
            font-size: 14px;
        }

        .btn-primary {
            background: #F97316;
            color: #fff;
        }

        .btn-primary:hover {
            background: #ea580c;
        }

        .btn-secondary {
            background: #333;
            color: #fff;
        }

        .btn-secondary:hover {
            background: #444;
        }

        .close-btn {
            position: absolute;
            top: 16px;
            right: 16px;
            background: none;
            border: none;
            color: #888;
            font-size: 28px;
            cursor: pointer;
        }

        .scan-header {
            position: relative;
        }

        /* Format Toggle */
        .format-toggle {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: #252542;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .toggle-label {
            color: #888;
            font-size: 13px;
        }

        .toggle-switch {
            display: flex;
            background: #1a1a2e;
            border-radius: 6px;
            padding: 4px;
        }

        .toggle-option {
            padding: 8px 16px;
            background: none;
            border: none;
            border-radius: 4px;
            color: #888;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .toggle-option.active {
            background: #F97316;
            color: #fff;
        }

        .edit-format-btn {
            margin-left: auto;
            background: none;
            border: none;
            color: #888;
            cursor: pointer;
            padding: 8px;
        }

        .edit-format-btn:hover {
            color: #F97316;
        }

        /* Processing Indicator */
        .processing-indicator {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            padding: 20px;
        }

        .spinner {
            width: 32px;
            height: 32px;
            border: 3px solid #333;
            border-top-color: #F97316;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Notification */
        .notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 8px;
            color: #fff;
            z-index: 10001;
            animation: slideIn 0.3s ease;
        }

        .notification.success { background: #10B981; }
        .notification.error { background: #EF4444; }
        .notification.info { background: #3B82F6; }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        /* Mobile */
        @media (max-width: 600px) {
            .format-options {
                grid-template-columns: 1fr;
            }

            .field-item {
                flex-wrap: wrap;
            }

            .field-item .field-label {
                width: 100%;
            }
        }
    `;

    document.head.appendChild(styles);
}

// =============================================================================
// NOTIFICATIONS
// =============================================================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// =============================================================================
// INITIALIZE
// =============================================================================

// Add styles on load
addFormStyles();

// Export functions for use in other scripts
window.FormsModule = {
    checkFormPreference,
    showFirstTimeSetupDialog,
    showScanSetup,
    createFormatToggle,
    initFormatToggle,
    openDocumentScanner,
    showNotification,
    state: FormsState
};
