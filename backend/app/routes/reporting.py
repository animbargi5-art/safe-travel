"""
Advanced Reporting & Business Intelligence API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.database_dep import get_db
from app.routes.auth import get_current_user
from app.services.reporting_service import BusinessIntelligenceService
from app.models.user import User

router = APIRouter(prefix="/reporting", tags=["Reporting & BI"])

def verify_admin_access(current_user: User = Depends(get_current_user)):
    """Verify user has admin access for reporting"""
    # In production, implement proper role-based access control
    # For now, we'll allow all authenticated users to access reports
    return current_user

@router.get("/executive-dashboard")
def get_executive_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get executive dashboard with key business metrics"""
    
    try:
        bi_service = BusinessIntelligenceService(db)
        dashboard_data = bi_service.get_executive_dashboard(days)
        
        return {
            'status': 'success',
            'data': dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating executive dashboard: {str(e)}"
        )

@router.get("/financial-report")
def get_financial_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial report"""
    
    try:
        # Default to last 30 days if dates not provided
        if not end_date:
            end_dt = datetime.utcnow()
        else:
            end_dt = datetime.fromisoformat(end_date)
            
        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.fromisoformat(start_date)
        
        bi_service = BusinessIntelligenceService(db)
        financial_data = bi_service.get_financial_report(start_dt, end_dt)
        
        return {
            'status': 'success',
            'data': financial_data
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating financial report: {str(e)}"
        )

@router.get("/predictive-insights")
def get_predictive_insights(
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get predictive insights and forecasts"""
    
    try:
        bi_service = BusinessIntelligenceService(db)
        insights = bi_service.get_predictive_insights()
        
        return {
            'status': 'success',
            'data': insights
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating predictive insights: {str(e)}"
        )

@router.get("/revenue-analysis")
def get_revenue_analysis(
    period: str = Query("30d", pattern="^(7d|30d|90d|1y)$", description="Analysis period"),
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get detailed revenue analysis"""
    
    try:
        # Parse period
        period_days = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        
        days = period_days[period]
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        bi_service = BusinessIntelligenceService(db)
        
        # Get revenue trends from executive dashboard
        dashboard_data = bi_service.get_executive_dashboard(days)
        revenue_trends = dashboard_data['revenue_trends']
        
        return {
            'status': 'success',
            'data': {
                'period': period,
                'revenue_trends': revenue_trends,
                'summary': dashboard_data['kpis']
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating revenue analysis: {str(e)}"
        )

@router.get("/customer-analytics")
def get_customer_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get comprehensive customer analytics"""
    
    try:
        bi_service = BusinessIntelligenceService(db)
        dashboard_data = bi_service.get_executive_dashboard(days)
        
        return {
            'status': 'success',
            'data': {
                'customer_metrics': dashboard_data['customer_metrics'],
                'operational_metrics': dashboard_data['operational_metrics'],
                'period': dashboard_data['period']
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating customer analytics: {str(e)}"
        )

@router.get("/market-insights")
def get_market_insights(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get market analysis and insights"""
    
    try:
        bi_service = BusinessIntelligenceService(db)
        dashboard_data = bi_service.get_executive_dashboard(days)
        
        return {
            'status': 'success',
            'data': {
                'market_insights': dashboard_data['market_insights'],
                'operational_metrics': dashboard_data['operational_metrics'],
                'period': dashboard_data['period']
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating market insights: {str(e)}"
        )

@router.get("/performance-summary")
def get_performance_summary(
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Get quick performance summary for dashboard widgets"""
    
    try:
        bi_service = BusinessIntelligenceService(db)
        
        # Get data for different periods
        daily_data = bi_service.get_executive_dashboard(1)
        weekly_data = bi_service.get_executive_dashboard(7)
        monthly_data = bi_service.get_executive_dashboard(30)
        
        return {
            'status': 'success',
            'data': {
                'today': {
                    'revenue': daily_data['kpis']['total_revenue']['value'],
                    'bookings': daily_data['kpis']['total_bookings']['value']
                },
                'this_week': {
                    'revenue': weekly_data['kpis']['total_revenue']['value'],
                    'bookings': weekly_data['kpis']['total_bookings']['value'],
                    'growth': weekly_data['kpis']['total_revenue']['growth']
                },
                'this_month': {
                    'revenue': monthly_data['kpis']['total_revenue']['value'],
                    'bookings': monthly_data['kpis']['total_bookings']['value'],
                    'conversion_rate': monthly_data['kpis']['conversion_rate']['value']
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating performance summary: {str(e)}"
        )

@router.get("/export/csv")
def export_data_csv(
    report_type: str = Query(..., pattern="^(revenue|bookings|customers)$"),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(verify_admin_access),
    db: Session = Depends(get_db)
):
    """Export report data as CSV"""
    
    try:
        from fastapi.responses import StreamingResponse
        import io
        import csv
        
        bi_service = BusinessIntelligenceService(db)
        dashboard_data = bi_service.get_executive_dashboard(days)
        
        # Create CSV content based on report type
        output = io.StringIO()
        writer = csv.writer(output)
        
        if report_type == 'revenue':
            writer.writerow(['Date', 'Revenue', 'Transactions'])
            for row in dashboard_data['revenue_trends']['daily']:
                writer.writerow([row['date'], row['revenue'], row['transactions']])
                
        elif report_type == 'bookings':
            writer.writerow(['Metric', 'Value'])
            kpis = dashboard_data['kpis']
            writer.writerow(['Total Revenue', kpis['total_revenue']['value']])
            writer.writerow(['Total Bookings', kpis['total_bookings']['value']])
            writer.writerow(['Conversion Rate', kpis['conversion_rate']['value']])
            
        elif report_type == 'customers':
            writer.writerow(['Segment', 'Count', 'Average Spent'])
            for segment in dashboard_data['customer_metrics']['customer_segments']:
                writer.writerow([segment['segment'], segment['count'], segment['average_spent']])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{report_type}_report.csv"'}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting data: {str(e)}"
        )

@router.get("/health")
def reporting_health_check():
    """Health check for reporting service"""
    return {
        'status': 'healthy',
        'service': 'reporting',
        'timestamp': datetime.utcnow().isoformat()
    }