from django.urls import path
from .views import (
    ApartmentListCreateView, ApartmentDetailView, ApartmentVerifiedImageView,
    UserListCreateView, UserDetailView, UserImageView,
    DepositOrderListCreateView, DepositOrderDetailView, DepositOrderByBuyerView,
    ViewingAppointmentListCreateView, ViewingAppointmentDetailView,
    ProjectListCreateView, ProjectDetailView,
    PasswordResetListCreateView, PasswordResetDetailView
)

urlpatterns = [
    # Apartments
    path('apartments/', ApartmentListCreateView.as_view(), name='apartment-list'),
    path('apartments/<str:pk>/', ApartmentDetailView.as_view(), name='apartment-detail'),
    path('apartments/<str:pk>/verified-images/', ApartmentVerifiedImageView.as_view(), name='apartment-verified-image-crud'),
    
    # Users
    path('users/', UserListCreateView.as_view(), name='user-list'),
    path('users/<str:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<str:pk>/image/', UserImageView.as_view(), name='user-image-crud'),
    
    # Deposit Orders
    path('deposit-orders/', DepositOrderListCreateView.as_view(), name='deposit-order-list'),
    path('deposit-orders/buyer/<str:buyer_id>/', DepositOrderByBuyerView.as_view(), name='deposit-order-by-buyer'),
    path('deposit-orders/<str:pk>/', DepositOrderDetailView.as_view(), name='deposit-order-detail'),
    
    # Viewing Appointments
    path('viewing-appointments/', ViewingAppointmentListCreateView.as_view(), name='viewing-appointment-list'),
    path('viewing-appointments/<str:pk>/', ViewingAppointmentDetailView.as_view(), name='viewing-appointment-detail'),
    
    # Projects
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<str:pk>/', ProjectDetailView.as_view(), name='project-detail'),

    # Password Resets
    path('password-resets/', PasswordResetListCreateView.as_view(), name='password-reset-list'),
    path('password-resets/<str:pk>/', PasswordResetDetailView.as_view(), name='password-reset-detail'),
]
