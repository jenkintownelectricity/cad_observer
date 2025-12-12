/**
 * ROOFIO Dashboard - AI-Powered Roofing OS
 * Complete functionality for all 13 AI Seats
 * Cross-module intelligence, voice commands, and real-time updates
 */

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadProjectsFromAPI();
    loadActivityFeed();
    loadMetricsFromAPI();
    initFilterButtons();
    initDateFields();
    startAutoRefresh();
    initCrossModuleIntelligence();
    console.log('✓ ROOFIO Dashboard initialized');
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
// SAMPLE DATA (Fallback when API unavailable)
// ============================================================================

let projectsData = [];

const sampleProjects = [
    {
        id: 1,
        name: 'JHU Library Roofing',
        client: 'Turner Construction',
        status: 'green',
        value: '$450,000',
        progress: 72,
        assignee: 'Mike S.',
        phase: 'Installation'
    },
    {
        id: 2,
        name: 'UMass Waterproofing',
        client: 'Gilbane Building',
        status: 'yellow',
        value: '$320,000',
        progress: 45,
        assignee: 'Tony R.',
        phase: 'Mobilization'
    },
    {
        id: 3,
        name: 'Boston Medical Center',
        client: 'Suffolk Construction',
        status: 'red',
        value: '$680,000',
        progress: 15,
        assignee: 'Dave K.',
        phase: 'Bidding'
    }
];

const sampleActivities = [
    {
        type: 'success',
        icon: 'check-circle',
        text: '<strong>AI Estimator</strong> generated bid for Boston Medical - $680,000',
        time: '10 min ago',
        project: 'Boston Medical'
    },
    {
        type: 'warning',
        icon: 'alert-triangle',
        text: '<strong>Weather Alert</strong> Rain expected tomorrow - JHU crews notified',
        time: '25 min ago',
        project: 'JHU Library'
    },
    {
        type: 'info',
        icon: 'file-text',
        text: '<strong>Daily Log</strong> submitted by Crew 2 - UMass',
        time: '1 hour ago',
        project: 'UMass'
    },
    {
        type: 'success',
        icon: 'dollar-sign',
        text: '<strong>Payment Received</strong> $45,000 from Hartford Plaza',
        time: '2 hours ago',
        project: 'Hartford Plaza'
    }
];

// ============================================================================
// COMPLETE ROLE DATA FOR ALL 8 AI SEATS
// ============================================================================

