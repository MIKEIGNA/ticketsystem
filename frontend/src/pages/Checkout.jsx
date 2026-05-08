import { useState } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { paymentService } from '../services/payments';
import { bookingService } from '../services/bookings';
import { useAuth } from '../context/AuthContext';
import { Calendar, MapPin, Ticket, CreditCard, Phone, Loader, CheckCircle, AlertCircle } from 'lucide-react';

const Checkout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { event, tier, quantity } = location.state || {};

  const [step, setStep] = useState('details'); // details, payment, processing, success
  const [bookingData, setBookingData] = useState({
    contact_name: user?.first_name + ' ' + user?.last_name || '',
    contact_email: user?.email || '',
    contact_phone: user?.phone_number || '',
    special_requests: '',
  });
  const [paymentPhone, setPaymentPhone] = useState(user?.phone_number || '');
  const [booking, setBooking] = useState(null);
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if no event data
  if (!event || !tier) {
    return <Navigate to="/events" />;
  }

  const totalAmount = tier.price * quantity;

  const handleCreateBooking = async () => {
    setLoading(true);
    setError('');

    try {
      const tickets = Array(quantity).fill({
        ticket_tier_id: tier.id,
        attendee_name: bookingData.contact_name,
        attendee_email: bookingData.contact_email,
        attendee_phone: bookingData.contact_phone,
      });

      const response = await bookingService.createBooking({
        event_id: event.id,
        ...bookingData,
        tickets,
      });

      setBooking(response.data);
      setStep('payment');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    setLoading(true);
    setError('');
    setStep('processing');

    try {
      const response = await paymentService.initiateMpesa({
        booking_id: booking.id,
        phone_number: paymentPhone,
      });

      setPayment(response.data);

      // Poll for payment status
      pollPaymentStatus(response.data.payment_id);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to initiate payment');
      setStep('payment');
    } finally {
      setLoading(false);
    }
  };

  const pollPaymentStatus = async (paymentId) => {
    const checkStatus = async () => {
      try {
        const response = await paymentService.getPaymentStatus(paymentId);
        const status = response.data.status;

        if (status === 'completed') {
          setStep('success');
        } else if (status === 'failed' || status === 'cancelled') {
          setError('Payment failed. Please try again.');
          setStep('payment');
        } else {
          // Continue polling
          setTimeout(checkStatus, 3000);
        }
      } catch (err) {
        setTimeout(checkStatus, 3000);
      }
    };

    // Start polling
    setTimeout(checkStatus, 3000);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
          <p className="text-gray-600 mt-1">Complete your booking</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="md:col-span-2">
            {step === 'details' && (
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Contact Information</h2>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                    {error}
                  </div>
                )}

                <div className="space-y-5">
                  <div>
                    <label className="label">Full Name *</label>
                    <input
                      type="text"
                      value={bookingData.contact_name}
                      onChange={(e) => setBookingData({ ...bookingData, contact_name: e.target.value })}
                      className="input"
                      required
                    />
                  </div>

                  <div>
                    <label className="label">Email *</label>
                    <input
                      type="email"
                      value={bookingData.contact_email}
                      onChange={(e) => setBookingData({ ...bookingData, contact_email: e.target.value })}
                      className="input"
                      required
                    />
                  </div>

                  <div>
                    <label className="label">Phone Number *</label>
                    <input
                      type="tel"
                      value={bookingData.contact_phone}
                      onChange={(e) => setBookingData({ ...bookingData, contact_phone: e.target.value })}
                      className="input"
                      placeholder="254XXXXXXXXX"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">Format: 254XXXXXXXXX</p>
                  </div>

                  <div>
                    <label className="label">Special Requests (Optional)</label>
                    <textarea
                      value={bookingData.special_requests}
                      onChange={(e) => setBookingData({ ...bookingData, special_requests: e.target.value })}
                      className="input h-24 resize-none"
                      placeholder="Any special requirements..."
                    />
                  </div>

                  <button
                    onClick={handleCreateBooking}
                    disabled={loading}
                    className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white font-semibold rounded-lg transition-colors"
                  >
                    {loading ? 'Creating Booking...' : 'Continue to Payment'}
                  </button>
                </div>
              </div>
            )}

            {step === 'payment' && (
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Payment</h2>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                    {error}
                  </div>
                )}

                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <Phone className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-green-900">M-Pesa Payment</p>
                      <p className="text-sm text-green-700">Secure payment via M-Pesa STK Push</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-5">
                  <div>
                    <label className="label">M-Pesa Phone Number *</label>
                    <input
                      type="tel"
                      value={paymentPhone}
                      onChange={(e) => setPaymentPhone(e.target.value)}
                      className="input"
                      placeholder="254712345678"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enter the phone number to receive the STK push
                    </p>
                  </div>

                  <button
                    onClick={handlePayment}
                    disabled={loading}
                    className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-semibold rounded-lg transition-colors"
                  >
                    {loading ? 'Initiating...' : `Pay KES ${totalAmount.toLocaleString()}`}
                  </button>

                  <button
                    onClick={() => setStep('details')}
                    className="w-full py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50"
                  >
                    Back
                  </button>
                </div>
              </div>
            )}

            {step === 'processing' && (
              <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                  <Loader className="w-8 h-8 text-primary-600 animate-spin" />
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Processing Payment</h2>
                <p className="text-gray-600">
                  Please check your phone (254...) and enter your M-Pesa PIN to complete the payment.
                </p>
              </div>
            )}

            {step === 'success' && (
              <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Payment Successful!</h2>
                <p className="text-gray-600 mb-6">
                  Your tickets have been booked. Check your email for the tickets.
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => navigate('/my-tickets')}
                    className="flex-1 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg"
                  >
                    View My Tickets
                  </button>
                  <button
                    onClick={() => navigate('/events')}
                    className="flex-1 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50"
                  >
                    More Events
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Order Summary */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 sticky top-24">
              <h3 className="font-bold text-gray-900 mb-4">Order Summary</h3>

              <div className="space-y-4 mb-6">
                <div className="flex gap-4">
                  <img
                    src={event.poster_image || '/placeholder-event.jpg'}
                    alt={event.title}
                    className="w-20 h-20 rounded-lg object-cover"
                  />
                  <div>
                    <h4 className="font-semibold text-gray-900 line-clamp-2">{event.title}</h4>
                    <p className="text-sm text-gray-500">{formatDate(event.start_datetime)}</p>
                    <p className="text-sm text-gray-500">{event.venue?.name}</p>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">{tier.name}</span>
                    <span className="font-medium">x {quantity}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Price per ticket</span>
                    <span className="font-medium">KES {tier.price.toLocaleString()}</span>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-gray-900">Total</span>
                    <span className="text-xl font-bold text-primary-600">
                      KES {totalAmount.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-xs text-gray-500 space-y-1">
                <p className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Instant ticket delivery
                </p>
                <p className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Secure M-Pesa payment
                </p>
                <p className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Easy mobile check-in
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
