from datetime import datetime
from flask import current_app
from app.services.report_service import ReportService

def generate_daily_report():
    """Generate daily inventory report at midnight."""
    try:
        current_app.logger.info("Starting daily report generation")
        report_service = ReportService()
        report = report_service.generate_daily_report()
        
        if report:
            current_app.logger.info(f"Successfully generated report for {report.date}")
        else:
            current_app.logger.error("Failed to generate daily report")
            
    except Exception as e:
        current_app.logger.error(f"Error in daily report generation: {str(e)}") 