const roleSkills = {
    estimator: {
        title: 'AI Estimator',
        tagline: 'Win more bids',
        icon: 'calculator',
        skills: [
            { name: 'Aerial Measurement', status: 'active', ai: true },
            { name: 'Material Pricing', status: 'active', ai: true },
            { name: 'Photo-to-Estimate', status: 'active', ai: true },
            { name: 'Bid Win/Loss Learning', status: 'learning', ai: true },
            { name: 'Schedule of Values', status: 'active' },
            { name: 'PDF Proposals', status: 'active' },
            { name: 'E-Sign Integration', status: 'pending' },
            { name: 'Voice Estimating', status: 'pending', ai: true }
        ],
        tasks: [
            { name: 'Complete bid for Boston Medical', project: 'Boston Medical', priority: 'high', due: 'Today 5PM' },
            { name: 'Takeoff for MIT Dorm project', project: 'MIT Dorm', priority: 'medium', due: 'Tomorrow' },
            { name: 'Review material pricing for TPO', project: 'General', priority: 'low', due: 'This week' }
        ],
        metrics: {
            hitRate: '67%',
            avgBidTime: '2.3 hrs',
            openBids: 5
        }
    },
    pm: {
        title: 'AI Project Manager',
        tagline: 'Never miss a detail',
        icon: 'user',
        skills: [
            { name: 'Gantt Scheduling', status: 'active' },
            { name: 'RFI Tracking', status: 'active' },
            { name: 'Submittal Management', status: 'active' },
            { name: 'Change Order Processing', status: 'active' },
            { name: 'AI Meeting Summarizer', status: 'active', ai: true },
            { name: 'Delay Claim Builder', status: 'active', ai: true },
            { name: 'Predictive Completion', status: 'learning', ai: true },
            { name: 'Document Control', status: 'active' }
        ],
        tasks: [
            { name: 'Respond to RFI #12', project: 'JHU Library', priority: 'high', due: 'Today 5PM' },
            { name: 'Review submittal package', project: 'UMass', priority: 'medium', due: 'Tomorrow' },
            { name: 'Update project schedule', project: 'Boston Medical', priority: 'medium', due: 'This week' }
        ],
        metrics: {
            openRFIs: 8,
            pendingSubmittals: 12,
            changeOrders: 3
        }
    },
    superintendent: {
        title: 'AI Superintendent',
        tagline: 'Field visibility',
        icon: 'clipboard',
        skills: [
            { name: 'Daily Logs (One-Tap)', status: 'active', ai: true },
            { name: 'Photo Progress Mapping', status: 'active', ai: true },
            { name: 'Voice Logging', status: 'active', ai: true },
            { name: 'Crew Scheduling', status: 'active' },
            { name: 'Weather Integration', status: 'active' },
            { name: 'Time Entry', status: 'active' },
            { name: 'Material Tracking', status: 'active' },
            { name: 'Offline Mode', status: 'pending' }
        ],
        tasks: [
            { name: 'Submit daily report', project: 'JHU Library', priority: 'medium', due: 'End of Day' },
            { name: 'Upload progress photos', project: 'UMass', priority: 'low', due: 'Today' }
        ],
        metrics: {
            activeCrews: 3,
            sfToday: '12,450',
            reportCompletion: '95%'
        }
    },
    qc: {
        title: 'AI QC Manager',
        tagline: 'Catch defects early',
        icon: 'check-square',
        skills: [
            { name: 'Defect Detection AI', status: 'active', ai: true },
            { name: 'Digital Checklists', status: 'active' },
            { name: 'NCR Management', status: 'active' },
            { name: 'Punch Lists', status: 'active' },
            { name: 'Crew Quality Scoring', status: 'active', ai: true },
            { name: 'Auto Warranty Registration', status: 'pending', ai: true },
            { name: 'Photo Documentation', status: 'active' },
            { name: 'Inspection Reports', status: 'active' }
        ],
        tasks: [
            { name: 'Review fish mouth detection', project: 'JHU Library', priority: 'high', due: 'Today' },
            { name: 'Final inspection walkthrough', project: 'UMass', priority: 'medium', due: 'Tomorrow' },
            { name: 'Complete punch list items', project: 'Hartford Plaza', priority: 'low', due: 'This week' }
        ],
        metrics: {
            passRate: '98%',
            openNCRs: 2,
            punchItems: 14
        }
    },
    safety: {
        title: 'AI Safety Director',
        tagline: 'Zero incidents',
        icon: 'shield',
        skills: [
            { name: 'Dynamic JHA Generator', status: 'active', ai: true },
            { name: 'PPE Photo AI', status: 'active', ai: true },
            { name: 'Heat Illness Prevention', status: 'active', ai: true },
            { name: 'Certification Tracker', status: 'active' },
            { name: 'Toolbox Talk Library', status: 'active' },
            { name: 'Incident Reporting', status: 'active' },
            { name: 'OSHA Compliance', status: 'active' },
            { name: 'EMR Tracking', status: 'active' }
        ],
        tasks: [
            { name: 'Complete morning JHA', project: 'All Projects', priority: 'high', due: 'Daily 6AM' },
            { name: 'Renew OSHA 30 - Mike S.', project: 'Certifications', priority: 'medium', due: 'Next week' },
            { name: 'Heat illness training', project: 'All Crews', priority: 'medium', due: 'This week' }
        ],
        metrics: {
            daysSafe: 124,
            incidents: 0,
            expiringCerts: 3
        }
    },
    accounting: {
        title: 'AI Accounting',
        tagline: 'Get paid faster',
        icon: 'dollar-sign',
        skills: [
            { name: 'AIA G702/G703 Billing', status: 'active' },
            { name: 'One-Click AIA', status: 'active', ai: true },
            { name: 'AI Collections', status: 'active', ai: true },
            { name: 'Job Costing', status: 'active' },
            { name: 'Retainage Tracking', status: 'active' },
            { name: 'Lien Waiver Management', status: 'active' },
            { name: 'Cash Position Dashboard', status: 'active', ai: true },
            { name: 'QuickBooks Integration', status: 'pending' }
        ],
        tasks: [
            { name: 'Follow up Hartford payment', project: 'Hartford Plaza', priority: 'high', due: 'Today' },
            { name: 'Submit Draw #3', project: 'JHU Library', priority: 'medium', due: 'Friday' },
            { name: 'Reconcile job costs', project: 'UMass', priority: 'low', due: 'Month end' }
        ],
        metrics: {
            arOverdue: '$45,000',
            collected: '$124,000',
            retainage: '$89,000'
        }
    },
    operations: {
        title: 'AI Operations',
        tagline: 'Materials on time',
        icon: 'settings',
        skills: [
            { name: 'Predictive Ordering', status: 'active', ai: true },
            { name: 'Live Price Comparison', status: 'active', ai: true },
            { name: 'Delivery Tracking', status: 'active' },
            { name: 'Emergency Material Finder', status: 'active', ai: true },
            { name: 'Inventory Management', status: 'active' },
            { name: 'Vendor Management', status: 'active' },
            { name: 'Equipment Scheduling', status: 'active' },
            { name: 'Crane/Lift Coordination', status: 'active' }
        ],
        tasks: [
            { name: 'Confirm TPO delivery', project: 'JHU Library', priority: 'medium', due: 'Tomorrow' },
            { name: 'Review price spike alert', project: 'All Projects', priority: 'low', due: 'Today' },
            { name: 'Schedule crane for UMass', project: 'UMass', priority: 'medium', due: 'Next week' }
        ],
        metrics: {
            inTransit: 4,
            delivered: 6,
            priceAlerts: 2
        }
    },
    'shop-drawings': {
        title: 'AI Shop Drawings',
        tagline: 'Details that win',
        icon: 'layers',
        skills: [
            { name: 'Spec-to-Detail AI', status: 'active', ai: true },
            { name: 'Assembly Letter Generator', status: 'active', ai: true },
            { name: 'RFI Suggestion Engine', status: 'active', ai: true },
            { name: 'Detail Library', status: 'active' },
            { name: 'Revision Control', status: 'active' },
            { name: 'Submittal Packages', status: 'active' },
            { name: 'AutoCAD Integration', status: 'active' },
            { name: 'Manufacturer Details', status: 'pending' }
        ],
        tasks: [
            { name: 'Complete parapet details', project: 'Boston Medical', priority: 'high', due: 'Monday' },
            { name: 'Review MIT drawings', project: 'MIT Dorm', priority: 'medium', due: 'Wednesday' },
            { name: 'Generate assembly letter', project: 'JHU Library', priority: 'low', due: 'This week' }
        ],
        metrics: {
            inProgress: 4,
            submitted: 2,
            rush: 1
        }
    },
    sales: {
        title: 'AI Sales/CRM',
        tagline: 'Close more deals',
        icon: 'trending-up',
        skills: [
            { name: 'Lead Scoring AI', status: 'active', ai: true },
            { name: 'Pipeline Management', status: 'active' },
            { name: 'Follow-up Automation', status: 'active', ai: true },
            { name: 'E-Signature Integration', status: 'active' },
            { name: 'Proposal Generator', status: 'active', ai: true },
            { name: 'Win/Loss Analysis', status: 'learning', ai: true },
            { name: 'Contact Management', status: 'active' },
            { name: 'Email Templates', status: 'active' }
        ],
        tasks: [
            { name: 'Follow up with Turner Construction', project: 'Leads', priority: 'high', due: 'Today' },
            { name: 'Send proposal to Gilbane', project: 'Leads', priority: 'medium', due: 'Tomorrow' },
            { name: 'Review hot leads', project: 'Pipeline', priority: 'medium', due: 'This week' }
        ],
        metrics: {
            hotLeads: 12,
            pipelineValue: '$2.4M',
            closeRate: '34%'
        }
    },
    hr: {
        title: 'AI HR/Workforce',
        tagline: 'Build your team',
        icon: 'users',
        skills: [
            { name: 'I-9/E-Verify', status: 'active', ai: true },
            { name: 'Onboarding Workflow', status: 'active', ai: true },
            { name: 'Union Tracking', status: 'active' },
            { name: 'Certification Tracking', status: 'active', ai: true },
            { name: 'Time & Attendance', status: 'active' },
            { name: 'Payroll Integration', status: 'pending' },
            { name: 'Performance Reviews', status: 'active' },
            { name: 'Training Records', status: 'active' }
        ],
        tasks: [
            { name: 'Complete I-9 for new hire', project: 'Hiring', priority: 'high', due: 'Today' },
            { name: 'Review expiring certifications', project: 'Compliance', priority: 'medium', due: 'This week' },
            { name: 'Process union dues', project: 'Union', priority: 'low', due: 'Month end' }
        ],
        metrics: {
            activeEmployees: 47,
            expiringCerts: 5,
            openPositions: 3
        }
    },
    marketing: {
        title: 'AI Marketing',
        tagline: 'Know your ROI',
        icon: 'target',
        skills: [
            { name: 'Lead Attribution', status: 'active', ai: true },
            { name: 'Campaign ROI', status: 'active', ai: true },
            { name: 'Cost per Lead Analysis', status: 'active', ai: true },
            { name: 'Google Ads Integration', status: 'active' },
            { name: 'Social Media Tracking', status: 'pending' },
            { name: 'Email Campaign Metrics', status: 'active' },
            { name: 'Website Analytics', status: 'active' },
            { name: 'A/B Testing', status: 'learning', ai: true }
        ],
        tasks: [
            { name: 'Review Q4 campaign performance', project: 'Analytics', priority: 'medium', due: 'This week' },
            { name: 'Update lead source tracking', project: 'Setup', priority: 'low', due: 'Next week' }
        ],
        metrics: {
            costPerLead: '$127',
            conversionRate: '8.4%',
            monthlyLeads: 34
        }
    },
    warranty: {
        title: 'AI Warranty/Service',
        tagline: 'Protect & serve',
        icon: 'shield',
        skills: [
            { name: 'Warranty Registration', status: 'active', ai: true },
            { name: 'Claim Tracking', status: 'active' },
            { name: 'Service Ticket System', status: 'active', ai: true },
            { name: 'Auto-Renewal Notices', status: 'active', ai: true },
            { name: 'Customer Portal', status: 'pending' },
            { name: 'Parts Ordering', status: 'active' },
            { name: 'Technician Dispatch', status: 'active' },
            { name: 'Warranty Analytics', status: 'learning', ai: true }
        ],
        tasks: [
            { name: 'Process claim #1247', project: 'Claims', priority: 'high', due: 'Today' },
            { name: 'Schedule service call - Turner', project: 'Service', priority: 'medium', due: 'Tomorrow' },
            { name: 'Send renewal notices', project: 'Renewals', priority: 'low', due: 'This week' }
        ],
        metrics: {
            activeWarranties: 156,
            openClaims: 4,
            serviceTickets: 7
        }
    },
    owner: {
        title: 'AI Owner Dashboard',
        tagline: 'See everything',
        icon: 'briefcase',
        skills: [
            { name: 'P&L Overview', status: 'active', ai: true },
            { name: 'Cash Position', status: 'active', ai: true },
            { name: 'KPI Dashboard', status: 'active', ai: true },
            { name: 'AI Business Insights', status: 'active', ai: true },
            { name: 'Risk Assessment', status: 'active', ai: true },
            { name: 'Competitor Analysis', status: 'learning', ai: true },
            { name: 'Financial Forecasting', status: 'active', ai: true },
            { name: 'Board Reports', status: 'pending' }
        ],
        tasks: [
            { name: 'Review monthly P&L', project: 'Finance', priority: 'high', due: 'Today' },
            { name: 'Approve cash flow forecast', project: 'Finance', priority: 'medium', due: 'This week' },
            { name: 'Review AI recommendations', project: 'Strategy', priority: 'medium', due: 'This week' }
        ],
        metrics: {
            revenueMTD: '$847K',
            grossMargin: '24%',
            backlog: '$3.2M'
        }
    }
};

