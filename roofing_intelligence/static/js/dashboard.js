/**
 * Company Dashboard - Roofing OS
 * Role-based seats, project management, activity tracking
 */

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadProjects();
    loadActivityFeed();
    initFilterButtons();
    startAutoRefresh();
});

// ============================================================================
// THEME HANDLING
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
// SAMPLE DATA
// ============================================================================

const sampleProjects = [
    {
        id: 1,
        name: 'JHU Library Roofing',
        client: 'Turner Construction',
        status: 'green',
        value: '$450,000',
        progress: 72,
        assignee: 'Mike S.',
        initials: 'MS',
        dueDate: '2025-01-15',
        phase: 'Installation'
    },
    {
        id: 2,
        name: 'UMass Waterproofing',
        client: 'Gilbane Building',
        status: 'yellow',
        value: '$280,000',
        progress: 45,
        assignee: 'John D.',
        initials: 'JD',
        dueDate: '2025-02-01',
        phase: 'Submittals'
    },
    {
        id: 3,
        name: 'Boston Medical Center',
        client: 'Suffolk Construction',
        status: 'red',
        value: '$620,000',
        progress: 15,
        assignee: 'Sarah K.',
        initials: 'SK',
        dueDate: '2024-12-20',
        phase: 'Shop Drawings'
    },
    {
        id: 4,
        name: 'Hartford Plaza',
        client: 'Shawmut Design',
        status: 'green',
        value: '$185,000',
        progress: 90,
        assignee: 'Mike S.',
        initials: 'MS',
        dueDate: '2024-12-15',
        phase: 'Closeout'
    },
    {
        id: 5,
        name: 'MIT Dormitory',
        client: 'Consigli Construction',
        status: 'yellow',
        value: '$340,000',
        progress: 30,
        assignee: 'John D.',
        initials: 'JD',
        dueDate: '2025-03-01',
        phase: 'Estimating'
    },
    {
        id: 6,
        name: 'Providence Hospital',
        client: 'Dimeo Construction',
        status: 'green',
        value: '$520,000',
        progress: 55,
        assignee: 'Sarah K.',
        initials: 'SK',
        dueDate: '2025-02-15',
        phase: 'Procurement'
    }
];

const sampleActivities = [
    {
        type: 'success',
        icon: 'check-circle',
        text: '<strong>Mike S.</strong> completed daily report for JHU Library',
        time: '5 min ago',
        project: 'JHU Library'
    },
    {
        type: 'warning',
        icon: 'alert-triangle',
        text: '<strong>RFI #12</strong> requires response by end of day',
        time: '15 min ago',
        project: 'UMass'
    },
    {
        type: 'info',
        icon: 'file-text',
        text: '<strong>John D.</strong> submitted bid for MIT Dormitory',
        time: '1 hour ago',
        project: 'MIT Dormitory'
    },
    {
        type: 'error',
        icon: 'x-circle',
        text: 'Shop drawing revision requested for <strong>Boston Medical</strong>',
        time: '2 hours ago',
        project: 'Boston Medical'
    },
    {
        type: 'success',
        icon: 'dollar-sign',
        text: 'Payment received: <strong>$45,000</strong> from Hartford Plaza',
        time: '3 hours ago',
        project: 'Hartford Plaza'
    },
    {
        type: 'info',
        icon: 'truck',
        text: 'Material delivery scheduled for JHU Library - Tomorrow 7AM',
        time: '4 hours ago',
        project: 'JHU Library'
    }
];

