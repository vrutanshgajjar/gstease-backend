from django.urls import path
from gst import views
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/',views.login_user,name="login"),
    path('details/',views.get_user,name="get"),
    path('delete/',views.delete_user,name="delete"),
    path('create-invoice/',views.create_invoice,name="invoice creation"),
    path('invoice-list/',views.get_invoices,name="invoice list"),
    path('purchase-list/', views.purchase_list, name='purchase-list'),
    path('purchase-create/', views.purchase_create, name='purchase-create'),
    path('gstr-repo/',views.gstr_report_view,name="GSTR-1"),
    path('create-purchase/',views.create_purchase,name="Purchase slip creation"),
    path('itc-tracker/',views.itc_tracker,name="tracker"),
    path('status-update/',views.update_itc_status,name="update status"),
    path('monthly/',views.monthly_summary,name="monthly"),
    path('recent/',views.get_recent_activities,name="Recent Activity"),
    path('stats/',views.dashboard_stats,name="stats"),
    path('home-stats/',views.platform_overview),
    path('export/',views.export_report,name="export"),
]
