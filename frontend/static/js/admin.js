let currentAppointmentId = null;
let currentAlertId = null;
let allUsers = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');

    if (tabName === 'dashboard') loadDashboard();
    if (tabName === 'users') loadUsers();
    if (tabName === 'appointments') loadAppointments();
    if (tabName === 'pharmacy') loadPrescriptions();
    if (tabName === 'alerts') loadEmergencyAlerts();
}

// Load Dashboard
async function loadDashboard() {
    try {
        const response = await fetch('/api/admin/analytics');
        const data = await response.json();
        
        if (data.status === 'success') {
            const analytics = data.analytics;
            
            document.getElementById('dashboardStats').innerHTML = `
                <div class="stat-card blue">
                    <div class="icon"><i class="fas fa-users"></i></div>
                    <h3>Total Users</h3>
                    <div class="number">${analytics.users.total}</div>
                </div>
                <div class="stat-card green">
                    <div class="icon"><i class="fas fa-user-injured"></i></div>
                    <h3>Patients</h3>
                    <div class="number">${analytics.users.patients}</div>
                </div>
                <div class="stat-card orange">
                    <div class="icon"><i class="fas fa-user-md"></i></div>
                    <h3>Doctors</h3>
                    <div class="number">${analytics.users.doctors}</div>
                </div>
                <div class="stat-card red">
                    <div class="icon"><i class="fas fa-calendar-check"></i></div>
                    <h3>Today's Appointments</h3>
                    <div class="number">${analytics.appointments.today}</div>
                </div>
                <div class="stat-card blue">
                    <div class="icon"><i class="fas fa-calendar"></i></div>
                    <h3>Total Appointments</h3>
                    <div class="number">${analytics.appointments.total}</div>
                </div>
                <div class="stat-card green">
                    <div class="icon"><i class="fas fa-check-circle"></i></div>
                    <h3>Completed</h3>
                    <div class="number">${analytics.appointments.completed}</div>
                </div>
                <div class="stat-card orange">
                    <div class="icon"><i class="fas fa-prescription-bottle"></i></div>
                    <h3>Today's Prescriptions</h3>
                    <div class="number">${analytics.prescriptions.today}</div>
                </div>
                <div class="stat-card red">
                    <div class="icon"><i class="fas fa-pills"></i></div>
                    <h3>Pending Medicines</h3>
                    <div class="number">${analytics.prescriptions.pending}</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load Users
async function loadUsers() {
    try {
        const roleFilter = document.getElementById('roleFilter').value;
        const url = roleFilter ? `/api/admin/users?role=${roleFilter}` : '/api/admin/users';
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success') {
            allUsers = data.users;
            displayUsers(allUsers);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.user_id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td><span class="badge">${user.role}</span></td>
            <td><span class="badge ${user.status}">${user.status}</span></td>
            <td>
                ${user.status === 'active' ? 
                    `<button class="btn btn-warning" onclick="updateUserStatus('${user.id}', 'inactive')">Deactivate</button>` :
                    `<button class="btn btn-success" onclick="updateUserStatus('${user.id}', 'active')">Activate</button>`
                }
                <button class="btn btn-danger" onclick="deleteUser('${user.id}')">Remove</button>
            </td>
        </tr>
    `).join('');
}

async function updateUserStatus(userId, status) {
    if (!confirm(`Are you sure you want to ${status} this user?`)) return;
    
    try {
        const response = await fetch(`/api/admin/user/${userId}/status`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert(data.message);
            loadUsers();
        }
    } catch (error) {
        console.error('Error updating user status:', error);
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to remove this user?')) return;
    
    try {
        const response = await fetch(`/api/admin/user/${userId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert(data.message);
            loadUsers();
        }
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}

// Load Appointments
async function loadAppointments() {
    try {
        const statusFilter = document.getElementById('appointmentStatusFilter').value;
        const url = statusFilter ? `/api/admin/appointments?status=${statusFilter}` : '/api/admin/appointments';
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAppointments(data.appointments);
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

function displayAppointments(appointments) {
    const tbody = document.getElementById('appointmentsTableBody');
    
    if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No appointments found</td></tr>';
        return;
    }
    
    tbody.innerHTML = appointments.map(apt => `
        <tr>
            <td>${apt.id}</td>
            <td>${apt.patient_name}</td>
            <td>${apt.doctor_name}</td>
            <td>${apt.appointment_date}</td>
            <td><span class="badge ${apt.status}">${apt.status}</span></td>
            <td>
                <button class="btn btn-primary" onclick="openReassignModal('${apt.id}')">Reassign</button>
            </td>
        </tr>
    `).join('');
}

function openReassignModal(appointmentId) {
    currentAppointmentId = appointmentId;
    document.getElementById('reassignModal').classList.add('active');
}

async function confirmReassign() {
    const newDoctor = document.getElementById('newDoctorName').value;
    if (!newDoctor) {
        alert('Please enter doctor name');
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/appointment/${currentAppointmentId}/reassign`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({doctor_name: newDoctor})
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert(data.message);
            closeModal('reassignModal');
            loadAppointments();
        }
    } catch (error) {
        console.error('Error reassigning appointment:', error);
    }
}

// Load Prescriptions
async function loadPrescriptions() {
    try {
        const response = await fetch('/api/admin/prescriptions/stats');
        const data = await response.json();
        
        if (data.status === 'success') {
            document.getElementById('pharmacyStats').innerHTML = `
                <div class="stat-card blue">
                    <div class="icon"><i class="fas fa-prescription"></i></div>
                    <h3>Total Prescriptions</h3>
                    <div class="number">${data.total_count}</div>
                </div>
                <div class="stat-card orange">
                    <div class="icon"><i class="fas fa-clock"></i></div>
                    <h3>Pending</h3>
                    <div class="number">${data.pending_count}</div>
                </div>
                <div class="stat-card green">
                    <div class="icon"><i class="fas fa-check"></i></div>
                    <h3>Ready</h3>
                    <div class="number">${data.ready_count}</div>
                </div>
                <div class="stat-card red">
                    <div class="icon"><i class="fas fa-truck"></i></div>
                    <h3>Delivered</h3>
                    <div class="number">${data.delivered_count}</div>
                </div>
            `;
            
            displayPrescriptions(data.prescriptions);
        }
    } catch (error) {
        console.error('Error loading prescriptions:', error);
    }
}

function displayPrescriptions(prescriptions) {
    const tbody = document.getElementById('prescriptionsTableBody');
    
    if (prescriptions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No prescriptions found</td></tr>';
        return;
    }
    
    tbody.innerHTML = prescriptions.map(rx => `
        <tr>
            <td>${rx.id}</td>
            <td>${rx.patient_name}</td>
            <td><span class="badge ${rx.status}">${rx.status}</span></td>
            <td><span class="badge ${rx.priority}">${rx.priority}</span></td>
            <td>${new Date(rx.created_at).toLocaleDateString()}</td>
        </tr>
    `).join('');
}

// Load Emergency Alerts
async function loadEmergencyAlerts() {
    try {
        const response = await fetch('/api/admin/emergency-alerts');
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAlerts(data.alerts);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function displayAlerts(alerts) {
    const tbody = document.getElementById('alertsTableBody');
    
    if (alerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No emergency alerts</td></tr>';
        return;
    }
    
    tbody.innerHTML = alerts.map(alert => `
        <tr>
            <td>${alert.id}</td>
            <td>${alert.patient_name}</td>
            <td>${alert.condition}</td>
            <td><span class="badge ${alert.severity}">${alert.severity}</span></td>
            <td><span class="badge ${alert.status}">${alert.status}</span></td>
            <td>
                ${alert.status === 'pending' ? 
                    `<button class="btn btn-danger" onclick="openForwardModal('${alert.id}')">Forward</button>` : 
                    alert.hospital_name || 'Resolved'
                }
                ${alert.status !== 'resolved' ? 
                    `<button class="btn btn-success" onclick="resolveAlert('${alert.id}')">Resolve</button>` : ''
                }
            </td>
        </tr>
    `).join('');
}

function openForwardModal(alertId) {
    currentAlertId = alertId;
    document.getElementById('forwardAlertModal').classList.add('active');
}

async function confirmForwardAlert() {
    const hospital = document.getElementById('hospitalName').value;
    if (!hospital) {
        alert('Please enter hospital name');
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/emergency-alert/${currentAlertId}/forward`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({hospital_name: hospital})
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert(data.message);
            closeModal('forwardAlertModal');
            loadEmergencyAlerts();
        }
    } catch (error) {
        console.error('Error forwarding alert:', error);
    }
}

async function resolveAlert(alertId) {
    if (!confirm('Mark this alert as resolved?')) return;
    
    try {
        const response = await fetch(`/api/admin/emergency-alert/${alertId}/resolve`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert(data.message);
            loadEmergencyAlerts();
        }
    } catch (error) {
        console.error('Error resolving alert:', error);
    }
}

// Load Patient Analytics
async function loadPatientAnalytics() {
    const patientId = document.getElementById('patientIdInput').value;
    if (!patientId) {
        alert('Please enter a patient ID');
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/patient-analytics/${patientId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const analytics = data.analytics;
            
            document.getElementById('patientAnalyticsContent').innerHTML = `
                <div class="patient-analytics-card">
                    <h4><i class="fas fa-user"></i> Patient: ${analytics.patient_id}</h4>
                    <div class="analytics-grid">
                        <div class="analytics-item">
                            <div class="label">Total Appointments</div>
                            <div class="value">${analytics.appointments.total}</div>
                        </div>
                        <div class="analytics-item">
                            <div class="label">Completed</div>
                            <div class="value">${analytics.appointments.completed}</div>
                        </div>
                        <div class="analytics-item">
                            <div class="label">Scheduled</div>
                            <div class="value">${analytics.appointments.scheduled}</div>
                        </div>
                        <div class="analytics-item">
                            <div class="label">Total Prescriptions</div>
                            <div class="value">${analytics.prescriptions.total}</div>
                        </div>
                        <div class="analytics-item">
                            <div class="label">Delivered</div>
                            <div class="value">${analytics.prescriptions.delivered}</div>
                        </div>
                        <div class="analytics-item">
                            <div class="label">Pending</div>
                            <div class="value">${analytics.prescriptions.pending}</div>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading patient analytics:', error);
        document.getElementById('patientAnalyticsContent').innerHTML = 
            '<p style="text-align:center;color:#999;">Patient not found or error loading data</p>';
    }
}

// Modal functions
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