const roleSkills = {
    pm: {
        title: 'Project Manager',
        skills: [
            { name: 'Estimating', status: 'active' },
            { name: 'Bid Prep', status: 'active' },
            { name: 'Spec Interpreter', status: 'active' },
            { name: 'Submittals', status: 'active' },
            { name: 'RFI Writer', status: 'active' },
            { name: 'Change Orders', status: 'learning' },
            { name: 'Scheduling', status: 'active' },
            { name: 'Safety', status: 'active' },
            { name: 'Quality Control', status: 'active' },
            { name: 'Daily Reports', status: 'active' },
            { name: 'Closeout', status: 'active' },
            { name: 'Contract Review', status: 'active' }
        ],
        tasks: [
            { name: 'Respond to RFI #12', project: 'UMass', priority: 'high', due: 'Today 5PM' },
            { name: 'Review submittal package', project: 'JHU Library', priority: 'medium', due: 'Tomorrow' },
            { name: 'Schedule kickoff meeting', project: 'MIT Dorm', priority: 'low', due: 'This Week' }
        ]
    },
    estimator: {
        title: 'Estimator',
        skills: [
            { name: 'Takeoffs', status: 'active' },
            { name: 'Pricing', status: 'active' },
            { name: 'Bid Preparation', status: 'active' },
            { name: 'Scope Analysis', status: 'active' },
            { name: 'Subcontractor Quotes', status: 'active' },
            { name: 'Value Engineering', status: 'learning' }
        ],
        tasks: [
            { name: 'Complete bid for Boston Medical', project: 'Boston Medical', priority: 'high', due: 'Today 5PM' },
            { name: 'Update pricing sheet', project: 'MIT Dorm', priority: 'medium', due: 'Tomorrow' },
            { name: 'Review subcontractor bids', project: 'Providence', priority: 'low', due: 'This Week' }
        ]
    },
    operations: {
        title: 'Operations',
        skills: [
            { name: 'Crew Scheduling', status: 'active' },
            { name: 'Material Logistics', status: 'active' },
            { name: 'Equipment Management', status: 'active' },
            { name: 'Dispatch', status: 'active' },
            { name: 'Weather Monitoring', status: 'active' },
            { name: 'Resource Planning', status: 'learning' }
        ],
        tasks: [
            { name: 'Reschedule Crew 3 for weather', project: 'UMass', priority: 'medium', due: 'Today' },
            { name: 'Confirm material delivery', project: 'JHU Library', priority: 'low', due: 'Tomorrow' }
        ]
    },
    accounting: {
        title: 'Accounting',
        skills: [
            { name: 'Accounts Receivable', status: 'active' },
            { name: 'Accounts Payable', status: 'active' },
            { name: 'Payroll', status: 'active' },
            { name: 'Job Costing', status: 'active' },
            { name: 'Collections', status: 'active' },
            { name: 'Financial Reporting', status: 'learning' }
        ],
        tasks: [
            { name: 'Follow up on Hartford payment', project: 'Hartford Plaza', priority: 'high', due: 'Today' },
            { name: 'Process payroll', project: 'Company', priority: 'high', due: 'Friday' },
            { name: 'Submit invoice', project: 'JHU Library', priority: 'medium', due: 'This Week' }
        ]
    },
    field: {
        title: 'Superintendent',
        skills: [
            { name: 'Daily Reports', status: 'active' },
            { name: 'Safety Management', status: 'active' },
            { name: 'Quality Control', status: 'active' },
            { name: 'Crew Supervision', status: 'active' },
            { name: 'Progress Tracking', status: 'active' },
            { name: 'Problem Solving', status: 'active' }
        ],
        tasks: [
            { name: 'Complete daily report', project: 'JHU Library', priority: 'medium', due: 'End of Day' },
            { name: 'Safety inspection', project: 'UMass', priority: 'medium', due: 'Morning' },
            { name: 'Quality walkthrough', project: 'Hartford Plaza', priority: 'low', due: 'This Week' }
        ]
    },
    'shop-drawings': {
        title: 'Shop Drawings',
        skills: [
            { name: 'AutoCAD LT', status: 'active' },
            { name: 'Detail Development', status: 'active' },
            { name: 'Spec Interpretation', status: 'active' },
            { name: 'Flashing Details', status: 'active' },
            { name: 'Membrane Layouts', status: 'active' },
            { name: 'Submittal Packages', status: 'active' }
        ],
        tasks: [
            { name: 'Complete parapet details', project: 'Boston Medical', priority: 'high', due: 'Monday' },
            { name: 'Revise curb flashing', project: 'MIT Dorm', priority: 'medium', due: 'This Week' },
            { name: 'Update cover sheet', project: 'JHU Library', priority: 'low', due: 'Next Week' }
        ]
    }
};