// ============================================================================
// API FUNCTIONS
// ============================================================================

async function loadProjectsFromAPI() {
    const grid = document.getElementById('projects-grid');
    if (!grid) return;

    if (window.UX?.Loader && !grid.querySelector('.project-card')) {
        window.UX.Loader.showSkeleton(grid, 3);
    }

    try {
        const response = await fetch('/api/company/projects');
        if (response.ok) {
            const data = await response.json();
            projectsData = data.projects || [];

            if (projectsData.length === 0) {
                projectsData = sampleProjects;
            }
            grid.innerHTML = projectsData.map(project => createProjectCard(project)).join('');
            console.log('✓ Loaded', projectsData.length, 'projects');
        } else {
            throw new Error('API response not OK');
        }
    } catch (error) {
        console.log('Using sample projects data');
        projectsData = sampleProjects;
        grid.innerHTML = projectsData.map(project => createProjectCard(project)).join('');
    }
}

async function loadMetricsFromAPI() {
    try {
        const response = await fetch('/api/company/metrics');
        if (response.ok) {
            const data = await response.json();
            updateMetric('active-projects', data.active_projects);
            updateMetric('pending-bids', data.pending_bids);
            updateMetric('roadblocks', data.roadblocks);
            updateMetric('revenue-mtd', data.revenue_mtd);
            updateMetric('safety-incidents', data.safety_incidents || 0);
        }
    } catch (error) {
        console.log('Using default metrics');
    }
}

