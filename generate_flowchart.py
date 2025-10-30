"""
MedCore AI - System Flowchart Generator
Generates visual flowcharts for the system architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Colors
color_patient = '#3b82f6'  # Blue
color_doctor = '#10b981'   # Green
color_pharmacy = '#f59e0b' # Orange
color_backend = '#6366f1'  # Indigo
color_ai = '#8b5cf6'       # Purple
color_db = '#ec4899'       # Pink

# Title
ax.text(5, 11.5, 'MedCore AI - Smart City Healthcare System', 
        fontsize=20, fontweight='bold', ha='center')
ax.text(5, 11, 'Complete System Architecture & Data Flow', 
        fontsize=14, ha='center', style='italic')

# Layer 1: User Portals
y_portals = 9.5

# Patient Portal
patient_box = FancyBboxPatch((0.5, y_portals), 2, 1, 
                             boxstyle="round,pad=0.1", 
                             edgecolor=color_patient, 
                             facecolor=color_patient, 
                             alpha=0.3, linewidth=2)
ax.add_patch(patient_box)
ax.text(1.5, y_portals + 0.7, 'PATIENT', fontsize=12, fontweight='bold', ha='center')
ax.text(1.5, y_portals + 0.4, 'PORTAL', fontsize=10, ha='center')
ax.text(1.5, y_portals + 0.1, '• AI Chat\n• Video Call\n• Track Rx', 
        fontsize=8, ha='center', va='top')

# Doctor Portal
doctor_box = FancyBboxPatch((3.5, y_portals), 2, 1, 
                            boxstyle="round,pad=0.1", 
                            edgecolor=color_doctor, 
                            facecolor=color_doctor, 
                            alpha=0.3, linewidth=2)
ax.add_patch(doctor_box)
ax.text(4.5, y_portals + 0.7, 'DOCTOR', fontsize=12, fontweight='bold', ha='center')
ax.text(4.5, y_portals + 0.4, 'PORTAL', fontsize=10, ha='center')
ax.text(4.5, y_portals + 0.1, '• AI Analysis\n• Send Rx\n• Consult', 
        fontsize=8, ha='center', va='top')

# Pharmacy Portal
pharmacy_box = FancyBboxPatch((6.5, y_portals), 2, 1, 
                              boxstyle="round,pad=0.1", 
                              edgecolor=color_pharmacy, 
                              facecolor=color_pharmacy, 
                              alpha=0.3, linewidth=2)
ax.add_patch(pharmacy_box)
ax.text(7.5, y_portals + 0.7, 'PHARMACY', fontsize=12, fontweight='bold', ha='center')
ax.text(7.5, y_portals + 0.4, 'PORTAL', fontsize=10, ha='center')
ax.text(7.5, y_portals + 0.1, '• View Rx\n• Update Status\n• Messages', 
        fontsize=8, ha='center', va='top')

# Arrows from portals to backend
ax.annotate('', xy=(1.5, 8), xytext=(1.5, y_portals),
            arrowprops=dict(arrowstyle='->', lw=2, color=color_patient))
ax.annotate('', xy=(4.5, 8), xytext=(4.5, y_portals),
            arrowprops=dict(arrowstyle='->', lw=2, color=color_doctor))
ax.annotate('', xy=(7.5, 8), xytext=(7.5, y_portals),
            arrowprops=dict(arrowstyle='->', lw=2, color=color_pharmacy))

# Layer 2: Backend Server
y_backend = 7
backend_box = FancyBboxPatch((1, y_backend), 7, 1.5, 
                             boxstyle="round,pad=0.1", 
                             edgecolor=color_backend, 
                             facecolor=color_backend, 
                             alpha=0.3, linewidth=3)
ax.add_patch(backend_box)
ax.text(4.5, y_backend + 1.1, 'FLASK WEB SERVER (app.py)', 
        fontsize=14, fontweight='bold', ha='center')
ax.text(4.5, y_backend + 0.7, 'Backend API & Business Logic', 
        fontsize=10, ha='center', style='italic')
ax.text(4.5, y_backend + 0.3, 'Routes: /patient, /doctor, /pharmacy', 
        fontsize=9, ha='center')
ax.text(4.5, y_backend + 0.05, 'APIs: /api/patient-chat, /api/send_prescription, /api/get_prescriptions', 
        fontsize=8, ha='center')

# Arrows from backend to data layer
ax.annotate('', xy=(2, 5.5), xytext=(2.5, y_backend),
            arrowprops=dict(arrowstyle='<->', lw=2, color=color_db))
ax.annotate('', xy=(4.5, 5.5), xytext=(4.5, y_backend),
            arrowprops=dict(arrowstyle='<->', lw=2, color='#64748b'))
ax.annotate('', xy=(7, 5.5), xytext=(6.5, y_backend),
            arrowprops=dict(arrowstyle='<->', lw=2, color=color_ai))

# Layer 3: Data & Services
y_data = 4

# Database
db_box = FancyBboxPatch((0.5, y_data), 2.5, 1.5, 
                        boxstyle="round,pad=0.1", 
                        edgecolor=color_db, 
                        facecolor=color_db, 
                        alpha=0.3, linewidth=2)
ax.add_patch(db_box)
ax.text(1.75, y_data + 1.1, 'SQLite', fontsize=12, fontweight='bold', ha='center')
ax.text(1.75, y_data + 0.8, 'DATABASE', fontsize=10, ha='center')
ax.text(1.75, y_data + 0.3, '• Patients\n• Vitals\n• Lab Results\n• History', 
        fontsize=8, ha='center', va='top')

# JSON Files
json_box = FancyBboxPatch((3.5, y_data), 2, 1.5, 
                          boxstyle="round,pad=0.1", 
                          edgecolor='#64748b', 
                          facecolor='#64748b', 
                          alpha=0.3, linewidth=2)
ax.add_patch(json_box)
ax.text(4.5, y_data + 1.1, 'JSON', fontsize=12, fontweight='bold', ha='center')
ax.text(4.5, y_data + 0.8, 'FILES', fontsize=10, ha='center')
ax.text(4.5, y_data + 0.3, '• Prescriptions\n• Messages\n• Sessions', 
        fontsize=8, ha='center', va='top')

# Gemini AI
ai_box = FancyBboxPatch((6, y_data), 2.5, 1.5, 
                        boxstyle="round,pad=0.1", 
                        edgecolor=color_ai, 
                        facecolor=color_ai, 
                        alpha=0.3, linewidth=2)
ax.add_patch(ai_box)
ax.text(7.25, y_data + 1.1, 'Gemini AI', fontsize=12, fontweight='bold', ha='center')
ax.text(7.25, y_data + 0.8, 'API', fontsize=10, ha='center')
ax.text(7.25, y_data + 0.3, '• Patient Chat\n• AI Analysis\n• Diagnosis', 
        fontsize=8, ha='center', va='top')

# Data Flow Example
y_flow = 2
ax.text(5, y_flow + 0.8, 'Example: Patient Chat Flow', 
        fontsize=12, fontweight='bold', ha='center')

flow_steps = [
    (1, 'Patient\nTypes\nQuestion'),
    (2.5, 'Frontend\nSends\nRequest'),
    (4, 'Backend\nProcesses'),
    (5.5, 'Gemini\nGenerates\nResponse'),
    (7, 'Backend\nFormats'),
    (8.5, 'Frontend\nDisplays')
]

for i, (x, text) in enumerate(flow_steps):
    # Box
    step_box = FancyBboxPatch((x-0.4, y_flow-0.3), 0.8, 0.6, 
                              boxstyle="round,pad=0.05", 
                              edgecolor='#1e293b', 
                              facecolor='#f1f5f9', 
                              linewidth=1.5)
    ax.add_patch(step_box)
    ax.text(x, y_flow, text, fontsize=7, ha='center', va='center')
    
    # Arrow to next step
    if i < len(flow_steps) - 1:
        ax.annotate('', xy=(flow_steps[i+1][0]-0.4, y_flow), 
                   xytext=(x+0.4, y_flow),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='#1e293b'))

# Smart City Benefits
y_benefits = 0.5
benefits = [
    ('Digital', '100% Paperless'),
    ('Efficient', '70% Faster'),
    ('Accessible', '24/7 Available'),
    ('Sustainable', 'Green Operations'),
    ('Data-Driven', 'Real-time Analytics')
]

benefit_width = 1.6
start_x = 0.5
for i, (title, desc) in enumerate(benefits):
    x = start_x + i * benefit_width
    benefit_box = FancyBboxPatch((x, y_benefits), benefit_width-0.1, 0.4, 
                                 boxstyle="round,pad=0.05", 
                                 edgecolor='#0891b2', 
                                 facecolor='#cffafe', 
                                 linewidth=1.5)
    ax.add_patch(benefit_box)
    ax.text(x + (benefit_width-0.1)/2, y_benefits + 0.28, title, 
            fontsize=8, fontweight='bold', ha='center')
    ax.text(x + (benefit_width-0.1)/2, y_benefits + 0.12, desc, 
            fontsize=7, ha='center')

# Legend
legend_elements = [
    mpatches.Patch(facecolor=color_patient, alpha=0.3, edgecolor=color_patient, label='Patient Portal'),
    mpatches.Patch(facecolor=color_doctor, alpha=0.3, edgecolor=color_doctor, label='Doctor Portal'),
    mpatches.Patch(facecolor=color_pharmacy, alpha=0.3, edgecolor=color_pharmacy, label='Pharmacy Portal'),
    mpatches.Patch(facecolor=color_backend, alpha=0.3, edgecolor=color_backend, label='Backend Server'),
    mpatches.Patch(facecolor=color_ai, alpha=0.3, edgecolor=color_ai, label='AI Services'),
    mpatches.Patch(facecolor=color_db, alpha=0.3, edgecolor=color_db, label='Database')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

# Footer
ax.text(5, 0.1, 'MedCore AI - Smart City Healthcare Platform', 
        fontsize=10, ha='center', style='italic', color='#64748b')

plt.tight_layout()
plt.savefig('MedCore_AI_System_Flowchart.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("✅ Flowchart saved as 'MedCore_AI_System_Flowchart.png'")
print("📊 High-resolution diagram created successfully!")
plt.show()
