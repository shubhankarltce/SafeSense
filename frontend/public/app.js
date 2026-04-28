document.addEventListener('DOMContentLoaded', () => {
    console.log('SafeSense Dashboard Initializing...');

    const wsUrl = "wss://safesense-7ckn.onrender.com/ws/dashboard";

    let socket;

    function connect() {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log('WebSocket connection established.');
            updateSystemStatus(true);
            showToast('info', 'Connected', 'Live connection to SafeSense established.');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received data:', data);
            // Route data to appropriate handler
            if (data.type) {
                switch (data.type) {
                    case 'full_state':
                        // A full update of the entire dashboard state
                        updateIncidents(data.incidents);
                        updateStaff(data.staff);
                        updateZones(data.zones);
                        updateChecklist(data.checklist);
                        updateGuestCounts(data.zones);
                        break;
                    case 'incident_new':
                        flashAlert();
                        showToast('danger', `New Incident: ${data.incident.type.toUpperCase()}`, `Detected in ${data.incident.zone_id}`);
                        // request full update to resync
                        break;
                    case 'zone_update':
                        updateZone(data.zone);
                        updateGuestCounts(getAllZones());
                        break;
                    case 'staff_update':
                         // To be implemented
                        break;
                    case 'alert':
                        showToast(data.level, data.title, data.message);
                        if (data.level === 'danger') {
                            flashAlert();
                        }
                        break;
                     case 'checklist_update':
                        updateChecklist(data.checklist);
                        break;
                    case 'voice_prompt':
                        updateVoicePrompt(data.message, data.can_play);
                        break;
                    default:
                        console.warn('Unknown message type:', data.type);
                }
            }
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed. Reconnecting...');
            updateSystemStatus(false);
            showToast('warning', 'Connection Lost', 'Attempting to reconnect...');
            setTimeout(connect, 3000); // Reconnect after 3 seconds
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateSystemStatus(false);
            showToast('danger', 'Connection Error', 'Could not establish live connection.');
            socket.close();
        };
    }

    // --- UI Selectors ---
    const systemStatusText = document.querySelector('#systemStatus span:last-child');
    const statusDot = document.querySelector('.status-dot');
    const toastContainer = document.getElementById('toastContainer');
    const clockEl = document.getElementById('systemClock');
    const dateEl = document.getElementById('systemDate');
    const alertFlash = document.getElementById('alertFlash');

    // --- Core UI Functions ---

    function updateSystemStatus(isOnline) {
        if (isOnline) {
            statusDot.classList.add('status-online');
            statusDot.style.background = 'var(--safe)';
            systemStatusText.textContent = 'System Online';
        } else {
            statusDot.classList.remove('status-online');
            statusDot.style.background = 'var(--warning)';
            systemStatusText.textContent = 'Connecting...';
        }
    }

    function showToast(type, title, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            danger: '🚨'
        };
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || ''}</div>
            <div class="toast-body">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
    
    function flashAlert() {
        alertFlash.classList.add('active');
        setTimeout(() => {
            alertFlash.classList.remove('active');
        }, 700);
    }

    function updateClock() {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
        dateEl.textContent = now.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }
    
    // --- Data Update Functions ---

    function updateZones(zones) {
        zones.forEach(updateZone);
    }

    function updateZone(zone) {
        const zoneEl = document.getElementById(`svg_${zone.id}`);
        const countEl = document.getElementById(`count_${zone.id}`);
        if (zoneEl) {
            zoneEl.classList.remove('zone-safe', 'zone-warning', 'zone-danger');
            zoneEl.classList.add(`zone-${zone.status}`);
        }
        if (countEl) {
            countEl.textContent = `?? ${zone.guest_count}`;
        }
    }
    
    function updateIncidents(incidents) {
        const list = document.getElementById('incidentsList');
        const count = document.getElementById('incidentCount');
        
        list.innerHTML = ''; // Clear list
        if (incidents.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#334155" stroke-width="1.5"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    <p>No active incidents</p>
                    <span>All zones are safe</span>
                </div>`;
            count.textContent = '0';
            count.classList.remove('active');
            return;
        }

        count.textContent = incidents.length;
        count.classList.add('active');

        incidents.forEach(incident => {
            const item = document.createElement('div');
            item.className = 'incident-item';
            const icon = { fire: '??', medical: '??', panic: '??', hazard: '??' };
            item.innerHTML = `
                <div class="incident-icon ${incident.type}">${icon[incident.type] || '??'}</div>
                <div class="incident-info">
                    <h4>${incident.type.toUpperCase()} in ${incident.zone_id}</h4>
                    <p>${new Date(incident.timestamp).toLocaleTimeString()}</p>
                </div>
            `;
            list.appendChild(item);
        });
    }
    
    function updateStaff(staffList) {
        const list = document.getElementById('staffList');
        list.innerHTML = '';
        if (staffList.length === 0) {
            list.innerHTML = '<div class="loading-skeleton">No staff found.</div>';
            return;
        }
        staffList.forEach(staff => {
            const item = document.createElement('div');
            item.className = 'staff-item';
            item.innerHTML = `
                <div class="staff-info">
                    <div class="staff-avatar">${staff.name.charAt(0)}</div>
                    <div>
                        <div class="staff-name">${staff.name}</div>
                        <div class="staff-role">${staff.role.replace('_', ' ')}</div>
                    </div>
                </div>
                <div class="status-pill status-${staff.status}">${staff.status.replace('_', ' ')}</div>
            `;
            list.appendChild(item);
        });
    }
    
    function updateChecklist(checklist) {
        const body = document.getElementById('checklistBody');
        const progressContainer = document.getElementById('checklistProgress');
        
        if (!checklist || checklist.tasks.length === 0) {
            body.innerHTML = `
                <div class="empty-state small">
                    <p>No active checklist</p>
                    <span>Checklists auto-populate on incidents</span>
                </div>`;
            progressContainer.style.display = 'none';
            return;
        }

        body.innerHTML = '';
        progressContainer.style.display = 'flex';
        
        let completed = 0;
        checklist.tasks.forEach(task => {
            if (task.completed) completed++;
            const item = document.createElement('div');
            item.className = `checklist-item ${task.completed ? 'checked' : ''}`;
            item.innerHTML = `
                <div class="checklist-checkbox"></div>
                <div class="checklist-text">${task.text}</div>
            `;
            body.appendChild(item);
        });

        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const percentage = (completed / checklist.tasks.length) * 100;
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${completed}/${checklist.tasks.length}`;
    }
    
    function updateGuestCounts(zones) {
        let total = 0, danger = 0;
        zones.forEach(zone => {
            total += zone.guest_count;
            if(zone.status === 'danger' || zone.status === 'warning') {
                danger += zone.guest_count;
            }
        });
        document.getElementById('totalGuests').textContent = total;
        document.getElementById('safeGuests').textContent = total - danger;
        document.getElementById('dangerGuests').textContent = danger;
    }

    function updateVoicePrompt(message, canPlay) {
        document.getElementById('voiceMessage').textContent = message;
        document.getElementById('voicePlayBtn').disabled = !canPlay;
    }

    // --- Initializers ---
    
    updateClock();
    setInterval(updateClock, 1000);

    // Initial empty states
    updateIncidents([]);
    updateStaff([]);
    updateChecklist(null);

    connect(); // Start the WebSocket connection

    console.log('SafeSense Dashboard Ready.');
});
