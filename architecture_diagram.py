#!/usr/bin/env python3
"""
MedCore AI - Enterprise Medical Platform Architecture Diagram Generator
Creates a comprehensive block diagram showing current and future architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_architecture_diagram():
    """Create comprehensive MedCore AI architecture diagram"""
    
    # Create figure with larger size for detailed diagram
    fig, ax = plt.subplots(1, 1, figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Color scheme - Professional medical colors
    colors = {
        'client': '#2E86AB',      # Medical blue
        'api': '#A23B72',         # Medical purple
        'ai': '#F18F01',          # Medical orange
        'data': '#C73E1D',        # Medical red
        'infra': '#4A5568',       # Gray
        'security': '#38A169',    # Green
        'future': '#805AD5',      # Purple for future components
        'realtime': '#00B4D8'     # Cyan for realtime
    }
    
    # Title
    ax.text(10, 13.5, 'MedCore AI - Enterprise Medical Platform Architecture', 
            fontsize=24, fontweight='bold', ha='center',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    # Legend
    legend_y = 12.8
    legend_items = [
        ('Current Components', colors['client']),
        ('Future Components', colors['future']),
        ('AI/ML Layer', colors['ai']),
        ('Security & Compliance', colors['security'])
    ]
    
    for i, (label, color) in enumerate(legend_items):
        ax.add_patch(patches.Rectangle((0.5 + i*4, legend_y), 0.3, 0.2, 
                                     facecolor=color, alpha=0.7))
        ax.text(0.9 + i*4, legend_y + 0.1, label, fontsize=10, va='center')
    
    # CLIENT LAYER (Top)
    client_y = 11.5
    
    # Patient Portal
    patient_box = FancyBboxPatch((0.5, client_y), 3.5, 1, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['client'], alpha=0.8)
    ax.add_patch(patient_box)
    ax.text(2.25, client_y + 0.7, 'Patient Portal', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2.25, client_y + 0.4, 'Web/Mobile App', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.25, client_y + 0.1, 'HTML5, CSS3, JS', fontsize=9, ha='center', va='center', color='white')
    
    # Doctor Dashboard
    doctor_box = FancyBboxPatch((4.5, client_y), 3.5, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['client'], alpha=0.8)
    ax.add_patch(doctor_box)
    ax.text(6.25, client_y + 0.7, 'Doctor Dashboard', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(6.25, client_y + 0.4, 'Professional UI', fontsize=10, ha='center', va='center', color='white')
    ax.text(6.25, client_y + 0.1, 'Medical Icons, Charts', fontsize=9, ha='center', va='center', color='white')
    
    # Mobile Apps (Future)
    mobile_box = FancyBboxPatch((8.5, client_y), 3, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['future'], alpha=0.8)
    ax.add_patch(mobile_box)
    ax.text(10, client_y + 0.7, 'Mobile Apps', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(10, client_y + 0.4, 'iOS/Android', fontsize=10, ha='center', va='center', color='white')
    ax.text(10, client_y + 0.1, 'React Native/Flutter', fontsize=9, ha='center', va='center', color='white')
    
    # Video/Audio Calling (Future)
    video_box = FancyBboxPatch((12, client_y), 3.5, 1, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['realtime'], alpha=0.8)
    ax.add_patch(video_box)
    ax.text(13.75, client_y + 0.7, 'Video/Audio Calls', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(13.75, client_y + 0.4, 'WebRTC + Twilio/Agora', fontsize=10, ha='center', va='center', color='white')
    ax.text(13.75, client_y + 0.1, 'TURN/STUN Servers', fontsize=9, ha='center', va='center', color='white')
    
    # SECURITY & COMPLIANCE LAYER
    security_y = 10
    security_box = FancyBboxPatch((0.5, security_y), 15, 0.8, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['security'], alpha=0.8)
    ax.add_patch(security_box)
    ax.text(8, security_y + 0.4, 'Security & Compliance Layer', fontsize=14, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(8, security_y + 0.1, 'HIPAA/FDA Compliance • JWT/OAuth2 • Encryption • Audit Logs • WAF • RBAC', 
            fontsize=10, ha='center', va='center', color='white')
    
    # API GATEWAY & BACKEND SERVICES
    api_y = 8.5
    
    # API Gateway
    gateway_box = FancyBboxPatch((0.5, api_y), 4, 1.2, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['api'], alpha=0.8)
    ax.add_patch(gateway_box)
    ax.text(2.5, api_y + 0.9, 'API Gateway', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2.5, api_y + 0.6, 'Flask + Gunicorn', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.5, api_y + 0.3, 'REST APIs, Rate Limiting', fontsize=9, ha='center', va='center', color='white')
    ax.text(2.5, api_y + 0.05, 'Load Balancer (Future)', fontsize=9, ha='center', va='center', color='white')
    
    # Core Services
    services = [
        ('Patient\nServices', 'Lookup, Vitals\nHistory, Records'),
        ('Consultation\nService', 'Triage, Orders\nNotes, Chat'),
        ('File\nService', 'Images, Reports\nDocument Storage'),
        ('Real-time\nComms', 'WebSocket\nNotifications')
    ]
    
    for i, (service, desc) in enumerate(services):
        service_box = FancyBboxPatch((5 + i*2.5, api_y), 2.3, 1.2, 
                                    boxstyle="round,pad=0.1", 
                                    facecolor=colors['api'], alpha=0.6)
        ax.add_patch(service_box)
        ax.text(6.15 + i*2.5, api_y + 0.8, service, fontsize=10, fontweight='bold', 
                ha='center', va='center')
        ax.text(6.15 + i*2.5, api_y + 0.3, desc, fontsize=8, ha='center', va='center')
    
    # AI/ML LAYER
    ai_y = 6.8
    
    # Current AI
    current_ai_box = FancyBboxPatch((0.5, ai_y), 5, 1.2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=colors['ai'], alpha=0.8)
    ax.add_patch(current_ai_box)
    ax.text(3, ai_y + 0.9, 'Current AI/ML Layer', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(3, ai_y + 0.6, 'Google Gemini API', fontsize=10, ha='center', va='center', color='white')
    ax.text(3, ai_y + 0.3, 'Medical Consultations, Image Analysis', fontsize=9, ha='center', va='center', color='white')
    ax.text(3, ai_y + 0.05, 'Clinical Decision Support', fontsize=9, ha='center', va='center', color='white')
    
    # Future AI/ML
    future_ai_box = FancyBboxPatch((6, ai_y), 9.5, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['future'], alpha=0.8)
    ax.add_patch(future_ai_box)
    ax.text(10.75, ai_y + 0.9, 'Future AI/ML Enhancements', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(10.75, ai_y + 0.6, 'Custom Models • NLP Pipelines • Risk Scoring • Triage AI', fontsize=10, 
            ha='center', va='center', color='white')
    ax.text(10.75, ai_y + 0.3, 'ICD/SNOMED Coding • Medical Summarization • Guardrails', fontsize=9, 
            ha='center', va='center', color='white')
    ax.text(10.75, ai_y + 0.05, 'MLOps Pipeline • Model Versioning • A/B Testing', fontsize=9, 
            ha='center', va='center', color='white')
    
    # DATA LAYER
    data_y = 4.8
    
    # Current Data Storage
    current_data_box = FancyBboxPatch((0.5, data_y), 4, 1.5, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['data'], alpha=0.8)
    ax.add_patch(current_data_box)
    ax.text(2.5, data_y + 1.1, 'Current Data Storage', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2.5, data_y + 0.8, 'JSON Files', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.5, data_y + 0.5, 'patients.json', fontsize=9, ha='center', va='center', color='white')
    ax.text(2.5, data_y + 0.3, 'patients_history.json', fontsize=9, ha='center', va='center', color='white')
    ax.text(2.5, data_y + 0.1, 'chat_sessions.json', fontsize=9, ha='center', va='center', color='white')
    
    # Future Databases
    future_db_box = FancyBboxPatch((5, data_y), 4, 1.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['future'], alpha=0.8)
    ax.add_patch(future_db_box)
    ax.text(7, data_y + 1.1, 'Future Databases', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(7, data_y + 0.8, 'PostgreSQL/MongoDB', fontsize=10, ha='center', va='center', color='white')
    ax.text(7, data_y + 0.5, 'Patient Records, EMR', fontsize=9, ha='center', va='center', color='white')
    ax.text(7, data_y + 0.3, 'Clinical Data, Analytics', fontsize=9, ha='center', va='center', color='white')
    ax.text(7, data_y + 0.1, 'Backup & Replication', fontsize=9, ha='center', va='center', color='white')
    
    # Cloud Storage
    cloud_box = FancyBboxPatch((9.5, data_y), 3, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['future'], alpha=0.8)
    ax.add_patch(cloud_box)
    ax.text(11, data_y + 1.1, 'Cloud Storage', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(11, data_y + 0.8, 'AWS S3/GCS', fontsize=10, ha='center', va='center', color='white')
    ax.text(11, data_y + 0.5, 'Medical Images', fontsize=9, ha='center', va='center', color='white')
    ax.text(11, data_y + 0.3, 'Reports, Documents', fontsize=9, ha='center', va='center', color='white')
    ax.text(11, data_y + 0.1, 'CDN Distribution', fontsize=9, ha='center', va='center', color='white')
    
    # Cache Layer
    cache_box = FancyBboxPatch((13, data_y), 2.5, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['future'], alpha=0.8)
    ax.add_patch(cache_box)
    ax.text(14.25, data_y + 1.1, 'Cache Layer', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(14.25, data_y + 0.8, 'Redis', fontsize=10, ha='center', va='center', color='white')
    ax.text(14.25, data_y + 0.5, 'Session Store', fontsize=9, ha='center', va='center', color='white')
    ax.text(14.25, data_y + 0.3, 'Rate Limiting', fontsize=9, ha='center', va='center', color='white')
    ax.text(14.25, data_y + 0.1, 'Quick Lookups', fontsize=9, ha='center', va='center', color='white')
    
    # INFRASTRUCTURE & DEPLOYMENT
    infra_y = 2.8
    
    # Current Infrastructure
    current_infra_box = FancyBboxPatch((0.5, infra_y), 4.5, 1.5, 
                                      boxstyle="round,pad=0.1", 
                                      facecolor=colors['infra'], alpha=0.8)
    ax.add_patch(current_infra_box)
    ax.text(2.75, infra_y + 1.1, 'Current Infrastructure', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(2.75, infra_y + 0.8, 'Netlify (Frontend)', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.75, infra_y + 0.5, 'Gunicorn (Backend)', fontsize=10, ha='center', va='center', color='white')
    ax.text(2.75, infra_y + 0.3, 'Environment Variables', fontsize=9, ha='center', va='center', color='white')
    ax.text(2.75, infra_y + 0.1, 'File-based Storage', fontsize=9, ha='center', va='center', color='white')
    
    # Future Infrastructure
    future_infra_box = FancyBboxPatch((5.5, infra_y), 10, 1.5, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=colors['future'], alpha=0.8)
    ax.add_patch(future_infra_box)
    ax.text(10.5, infra_y + 1.1, 'Future Infrastructure & DevOps', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(10.5, infra_y + 0.8, 'Docker Containers • Kubernetes Orchestration • CI/CD Pipeline', 
            fontsize=10, ha='center', va='center', color='white')
    ax.text(10.5, infra_y + 0.5, 'Auto-scaling • Load Balancers • Health Monitoring', 
            fontsize=9, ha='center', va='center', color='white')
    ax.text(10.5, infra_y + 0.3, 'Terraform IaC • GitHub Actions • Multi-region Deployment', 
            fontsize=9, ha='center', va='center', color='white')
    ax.text(10.5, infra_y + 0.1, 'Prometheus/Grafana • ELK Stack • OpenTelemetry', 
            fontsize=9, ha='center', va='center', color='white')
    
    # OBSERVABILITY & ANALYTICS
    obs_y = 0.8
    
    obs_box = FancyBboxPatch((0.5, obs_y), 15, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['future'], alpha=0.8)
    ax.add_patch(obs_box)
    ax.text(8, obs_y + 1.1, 'Observability & Analytics (Future)', fontsize=12, fontweight='bold', 
            ha='center', va='center', color='white')
    ax.text(8, obs_y + 0.8, 'Monitoring: Prometheus/Grafana • Logging: ELK/Splunk • Tracing: OpenTelemetry', 
            fontsize=10, ha='center', va='center', color='white')
    ax.text(8, obs_y + 0.5, 'Medical Analytics: Patient Outcomes • Usage Analytics: Mixpanel/GA4', 
            fontsize=9, ha='center', va='center', color='white')
    ax.text(8, obs_y + 0.3, 'SIEM: Security Monitoring • Compliance Reporting • Audit Trails', 
            fontsize=9, ha='center', va='center', color='white')
    ax.text(8, obs_y + 0.1, 'Performance Metrics • Error Tracking • Business Intelligence', 
            fontsize=9, ha='center', va='center', color='white')
    
    # ARROWS AND CONNECTIONS
    # Client to Security
    ax.arrow(8, client_y, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Security to API
    ax.arrow(8, security_y, 0, -0.2, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # API to AI
    ax.arrow(8, api_y, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # AI to Data
    ax.arrow(8, ai_y, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Data to Infrastructure
    ax.arrow(8, data_y, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Infrastructure to Observability
    ax.arrow(8, infra_y, 0, -0.5, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Side arrows for data flow
    # Patient to API
    ax.arrow(2.25, client_y, 0.2, -2.5, head_width=0.1, head_length=0.1, fc='blue', ec='blue', alpha=0.7)
    
    # Doctor to API  
    ax.arrow(6.25, client_y, -3.5, -2.5, head_width=0.1, head_length=0.1, fc='blue', ec='blue', alpha=0.7)
    
    # Video calls connection
    ax.arrow(13.75, client_y, 0, -7.5, head_width=0.1, head_length=0.1, fc='cyan', ec='cyan', alpha=0.7)
    
    plt.tight_layout()
    return fig

def create_data_flow_diagram():
    """Create a simplified data flow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(8, 9.5, 'MedCore AI - Data Flow Architecture', 
            fontsize=20, fontweight='bold', ha='center',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    # Data flow boxes with arrows
    flows = [
        (2, 8, "Patient\nSubmits Data", '#2E86AB'),
        (6, 8, "API Gateway\nValidation", '#A23B72'),
        (10, 8, "AI Processing\nGemini API", '#F18F01'),
        (14, 8, "Clinical\nInsights", '#C73E1D'),
        (2, 5, "Doctor\nDashboard", '#2E86AB'),
        (6, 5, "Patient\nLookup", '#A23B72'),
        (10, 5, "Data\nVisualization", '#F18F01'),
        (14, 5, "Treatment\nRecommendations", '#C73E1D'),
        (2, 2, "Video Call\nInitiation", '#00B4D8'),
        (6, 2, "WebRTC\nSignaling", '#805AD5'),
        (10, 2, "Media\nStreaming", '#00B4D8'),
        (14, 2, "Session\nRecording", '#805AD5')
    ]
    
    for x, y, text, color in flows:
        box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, 
                            boxstyle="round,pad=0.1", 
                            facecolor=color, alpha=0.8)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=10, fontweight='bold', 
                ha='center', va='center', color='white')
    
    # Arrows between flows
    arrow_pairs = [
        ((2, 8), (6, 8)),
        ((6, 8), (10, 8)),
        ((10, 8), (14, 8)),
        ((2, 5), (6, 5)),
        ((6, 5), (10, 5)),
        ((10, 5), (14, 5)),
        ((2, 2), (6, 2)),
        ((6, 2), (10, 2)),
        ((10, 2), (14, 2))
    ]
    
    for (x1, y1), (x2, y2) in arrow_pairs:
        ax.arrow(x1+0.8, y1, x2-x1-1.6, y2-y1, 
                head_width=0.15, head_length=0.2, fc='black', ec='black', alpha=0.6)
    
    plt.tight_layout()
    return fig

def main():
    """Generate and save architecture diagrams"""
    print("Generating MedCore AI Architecture Diagrams...")
    
    # Create main architecture diagram
    fig1 = create_architecture_diagram()
    fig1.savefig('medcore_ai_architecture.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("✅ Main architecture diagram saved as 'medcore_ai_architecture.png'")
    
    # Create data flow diagram
    fig2 = create_data_flow_diagram()
    fig2.savefig('medcore_ai_dataflow.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✅ Data flow diagram saved as 'medcore_ai_dataflow.png'")
    
    # Show the diagrams
    plt.show()
    
    print("\n🏥 MedCore AI Architecture Diagrams Generated Successfully!")
    print("\nKey Components Visualized:")
    print("• Current: Flask API, Gemini AI, JSON storage, Netlify hosting")
    print("• Future: Microservices, PostgreSQL/MongoDB, Redis cache, Docker/K8s")
    print("• Video/Audio: WebRTC, Twilio/Agora integration")
    print("• Security: HIPAA/FDA compliance, encryption, audit logs")
    print("• Observability: Monitoring, logging, analytics")

if __name__ == "__main__":
    main()
