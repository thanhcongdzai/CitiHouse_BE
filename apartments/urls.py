from django.urls import path
from .views import (
    ApartmentListCreateView, ApartmentDetailView,
    UserListCreateView, UserDetailView,
    DepositOrderListCreateView, DepositOrderDetailView,
    ViewingAppointmentListCreateView, ViewingAppointmentDetailView,
    ProjectListCreateView, ProjectDetailView
)

urlpatterns = [
    # Apartments
    path('apartments/', ApartmentListCreateView.as_view(), name='apartment-list'),
    path('apartments/<str:pk>/', ApartmentDetailView.as_view(), name='apartment-detail'),
    
    # Users
    path('users/', UserListCreateView.as_view(), name='user-list'),
    path('users/<str:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Deposit Orders
    path('deposit-orders/', DepositOrderListCreateView.as_view(), name='deposit-order-list'),
    path('deposit-orders/<str:pk>/', DepositOrderDetailView.as_view(), name='deposit-order-detail'),
    
    # Viewing Appointments
    path('viewing-appointments/', ViewingAppointmentListCreateView.as_view(), name='viewing-appointment-list'),
    path('viewing-appointments/<str:pk>/', ViewingAppointmentDetailView.as_view(), name='viewing-appointment-detail'),
    
    # Projects
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<str:pk>/', ProjectDetailView.as_view(), name='project-detail'),
]
