# billing_app/urls.py

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='billing_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.create_bill, name='create_bill'),
    path('bill/<int:bill_id>/', views.bill_summary, name='bill_summary'),
    path('patients/search/', views.patient_search, name='patient_search'),
    path('patients/list/', views.patient_list, name='patient_list'),
    path('patients/<int:patient_id>/delete/', views.patient_delete, name='patient_delete'),
]
