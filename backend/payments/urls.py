from django.urls import path

from .views import (
    PaymentListView,
    PaymentDetailView,
    MpesaInitiateView,
    MpesaCallbackView,
    PaymentStatusCheckView,
    MpesaQueryStatusView
)

urlpatterns = [
    # Payments
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<uuid:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('<uuid:payment_id>/status/', PaymentStatusCheckView.as_view(), name='payment-status'),
    
    # M-Pesa
    path('mpesa/initiate/', MpesaInitiateView.as_view(), name='mpesa-initiate'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('mpesa/query/<uuid:payment_id>/', MpesaQueryStatusView.as_view(), name='mpesa-query'),
]