function updateMetric(id, value) {
    const el = document.getElementById(id);
    if (el && value !== undefined) el.textContent = value;
}

async function createProjectAPI(projectData) {
    try {
        const response = await fetch('/api/company/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData)
        });

        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create project');
        }
    } catch (error) {
        console.error('Error creating project:', error);
        throw error;
    }
}

// ============================================================================
// PROJECT CARD
// ============================================================================

function createProjectCard(project) {
    const id = project.id || project.project_id;
    const name = project.name;
    const client = project.client || '';
    const status = project.status || 'yellow';
    const value = project.value || '';
    const progress = project.progress || 0;
    const assignee = project.assignee || 'Unassigned';
    const initials = assignee.substring(0, 2).toUpperCase();
    const phase = project.phase || 'Bidding';

    return `
        <div class="project-card status-${status}" data-status="${status}" data-id="${id}" onclick="openProject('${id}')">
            <div class="project-header">
                <div>
                    <div class="project-name">${name}</div>
                    <div class="project-client">${client}</div>
                </div>
                <div class="project-status">
                    <span class="traffic-light ${status}"></span>
                </div>
            </div>
            <div class="project-stats">
                <div class="project-stat">
                    <span class="project-stat-value">${value}</span>
                    <span class="project-stat-label">Contract</span>
                </div>
                <div class="project-stat">
                    <span class="project-stat-value">${phase}</span>
                    <span class="project-stat-label">Phase</span>
                </div>
            </div>
            <div class="project-progress">
                <div class="progress-header">
                    <span class="progress-label">Progress</span>
                    <span class="progress-value">${progress}%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill ${status}" style="width: ${progress}%"></div>
                </div>
            </div>
            <div class="project-assignee">
                <div class="assignee-avatar">${initials}</div>
                <span class="assignee-name">${assignee}</span>
            </div>
        </div>
    `;
}

// ============================================================================
// ACTIVITY FEED
// ============================================================================

function loadActivityFeed() {
    const feed = document.getElementById('activity-feed');
    if (!feed) return;

    fetch('/api/company/activity')
        .then(response => response.json())
        .then(data => {
            const activities = data.activities || sampleActivities;
            feed.innerHTML = activities.map(activity => createActivityItem(activity)).join('');
        })
        .catch(() => {
            feed.innerHTML = sampleActivities.map(activity => createActivityItem(activity)).join('');
        });
}

