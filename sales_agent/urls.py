from django.urls import path
from sales_agent.views import dashboard, analytics_dashboard, start_sequence_view, register, login_view, logout_view

urlpatterns = [
    path('', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('analytics/', analytics_dashboard, name='analytics'),
    path('start-sequence/<int:lead_id>/', start_sequence_view, name='start_sequence'),
]