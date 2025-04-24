from django.urls import path
from . import views
from .views import export_mesures_csv


urlpatterns = [
    path('api/data/', views.receive_data, name='receive_data'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('historique/', views.historique, name='historique'),
    path('config/', views.config_view, name='config'),
    path('export/csv/', export_mesures_csv, name='export_csv'),
]