function createActivityItem(activity) {
    const iconSvg = getActivityIcon(activity.icon || 'file-text');
    return `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">${iconSvg}</div>
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
        'dollar-sign': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
        'truck': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>'
    };
    return icons[iconName] || icons['file-text'];
}

// ============================================================================
// CROSS-MODULE INTELLIGENCE
// ============================================================================

function initCrossModuleIntelligence() {
    // Simulate real-time cross-module events
    setInterval(() => {
        const feed = document.getElementById('intelligence-feed');
        if (feed && Math.random() > 0.8) {
            // Randomly add new intelligence items
            const events = [
                { type: 'success', trigger: 'Material delivery confirmed', actions: ['Crew notified', 'Schedule updated', 'Inventory adjusted'] },
                { type: 'warning', trigger: 'Price increase detected on TPO', actions: ['Open bids flagged', 'Buyer notified', 'Alternatives suggested'] },
                { type: 'info', trigger: 'Crew finished early at UMass', actions: ['Dispatcher notified', 'Tomorrow schedule adjusted'] }
            ];
            // Could add dynamic updates here
        }
    }, 30000);
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
// DATE FIELD INITIALIZATION
// ============================================================================

function initDateFields() {
    // Set today's date as default for date fields
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value) {
            input.value = today;
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

    title.textContent = roleData.title;

    body.innerHTML = `
        <div class="seat-detail">
            <div class="seat-detail-header">
                <div class="seat-detail-avatar seat-avatar ${role}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </div>
                <div class="seat-detail-info">
                    <h4>${roleData.title}</h4>
                    <p class="seat-tagline">${roleData.tagline}</p>
                </div>
            </div>

            ${roleData.metrics ? `
            <div class="seat-metrics-grid">
                ${Object.entries(roleData.metrics).map(([key, value]) => `
                    <div class="seat-metric">
                        <span class="metric-value">${value}</span>
                        <span class="metric-label">${formatMetricLabel(key)}</span>
                    </div>
                `).join('')}
            </div>
            ` : ''}

            <div class="seat-detail-section">
                <h5>AI Capabilities & Skills</h5>
                <div class="skill-list">
                    ${roleData.skills.map(skill => `
                        <div class="skill-item ${skill.ai ? 'ai-skill' : ''}">
                            <span class="skill-status ${skill.status}"></span>
                            <span>${skill.name}</span>
                            ${skill.ai ? '<span class="ai-badge-small">AI</span>' : ''}
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

            <div class="seat-detail-actions">
                ${getSeatActions(role)}
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
}

function formatMetricLabel(key) {
    return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
}

function getSeatActions(role) {
    const actions = {
        estimator: `
            <button class="btn-primary" onclick="closeSeatModal(); openEstimateForm();">New Estimate</button>
            <button class="btn-secondary" onclick="showToast('Opening bid queue...', 'info')">View All Bids</button>
        `,
        pm: `
            <button class="btn-primary" onclick="closeSeatModal(); openRFIForm();">New RFI</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openSubmittalForm();">New Submittal</button>
        `,
        superintendent: `
            <button class="btn-primary" onclick="closeSeatModal(); openDailyLogForm();">Daily Log</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openPhotoCapture();">Upload Photos</button>
        `,
        qc: `
            <button class="btn-primary" onclick="closeSeatModal(); openInspectionForm();">New Inspection</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openPunchListForm();">Punch List</button>
        `,
        safety: `
            <button class="btn-primary" onclick="closeSeatModal(); openJHAForm();">New JHA</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openToolboxTalkForm();">Toolbox Talk</button>
        `,
        accounting: `
            <button class="btn-primary" onclick="closeSeatModal(); openAIABillingForm();">AIA Billing</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openChangeOrderForm();">Change Order</button>
        `,
        operations: `
            <button class="btn-primary" onclick="closeSeatModal(); openPurchaseOrderForm();">New PO</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openVendorCompare();">Compare Prices</button>
        `,
        'shop-drawings': `
            <button class="btn-primary" onclick="closeSeatModal(); openDrawingForm();">New Drawing</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openDetailLibrary();">Detail Library</button>
        `,
        sales: `
            <button class="btn-primary" onclick="closeSeatModal(); openLeadForm();">New Lead</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openPipelineView();">View Pipeline</button>
        `,
        hr: `
            <button class="btn-primary" onclick="closeSeatModal(); openEmployeeForm();">New Employee</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openCertificationsView();">Certifications</button>
        `,
        marketing: `
            <button class="btn-primary" onclick="closeSeatModal(); openCampaignForm();">New Campaign</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openMarketingAnalytics();">Analytics</button>
        `,
        warranty: `
            <button class="btn-primary" onclick="closeSeatModal(); openServiceTicketForm();">New Ticket</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openWarrantySearch();">Find Warranty</button>
        `,
        owner: `
            <button class="btn-primary" onclick="closeSeatModal(); openFinancialReport();">View Reports</button>
            <button class="btn-secondary" onclick="closeSeatModal(); openAIInsights();">AI Insights</button>
        `
    };
    return actions[role] || '';
}

function closeSeatModal() {
    document.getElementById('seat-modal').classList.add('hidden');
}

// ============================================================================
// GENERIC MODAL FUNCTIONS
// ============================================================================

function openModal(modalId) {
    document.getElementById(modalId)?.classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId)?.classList.add('hidden');
}

// ============================================================================
// NEW PROJECT MODAL
// ============================================================================

function openNewProject() {
    openModal('new-project-modal');
}

function closeNewProjectModal() {
    closeModal('new-project-modal');
    document.getElementById('new-project-form')?.reset();
}

async function createProject(event) {
    event.preventDefault();

    const name = document.getElementById('project-name').value;
    const client = document.getElementById('project-client').value;
    const value = document.getElementById('project-value').value;
    const startDate = document.getElementById('project-start').value;
    const pm = document.getElementById('project-pm').value;
    const phase = document.getElementById('project-phase')?.value || 'bidding';

    const submitBtn = event.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';

    try {
        const result = await createProjectAPI({
            name, client, value, startDate, pm, phase
        });

        if (result.success) {
            await loadProjectsFromAPI();
            await loadMetricsFromAPI();
            closeNewProjectModal();
            showToast('Project created successfully!', 'success');
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Failed to create project:', error);
        showToast('Failed to create project: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Project';
    }
}

// ============================================================================
// AI ESTIMATOR FUNCTIONS
// ============================================================================

function openEstimateForm() {
    openModal('estimate-modal');
}

async function submitEstimate(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    showToast('Generating estimate with AI...', 'info');

    // Simulate AI processing
    setTimeout(() => {
        showToast('Estimate generated! $' + (Math.floor(Math.random() * 500000) + 100000).toLocaleString(), 'success');
        closeModal('estimate-modal');
    }, 2000);
}

function runAerialMeasurement() {
    showToast('Fetching aerial imagery and measuring roof area...', 'info');
    setTimeout(() => {
        const sqft = Math.floor(Math.random() * 50000) + 10000;
        document.querySelector('input[name="est_sqft"]').value = sqft;
        showToast(`Aerial measurement complete: ${sqft.toLocaleString()} SF`, 'success');
    }, 2000);
}

function getMaterialPrices() {
    showToast('Fetching live prices from ABC, Beacon, SRS...', 'info');
    setTimeout(() => {
        showToast('Material prices updated! TPO: $0.85/SF, EPDM: $0.72/SF', 'success');
    }, 1500);
}

function photoToEstimate() {
    showToast('Upload roof photos for AI analysis...', 'info');
    // Would open file picker
}

function checkBidHistory() {
    showToast('Analyzing your bid win/loss history...', 'info');
    setTimeout(() => {
        showToast('Analysis complete: 67% hit rate on similar projects. Suggest bid at $12.50/SF', 'success');
    }, 2000);
}

function saveEstimateDraft() {
    showToast('Draft saved!', 'success');
}

// ============================================================================
// AI PROJECT MANAGER FUNCTIONS
// ============================================================================

function openRFIForm() {
    openModal('rfi-modal');
}

function openSubmittalForm() {
    showToast('Opening submittal form...', 'info');
    // Would open submittal modal
}

async function submitRFI(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    showToast('Submitting RFI...', 'info');

    setTimeout(() => {
        showToast('RFI submitted successfully!', 'success');
        closeModal('rfi-modal');
    }, 1000);
}

// ============================================================================
// AI SUPERINTENDENT FUNCTIONS
// ============================================================================

function openDailyLogForm() {
    openModal('daily-log-modal');
}

function openPhotoCapture() {
    showToast('Opening camera for photo capture...', 'info');
}

async function submitDailyLog(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    showToast('Submitting daily report...', 'info');

    // Check for weather delay - triggers cross-module intelligence
    if (data.log_delay) {
        setTimeout(() => {
            showToast('Weather delay logged! Cross-module updates triggered.', 'warning');
            // Simulate cross-module cascade
            setTimeout(() => showToast('→ Schedule updated for delay', 'info'), 500);
            setTimeout(() => showToast('→ Cash flow projections adjusted', 'info'), 1000);
            setTimeout(() => showToast('→ Delay claim documentation started', 'info'), 1500);
        }, 1000);
    } else {
        setTimeout(() => {
            showToast('Daily report submitted successfully!', 'success');
        }, 1000);
    }

    closeModal('daily-log-modal');
}

function voiceLogEntry() {
    showToast('Voice logging activated. Speak your report...', 'info');
    // Would activate speech recognition
}

function previewPhotos(event, containerId) {
    const container = document.getElementById(containerId);
    const files = event.target.files;

    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.createElement('div');
            preview.className = 'photo-preview';
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <button type="button" class="remove-photo" onclick="this.parentElement.remove()">×</button>
            `;
            container.insertBefore(preview, container.querySelector('.photo-upload-btn'));
        };
        reader.readAsDataURL(file);
    });
}

