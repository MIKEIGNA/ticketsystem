from rest_framework import serializers
from .models import Payment, PaymentAttempt, Refund


class PaymentAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAttempt
        fields = ['id', 'status', 'error_code', 'error_message', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    attempts = PaymentAttemptSerializer(many=True, read_only=True)
    booking_number = serializers.CharField(source='booking.booking_number', read_only=True)
    event_title = serializers.CharField(source='booking.event.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'booking_number', 'event_title', 'amount', 'currency',
                  'method', 'status', 'mpesa_receipt_number', 'mpesa_phone_number',
                  'failure_reason', 'attempts', 'created_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'completed_at']


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for initiating M-Pesa payment"""
    booking_id = serializers.UUIDField()
    phone_number = serializers.CharField(max_length=13)
    
    def validate_phone_number(self, value):
        from accounts.models import normalize_phone
        normalized = normalize_phone(value)
        if not (normalized.startswith('254') and len(normalized) == 12 and normalized.isdigit()):
            raise serializers.ValidationError(
                "Enter a valid Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, or 254XXXXXXXXX"
            )
        return normalized


class MpesaCallbackSerializer(serializers.Serializer):
    """Serializer for M-Pesa callback data"""
    Body = serializers.DictField()


class PaymentStatusSerializer(serializers.ModelSerializer):
    """Lightweight serializer for checking payment status"""
    class Meta:
        model = Payment
        fields = ['id', 'status', 'mpesa_receipt_number', 'completed_at']


class RefundSerializer(serializers.ModelSerializer):
    payment_booking = serializers.CharField(source='payment.booking.booking_number', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    
    class Meta:
        model = Refund
        fields = ['id', 'payment', 'payment_booking', 'amount', 'reason',
                  'status', 'requested_by', 'requested_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'requested_by']
    
    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)
