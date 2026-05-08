import base64
import json
import requests
from datetime import datetime
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from bookings.models import Booking
from .models import Payment, PaymentAttempt
from .serializers import (
    PaymentSerializer, 
    PaymentCreateSerializer,
    PaymentStatusSerializer,
    MpesaCallbackSerializer
)


class PaymentListView(generics.ListAPIView):
    """ListAPIView: List user's payments"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        ).select_related('booking', 'booking__event')


class PaymentDetailView(generics.RetrieveAPIView):
    """RetrieveAPIView: Get payment details"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user)


class MpesaInitiateView(APIView):
    """
    APIView: Initiate M-Pesa STK Push payment
    This handles the entire M-Pesa payment flow
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Validate request data
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        booking_id = serializer.validated_data['booking_id']
        phone_number = serializer.validated_data['phone_number']
        
        # Get booking
        try:
            booking = Booking.objects.get(
                id=booking_id,
                user=request.user,
                status='pending'
            )
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found or already processed'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create or get payment record
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': booking.total_amount,
                'method': 'mpesa',
                'mpesa_phone_number': phone_number
            }
        )
        
        if payment.status == 'completed':
            return Response(
                {'error': 'Payment already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initiate M-Pesa STK Push
        try:
            mpesa_response = self.initiate_stk_push(
                phone_number=phone_number,
                amount=float(booking.total_amount),
                account_reference=booking.booking_number,
                transaction_desc=f"Payment for {booking.event.title}"
            )
            
            if mpesa_response.get('ResponseCode') == '0':
                # Update payment record
                payment.mpesa_checkout_request_id = mpesa_response.get('CheckoutRequestID')
                payment.mpesa_merchant_request_id = mpesa_response.get('MerchantRequestID')
                payment.status = 'processing'
                payment.save()
                
                # Log payment attempt
                PaymentAttempt.objects.create(
                    payment=payment,
                    status='stk_pushed',
                    request_payload={
                        'phone_number': phone_number,
                        'amount': str(booking.total_amount)
                    },
                    response_payload=mpesa_response
                )
                
                return Response({
                    'message': 'M-Pesa STK Push initiated successfully',
                    'checkout_request_id': payment.mpesa_checkout_request_id,
                    'payment_id': str(payment.id),
                    'status': payment.status
                })
            else:
                # Log failed attempt
                PaymentAttempt.objects.create(
                    payment=payment,
                    status='failed',
                    response_payload=mpesa_response,
                    error_code=mpesa_response.get('ResponseCode'),
                    error_message=mpesa_response.get('ResponseDescription')
                )
                
                return Response({
                    'error': 'Failed to initiate M-Pesa payment',
                    'details': mpesa_response.get('ResponseDescription')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            PaymentAttempt.objects.create(
                payment=payment,
                status='failed',
                error_message=str(e)
            )
            return Response({
                'error': 'Failed to initiate M-Pesa payment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate M-Pesa STK Push via Daraja API"""
        
        # Get access token
        access_token = self.get_mpesa_access_token()
        
        # Prepare STK Push request
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        if settings.MPESA_ENVIRONMENT == 'production':
            api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': settings.MPESA_SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': settings.MPESA_SHORTCODE,
            'PhoneNumber': phone_number,
            'CallBackURL': settings.MPESA_CALLBACK_URL,
            'AccountReference': account_reference[:20],  # Max 20 chars
            'TransactionDesc': transaction_desc[:100]  # Max 100 chars
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()

    def get_mpesa_access_token(self):
        """Get M-Pesa OAuth access token"""
        
        auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        if settings.MPESA_ENVIRONMENT == 'production':
            auth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        credentials = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}'
        }
        
        response = requests.get(auth_url, headers=headers)
        return response.json().get('access_token')


class MpesaCallbackView(APIView):
    """
    APIView: Handle M-Pesa callback
    This is the endpoint that M-Pesa will call after payment
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MpesaCallbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        callback_data = serializer.validated_data['Body']
        stk_callback = callback_data.get('stkCallback', {})
        
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        merchant_request_id = stk_callback.get('MerchantRequestID')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        # Find payment by checkout request ID
        try:
            payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Log the callback
        PaymentAttempt.objects.create(
            payment=payment,
            status='completed' if result_code == 0 else 'failed',
            response_payload=callback_data
        )
        
        if result_code == 0:
            # Payment successful
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            receipt_number = None
            transaction_date = None
            phone_number = None
            
            for item in items:
                name = item.get('Name')
                value = item.get('Value')
                
                if name == 'MpesaReceiptNumber':
                    receipt_number = value
                elif name == 'TransactionDate':
                    transaction_date = str(value)
                elif name == 'PhoneNumber':
                    phone_number = str(value)
            
            # Update payment
            payment.mark_completed(receipt_number=receipt_number)
            payment.mpesa_transaction_date = transaction_date
            if phone_number:
                payment.mpesa_phone_number = phone_number
            payment.save()
            
            # Update booking
            booking = payment.booking
            booking.status = 'confirmed'
            booking.save()
            
            return Response({'ResultCode': 0, 'ResultDesc': 'Success'})
        
        else:
            # Payment failed
            payment.mark_failed(
                result_code=str(result_code),
                result_desc=result_desc
            )
            
            return Response({'ResultCode': 0, 'ResultDesc': 'Received'})


class PaymentStatusCheckView(APIView):
    """APIView: Check payment status"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                booking__user=request.user
            )
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PaymentStatusSerializer(payment)
        return Response(serializer.data)


class MpesaQueryStatusView(APIView):
    """
    APIView: Query M-Pesa transaction status
    Fallback for when callback is not received
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                booking__user=request.user
            )
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not payment.mpesa_checkout_request_id:
            return Response(
                {'error': 'No M-Pesa transaction to query'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Query transaction status
            access_token = MpesaInitiateView().get_mpesa_access_token()
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
            ).decode()
            
            query_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
            if settings.MPESA_ENVIRONMENT == 'production':
                query_url = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': settings.MPESA_SHORTCODE,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': payment.mpesa_checkout_request_id
            }
            
            response = requests.post(query_url, json=payload, headers=headers)
            result = response.json()
            
            return Response({
                'payment_status': payment.status,
                'query_result': result
            })
            
        except Exception as e:
            return Response({
                'error': 'Failed to query transaction status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