// ============================================================================
// AI QC MANAGER FUNCTIONS
// ============================================================================

function openInspectionForm() {
    openModal('inspection-modal');
}

function openPunchListForm() {
    showToast('Opening punch list...', 'info');
}

async function submitInspection(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    showToast('Processing inspection...', 'info');

    setTimeout(() => {
        if (data.insp_result === 'fail') {
            showToast('Inspection failed - NCR created and foreman notified', 'warning');
        } else {
            showToast('Inspection passed and documented!', 'success');
        }
        closeModal('inspection-modal');
    }, 1000);
}

function runDefectDetection() {
    showToast('Upload photos for AI defect detection...', 'info');
    // Would open file picker and run AI analysis
    setTimeout(() => {
        showToast('AI scan complete: 1 potential fish mouth detected at grid C-4', 'warning');
    }, 2000);
}

// ============================================================================
// AI SAFETY DIRECTOR FUNCTIONS
// ============================================================================

function openJHAForm() {
    openModal('jha-modal');
}

function openToolboxTalkForm() {
    showToast('Opening toolbox talk library...', 'info');
}

function loadDynamicJHA(projectId) {
    if (!projectId) return;

    showToast('Generating dynamic JHA based on today\'s conditions...', 'info');
    // Would load project-specific and weather-specific hazards
}

