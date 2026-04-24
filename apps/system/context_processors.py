from apps.users.models import User
from apps.orders.models import Order
from apps.ai.models import AICase
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def dashboard_stats(request):
    if not request.path.startswith('/admin/'):
        return {}
    
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_ai_cases = AICase.objects.count()
    
    # Simple data for charts (last 7 days)
    last_7_days = [timezone.now().date() - timedelta(days=i) for i in range(6, -1, -1)]
    
    # User registrations per day
    registrations_data = []
    for day in last_7_days:
        count = User.objects.filter(date_joined__date=day).count()
        registrations_data.append(count)
        
    # Sales per day
    sales_data = []
    for day in last_7_days:
        amount = Order.objects.filter(created_at__date=day).aggregate(Sum('total'))['total__sum'] or 0
        sales_data.append(float(amount))
        
    return {
        'kpi_total_users': total_users,
        'kpi_total_orders': total_orders,
        'kpi_total_revenue': total_revenue,
        'kpi_total_ai_cases': total_ai_cases,
        'chart_labels': [day.strftime('%b %d') for day in last_7_days],
        'chart_registrations': registrations_data,
        'chart_sales': sales_data,
    }
