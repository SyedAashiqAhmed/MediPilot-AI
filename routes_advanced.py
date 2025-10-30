"""
Flask Routes for Advanced Features
Add these to your dpp.py or import this module
"""
from flask import jsonify, request, send_file
from advanced_features import (
    get_patient_dashboard,
    get_patient_trends,
    advanced_patient_search,
    get_patient_alerts,
    generate_patient_report_pdf,
    get_upcoming_appointments,
    get_patient_medications
)

# ==================== DASHBOARD ROUTE ====================

def register_advanced_routes(app):
    """Register all advanced feature routes"""
    
    @app.route("/api/dashboard")
    def api_dashboard():
        """Real-time patient dashboard with statistics"""
        try:
            dashboard_data = get_patient_dashboard()
            return jsonify(dashboard_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== TRENDS ROUTE ====================
    
    @app.route("/api/patient_trends/<patient_id>")
    def api_patient_trends(patient_id):
        """Get historical trends for patient"""
        try:
            trends = get_patient_trends(patient_id)
            if not trends:
                return jsonify({"error": "Patient not found"}), 404
            return jsonify(trends)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== ADVANCED SEARCH ROUTE ====================
    
    @app.route("/api/search", methods=["GET", "POST"])
    def api_advanced_search():
        """Advanced patient search with filters"""
        try:
            if request.method == "POST":
                data = request.get_json()
                query = data.get('query', '')
                filters = data.get('filters', {})
            else:
                query = request.args.get('q', '')
                filters = {
                    'min_age': request.args.get('min_age'),
                    'max_age': request.args.get('max_age'),
                    'gender': request.args.get('gender'),
                    'status': request.args.get('status'),
                    'start_date': request.args.get('start_date'),
                    'end_date': request.args.get('end_date')
                }
                # Remove None values
                filters = {k: v for k, v in filters.items() if v is not None}
            
            results = advanced_patient_search(query, filters)
            return jsonify({
                "results": results,
                "count": len(results),
                "query": query,
                "filters": filters
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== ALERTS ROUTE ====================
    
    @app.route("/api/alerts")
    def api_alerts():
        """Get all patient alerts"""
        try:
            alerts = get_patient_alerts()
            return jsonify({
                "alerts": alerts,
                "total_alerts": len(alerts),
                "critical_count": sum(1 for a in alerts if a['highest_severity'] == 'critical'),
                "warning_count": sum(1 for a in alerts if a['highest_severity'] == 'warning')
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== PDF REPORT ROUTE ====================
    
    @app.route("/api/report/<patient_id>/pdf")
    def api_generate_report(patient_id):
        """Generate and download PDF report for patient"""
        try:
            pdf_buffer = generate_patient_report_pdf(patient_id)
            if not pdf_buffer:
                return jsonify({"error": "Patient not found"}), 404
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'patient_report_{patient_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== APPOINTMENTS ROUTE ====================
    
    @app.route("/api/appointments")
    def api_appointments():
        """Get upcoming appointments"""
        try:
            days = request.args.get('days', 7, type=int)
            appointments = get_upcoming_appointments(days)
            return jsonify(appointments)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== MEDICATIONS ROUTE ====================
    
    @app.route("/api/medications/<patient_id>")
    def api_medications(patient_id):
        """Get patient medications"""
        try:
            medications = get_patient_medications(patient_id)
            if not medications:
                return jsonify({"error": "Patient not found"}), 404
            return jsonify(medications)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== STATISTICS ROUTE ====================
    
    @app.route("/api/statistics")
    def api_statistics():
        """Get overall system statistics"""
        try:
            from models import Patient, Vitals, LabResult, ChatSession, ChatMessage
            
            stats = {
                "patients": {
                    "total": Patient.query.count(),
                    "today": Patient.query.filter(
                        Patient.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
                    ).count()
                },
                "vitals_recorded": Vitals.query.count(),
                "lab_tests": LabResult.query.count(),
                "chat_sessions": ChatSession.query.count(),
                "chat_messages": ChatMessage.query.count(),
                "active_alerts": len(get_patient_alerts())
            }
            
            return jsonify(stats)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== PATIENT COMPARISON ROUTE ====================
    
    @app.route("/api/compare")
    def api_compare_patients():
        """Compare multiple patients"""
        try:
            patient_ids = request.args.get('ids', '').split(',')
            if not patient_ids or not patient_ids[0]:
                return jsonify({"error": "No patient IDs provided"}), 400
            
            from database import get_patient_by_id
            
            comparison = []
            for pid in patient_ids:
                patient = get_patient_by_id(pid.strip())
                if patient:
                    comparison.append(patient)
            
            return jsonify({
                "patients": comparison,
                "count": len(comparison)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    # ==================== EXPORT DATA ROUTE ====================
    
    @app.route("/api/export/<patient_id>")
    def api_export_patient(patient_id):
        """Export patient data as JSON"""
        try:
            from database import get_patient_by_id, get_patient_history
            import json
            
            patient = get_patient_by_id(patient_id)
            if not patient:
                return jsonify({"error": "Patient not found"}), 404
            
            history = get_patient_history(patient_id)
            
            export_data = {
                "patient": patient,
                "history": history,
                "export_date": datetime.now().isoformat()
            }
            
            return jsonify(export_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    
    print("✅ Advanced routes registered successfully!")


# Import datetime at top
from datetime import datetime