// ============================================================================
// PROJECT LOADING
// ============================================================================

function loadProjects() {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;

    grid.innerHTML = sampleProjects.map(project => createProjectCard(project)).join('');
}

function createProjectCard(project) {
    return `
        <div class="project-card status-${project.status}" data-status="${project.status}" onclick="openProject(${project.id})">
            <div class="project-header">
                <div>
                    <div class="project-name">${project.name}</div>
                    <div class="project-client">${project.client}</div>
                </div>
                <div class="project-status">
                    <span class="traffic-light ${project.status}"></span>
                </div>
            </div>
            <div class="project-stats">
                <div class="project-stat">
                    <span class="project-stat-value">${project.value}</span>
                    <span class="project-stat-label">Contract</span>
                </div>
                <div class="project-stat">
                    <span class="project-stat-value">${project.phase}</span>
                    <span class="project-stat-label">Phase</span>
                </div>
                <div class="project-stat">
                    <span class="project-stat-value">${formatDate(project.dueDate)}</span>
                    <span class="project-stat-label">Due</span>
                </div>
            </div>
            <div class="project-progress">
                <div class="progress-header">
                    <span class="progress-label">Progress</span>
                    <span class="progress-value">${project.progress}%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill ${project.status}" style="width: ${project.progress}%"></div>
                </div>
            </div>
            <div class="project-assignee">
                <div class="assignee-avatar">${project.initials}</div>
                <span class="assignee-name">${project.assignee}</span>
            </div>
        </div>
    `;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const month = date.toLocaleDateString('en-US', { month: 'short' });
    const day = date.getDate();
    return `${month} ${day}`;
}

// ============================================================================
// ACTIVITY FEED
// ============================================================================

function loadActivityFeed() {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;

    feed.innerHTML = sampleActivities.map(activity => createActivityItem(activity)).join('');
}

function createActivityItem(activity) {
    const iconSvg = getActivityIcon(activity.icon);
    return `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                ${iconSvg}
            </div>
            <div class="activity-content">
                <div class="activity-text">${activity.text}</div>
                <div class="activity-meta">
                    <span>${activity.time}</span>
                    <span>${activity.project}</span>
                </div>
            </div>
        </div>
    `;
}

function getActivityIcon(iconName) {
    const icons = {
        'check-circle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        'alert-triangle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        'file-text': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
        'x-circle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        'dollar-sign': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
        'truck': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>'
    };
    return icons[iconName] || icons['file-text'];
}

// ============================================================================
// FILTER FUNCTIONALITY
// ============================================================================

function initFilterButtons() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterProjects(btn.dataset.filter);
        });
    });
}