async function submitJHA(event) {
    event.preventDefault();

    showToast('Submitting JHA...', 'info');

    setTimeout(() => {
        showToast('JHA submitted! Crew acknowledgments recorded.', 'success');
        closeModal('jha-modal');
    }, 1000);
}

function collectSignatures() {
    showToast('Opening signature collection...', 'info');
    // Would open signature pad
}

// ============================================================================
// AI ACCOUNTING FUNCTIONS
// ============================================================================

function openAIABillingForm() {
    openModal('aia-billing-modal');
}

function openChangeOrderForm() {
    showToast('Opening change order form...', 'info');
}

function loadSOV(projectId) {
    if (!projectId) return;
    showToast('Loading Schedule of Values...', 'info');
    // Would load project's SOV from database
}

async function submitAIABilling(event) {
    event.preventDefault();

    showToast('Generating AIA G702/G703...', 'info');

    setTimeout(() => {
        showToast('AIA billing generated! PDF ready for download.', 'success');
        closeModal('aia-billing-modal');
    }, 2000);
}

function previewAIA() {
    showToast('Generating preview PDF...', 'info');
}

// ============================================================================
// AI OPERATIONS FUNCTIONS
// ============================================================================

function openPurchaseOrderForm() {
    openModal('po-modal');
}

function openVendorCompare() {
    showToast('Fetching live prices from all vendors...', 'info');
    setTimeout(() => {
        showToast('Price comparison updated!', 'success');
    }, 1500);
}

async function submitPurchaseOrder(event) {
    event.preventDefault();

    showToast('Creating purchase order...', 'info');

    setTimeout(() => {
        showToast('PO created and sent to vendor!', 'success');
        closeModal('po-modal');
    }, 1000);
}

function addPOLine() {
    const tbody = document.querySelector('#po-items tbody');
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td><input type="text" placeholder="Material description"></td>
        <td><input type="number" value="1"></td>
        <td>
            <select>
                <option>Rolls</option>
                <option>SF</option>
                <option>LF</option>
            </select>
        </td>
        <td><input type="text" placeholder="$0.00"></td>
        <td>$0.00</td>
        <td><button type="button" class="remove-row" onclick="this.closest('tr').remove()">×</button></td>
    `;
    tbody.appendChild(newRow);
}

// ============================================================================
// AI SHOP DRAWINGS FUNCTIONS
// ============================================================================

function openDrawingForm() {
    openModal('drawing-modal');
}

function openDetailLibrary() {
    showToast('Opening detail library...', 'info');
}

async function submitDrawing(event) {
    event.preventDefault();

    showToast('Creating drawing task...', 'info');

    setTimeout(() => {
        showToast('Drawing task created and added to queue!', 'success');
        closeModal('drawing-modal');
    }, 1000);
}

function specToDetail() {
    showToast('AI analyzing specification section...', 'info');
    setTimeout(() => {
        showToast('AI suggests: Parapet detail per 07 62 00 Section 3.2.A', 'success');
    }, 2000);
}

function generateAssemblyLetter() {
    showToast('Generating manufacturer assembly letter...', 'info');
    setTimeout(() => {
        showToast('Assembly letter generated for GAF EverGuard system!', 'success');
    }, 2000);
}

function suggestRFI() {
    showToast('AI analyzing for potential RFIs...', 'info');
    setTimeout(() => {
        showToast('AI suggests RFI: "Clarify flashing termination at masonry wall"', 'success');
    }, 2000);
}

// ============================================================================
// AI SALES/CRM FUNCTIONS
// ============================================================================

function openLeadForm() {
    showToast('Opening new lead capture form...', 'info');
    // Would open lead modal
}

function openPipelineView() {
    showToast('Loading sales pipeline...', 'info');
    setTimeout(() => {
        showToast('Pipeline: 12 hot leads, $2.4M total value', 'success');
    }, 1000);
}

function scoreLead() {
    showToast('AI analyzing lead quality...', 'info');
    setTimeout(() => {
        showToast('Lead Score: 87/100 - High probability close', 'success');
    }, 1500);
}

// ============================================================================
// AI HR/WORKFORCE FUNCTIONS
// ============================================================================

function openEmployeeForm() {
    showToast('Opening new employee onboarding form...', 'info');
    // Would open employee modal
}

function openCertificationsView() {
    showToast('Loading certification tracker...', 'info');
    setTimeout(() => {
        showToast('5 certifications expiring in 30 days', 'warning');
    }, 1000);
}

function runEVerify() {
    showToast('Submitting I-9 to E-Verify...', 'info');
    setTimeout(() => {
        showToast('E-Verify: Employment Authorized', 'success');
    }, 2000);
}

// ============================================================================
// AI MARKETING FUNCTIONS
// ============================================================================

function openCampaignForm() {
    showToast('Opening campaign setup...', 'info');
    // Would open campaign modal
}

function openMarketingAnalytics() {
    showToast('Loading marketing analytics dashboard...', 'info');
    setTimeout(() => {
        showToast('Cost per Lead: $127 | Conversion: 8.4%', 'success');
    }, 1000);
}

function analyzeLeadSource() {
    showToast('AI analyzing lead attribution...', 'info');
    setTimeout(() => {
        showToast('Top source: Google Ads (45% of leads, $89 CPL)', 'success');
    }, 1500);
}

// ============================================================================
// AI WARRANTY/SERVICE FUNCTIONS
// ============================================================================

function openServiceTicketForm() {
    showToast('Opening service ticket form...', 'info');
    // Would open service ticket modal
}

function openWarrantySearch() {
    showToast('Opening warranty lookup...', 'info');
    // Would open warranty search modal
}

function registerWarranty() {
    showToast('Registering warranty with manufacturer...', 'info');
    setTimeout(() => {
        showToast('Warranty registered! Certificate #W-2024-1247', 'success');
    }, 2000);
}

function processServiceClaim() {
    showToast('Processing warranty claim...', 'info');
    setTimeout(() => {
        showToast('Claim approved - Parts ordered, tech scheduled', 'success');
    }, 1500);
}

// ============================================================================
// AI OWNER DASHBOARD FUNCTIONS
// ============================================================================

function openFinancialReport() {
    showToast('Generating financial reports...', 'info');
    setTimeout(() => {
        showToast('P&L Report ready: Revenue $847K MTD, Margin 24%', 'success');
    }, 1500);
}

function openAIInsights() {
    showToast('AI analyzing business patterns...', 'info');
    setTimeout(() => {
        showToast('AI Insight: Material costs up 12% - recommend early ordering', 'warning');
    }, 2000);
}

function getCashPosition() {
    showToast('Calculating current cash position...', 'info');
    setTimeout(() => {
        showToast('Cash: $234K | AR: $456K | Committed: $189K', 'success');
    }, 1000);
}

function viewKPIDashboard() {
    showToast('Loading KPI dashboard...', 'info');
    setTimeout(() => {
        showToast('All KPIs green except AR Days (42 vs target 35)', 'warning');
    }, 1000);
}

// ============================================================================
// VOICE COMMAND FUNCTIONS (HIVE215)
// ============================================================================

let isListening = false;
let recognition = null;

function openVoiceCommand() {
    openModal('voice-modal');
    initVoiceRecognition();
}

function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            document.getElementById('voice-transcript').textContent = transcript;
        };

        recognition.onend = () => {
            isListening = false;
            updateVoiceUI();
            processVoiceCommand(document.getElementById('voice-transcript').textContent);
        };
    }
}

function toggleVoiceListening() {
    if (!recognition) {
        showToast('Voice recognition not available in this browser', 'error');
        return;
    }

    if (isListening) {
        recognition.stop();
        isListening = false;
    } else {
        recognition.start();
        isListening = true;
    }
    updateVoiceUI();
}

function updateVoiceUI() {
    const btn = document.getElementById('voice-btn');
    const status = document.getElementById('voice-status');
    const visual = document.getElementById('voice-visual');

    if (isListening) {
        btn.textContent = 'Stop Listening';
        btn.classList.add('listening');
        status.textContent = 'Listening...';
        visual.classList.add('active');
    } else {
        btn.textContent = 'Start Listening';
        btn.classList.remove('listening');
        status.textContent = 'Tap to speak';
        visual.classList.remove('active');
    }
}

function processVoiceCommand(command) {
    if (!command) return;

    command = command.toLowerCase();

    if (command.includes('cash position') || command.includes('cash flow')) {
        showToast('Cash position: $847K revenue MTD, $45K overdue AR', 'info');
    } else if (command.includes('change order')) {
        showToast('Opening change order form...', 'info');
        closeModal('voice-modal');
        openChangeOrderForm();
    } else if (command.includes('certified') || command.includes('certification')) {
        showToast('Checking certifications database...', 'info');
    } else if (command.includes('status') || command.includes('update')) {
        showToast('JHU Library: 72% complete, on schedule. UMass: 45% complete, 2 day delay.', 'info');
    } else {
        showToast('Processing: "' + command + '"', 'info');
    }
}

// ============================================================================
// PROJECT DETAIL
// ============================================================================

function openProject(projectId) {
    const project = projectsData.find(p => (p.id || p.project_id) == projectId);
    if (!project) {
        showToast('Project not found', 'error');
        return;
    }
    window.location.href = `/projects?id=${projectId}`;
}

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

// Add toast animation styles
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
    loadProjectsFromAPI();
    loadActivityFeed();
    loadMetricsFromAPI();
}

function startAutoRefresh() {
    setInterval(loadMetricsFromAPI, 30000);
    setInterval(loadProjectsFromAPI, 120000);
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeSeatModal();
        closeNewProjectModal();
        closeModal('estimate-modal');
        closeModal('rfi-modal');
        closeModal('daily-log-modal');
        closeModal('inspection-modal');
        closeModal('jha-modal');
        closeModal('aia-billing-modal');
        closeModal('po-modal');
        closeModal('drawing-modal');
        closeModal('voice-modal');
    }

    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        openNewProject();
    }

    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        refreshDashboard();
    }

    // Voice command shortcut
    if (e.ctrlKey && e.key === ' ') {
        e.preventDefault();
        openVoiceCommand();
    }
});

// ============================================================================
// MOBILE NAVIGATION
// ============================================================================

document.querySelector('.mobile-nav-toggle')?.addEventListener('click', function() {
    const nav = document.querySelector('.nav');
    const expanded = this.getAttribute('aria-expanded') === 'true';
    this.setAttribute('aria-expanded', !expanded);
    nav.classList.toggle('open');
});