function filterProjects(status) {
    const cards = document.querySelectorAll('.project-card');
    cards.forEach(card => {
        if (status === 'all' || card.dataset.status === status) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

// ============================================================================
// SEAT DETAIL MODAL
// ============================================================================

function openSeatDetail(role) {
    const modal = document.getElementById('seat-modal');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    const roleData = roleSkills[role];
    if (!roleData) return;

    title.textContent = roleData.title + ' Details';

    const avatarClass = role === 'shop-drawings' ? 'shop-drawings' : role;

    body.innerHTML = `
        <div class="seat-detail">
            <div class="seat-detail-header">
                <div class="seat-detail-avatar seat-avatar ${avatarClass}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </div>
                <div class="seat-detail-info">
                    <h4>${roleData.title}</h4>
                    <p>${roleData.skills.length} Skills Active</p>
                </div>
            </div>

            <div class="seat-detail-section">
                <h5>Active Skills</h5>
                <div class="skill-list">
                    ${roleData.skills.map(skill => `
                        <div class="skill-item">
                            <span class="skill-status ${skill.status}"></span>
                            <span>${skill.name}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="seat-detail-section">
                <h5>Current Tasks</h5>
                <div class="task-list">
                    ${roleData.tasks.map(task => `
                        <div class="task-item">
                            <div class="task-priority ${task.priority}"></div>
                            <div class="task-info">
                                <div class="task-name">${task.name}</div>
                                <div class="task-project">${task.project}</div>
                            </div>
                            <div class="task-due">${task.due}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
}

function closeSeatModal() {
    const modal = document.getElementById('seat-modal');
    modal.classList.add('hidden');
}

// ============================================================================
// NEW PROJECT MODAL
// ============================================================================

function openNewProject() {
    const modal = document.getElementById('new-project-modal');
    modal.classList.remove('hidden');
}

function closeNewProjectModal() {
    const modal = document.getElementById('new-project-modal');
    modal.classList.add('hidden');
    document.getElementById('new-project-form').reset();
}

function createProject(event) {
    event.preventDefault();

    const name = document.getElementById('project-name').value;
    const client = document.getElementById('project-client').value;
    const value = document.getElementById('project-value').value;
    const startDate = document.getElementById('project-start').value;
    const pm = document.getElementById('project-pm').value;

    // Create new project object
    const newProject = {
        id: sampleProjects.length + 1,
        name: name,
        client: client || 'TBD',
        status: 'yellow',
        value: value || 'TBD',
        progress: 0,
        assignee: pm || 'Unassigned',
        initials: pm ? pm.substring(0, 2).toUpperCase() : 'UN',
        dueDate: startDate || new Date().toISOString().split('T')[0],
        phase: 'Bidding'
    };

    // Add to projects array
    sampleProjects.unshift(newProject);

    // Reload projects grid
    loadProjects();

    // Close modal and show toast
    closeNewProjectModal();
    showToast('Project created successfully!', 'success');
}

// ============================================================================
// PROJECT DETAIL
// ============================================================================

function openProject(projectId) {
    const project = sampleProjects.find(p => p.id === projectId);
    if (!project) return;

    // For now, show a toast with project info
    showToast(`Opening ${project.name}...`, 'info');

    // TODO: Navigate to project detail page
    // window.location.href = `/project/${projectId}`;
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add toast out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes toastOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }
`;
document.head.appendChild(style);

// ============================================================================
// REFRESH & AUTO-UPDATE
// ============================================================================

function refreshDashboard() {
    showToast('Refreshing dashboard...', 'info');
    loadProjects();
    loadActivityFeed();
    updateMetrics();
}

function updateMetrics() {
    // Simulate metric updates
    const activeProjects = document.getElementById('active-projects');
    const pendingBids = document.getElementById('pending-bids');
    const roadblocks = document.getElementById('roadblocks');

    if (activeProjects) activeProjects.textContent = sampleProjects.length;
    if (pendingBids) pendingBids.textContent = sampleProjects.filter(p => p.phase === 'Bidding' || p.phase === 'Estimating').length;
    if (roadblocks) roadblocks.textContent = sampleProjects.filter(p => p.status === 'red').length;
}

function startAutoRefresh() {
    // Update metrics every 30 seconds
    setInterval(updateMetrics, 30000);

    // Check for new activities every minute
    setInterval(() => {
        // Simulate new activity
        const newActivity = {
            type: 'info',
            icon: 'file-text',
            text: 'Dashboard updated automatically',
            time: 'Just now',
            project: 'System'
        };
        // Could add to feed here if needed
    }, 60000);
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

document.addEventListener('keydown', (e) => {
    // ESC to close modals
    if (e.key === 'Escape') {
        closeSeatModal();
        closeNewProjectModal();
    }

    // Ctrl+N for new project
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        openNewProject();
    }

    // Ctrl+R for refresh
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        refreshDashboard();
    }
});

// ============================================================================
// API INTEGRATION (Future)
// ============================================================================

async function fetchProjects() {
    try {
        const response = await fetch('/api/company/projects');
        if (response.ok) {
            const data = await response.json();
            return data.projects;
        }
    } catch (error) {
        console.error('Error fetching projects:', error);
    }
    return sampleProjects;
}

async function fetchActivityFeed() {
    try {
        const response = await fetch('/api/company/activity');
        if (response.ok) {
            const data = await response.json();
            return data.activities;
        }
    } catch (error) {
        console.error('Error fetching activity:', error);
    }
    return sampleActivities;
}

async function saveProject(projectData) {
    try {
        const response = await fetch('/api/company/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Error saving project:', error);
    }
    return null;
}
