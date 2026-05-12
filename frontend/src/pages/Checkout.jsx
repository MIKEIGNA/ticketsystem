import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import { paymentService } from '../services/payments';
import { bookingService } from '../services/bookings';
import { useAuth } from '../context/AuthContext';
import { Calendar, MapPin, Ticket, CreditCard, Phone, Loader, CheckCircle, AlertCircle, Download } from 'lucide-react';

const Checkout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { event, tier, quantity, isGuest } = location.state || {};

  const [step, setStep] = useState('details'); // details, payment, processing, success

  // Warn guest users before leaving page if they have tickets to download
  useEffect(() => {
    if (step === 'success' && isGuest) {
      const handleBeforeUnload = (e) => {
        e.preventDefault();
        e.returnValue = 'You have tickets available to download. If you leave now, you may not be able to access them again. Are you sure you want to leave?';
      };

      window.addEventListener('beforeunload', handleBeforeUnload);
      return () => window.removeEventListener('beforeunload', handleBeforeUnload);
    }
  }, [step, isGuest]);
  const getUserFullName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return '';
  };
  const [paymentPhone, setPaymentPhone] = useState(user?.phone_number || '');
  const [booking, setBooking] = useState(null);
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloadingTickets, setDownloadingTickets] = useState({});

  // Individual ticket details - each ticket gets its own fields
  const [ticketDetails, setTicketDetails] = useState(
    Array(quantity).fill(null).map((_, i) => ({
      ticket_index: i + 1,
      attendee_name: i === 0 ? getUserFullName() : '',
      attendee_email: i === 0 ? (user?.email || '') : '',
      attendee_phone: i === 0 ? (user?.phone_number || '') : '',
    }))
  );

  // Redirect if no event data
  if (!event || !tier) {
    return <Navigate to="/events" />;
  }

  const totalAmount = tier.price * quantity;

  const handleCreateBooking = async () => {
    setLoading(true);
    setError('');

    try {
      // Create tickets array with individual details for each ticket
      const tickets = ticketDetails.map((detail) => ({
        ticket_tier_id: tier.id,
        attendee_name: detail.attendee_name,
        attendee_email: detail.attendee_email,
        attendee_phone: detail.attendee_phone,
      }));

      // Use first ticket details as booking contact info
      const bookingContact = ticketDetails[0];

      const response = await bookingService.createBooking({
        event_id: event.id,
        contact_name: bookingContact.attendee_name,
        contact_email: bookingContact.attendee_email,
        contact_phone: bookingContact.attendee_phone,
        special_requests: '',
        tickets,
      });

      setBooking(response.data);
      // SKIP PAYMENT FOR TESTING: Go directly to success
      setStep('success');
    } catch (err) {
      const data = err.response?.data;
      // Extract the most useful error message from DRF responses
      let msg = 'Failed to create booking';
      if (data) {
        if (typeof data === 'string') {
          msg = data;
        } else if (data.detail) {
          msg = data.detail;
        } else if (data.message) {
          msg = data.message;
        } else if (data.non_field_errors) {
          msg = Array.isArray(data.non_field_errors) ? data.non_field_errors.join(', ') : data.non_field_errors;
        } else {
          // Flatten field-level errors
          const fieldErrors = Object.entries(data)
            .map(([field, errs]) => `${field}: ${Array.isArray(errs) ? errs.join(', ') : errs}`)
            .join(' | ');
          if (fieldErrors) msg = fieldErrors;
        }
      }
      setError(msg);    } finally {
      setLoading(false);
    }
  };

  const updateTicketDetail = (index, field, value) => {
    setTicketDetails(prev => 
      prev.map((ticket, i) => 
        i === index ? { ...ticket, [field]: value } : ticket
      )
    );
  };

  const copyFirstTicketToAll = () => {
    const firstTicket = ticketDetails[0];
    setTicketDetails(prev =>
      prev.map((ticket, index) => index === 0 ? ticket : {
        ...ticket,
        attendee_name: firstTicket.attendee_name,
        attendee_email: firstTicket.attendee_email,
        attendee_phone: firstTicket.attendee_phone,
      })
    );
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

  const handleDownloadTicket = async (ticketNumber) => {
    setDownloadingTickets(prev => ({ ...prev, [ticketNumber]: true }));
    try {
      const response = await bookingService.downloadTicket(ticketNumber);
      
      // Create a blob from the PDF data
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // Create a temporary link to download
      const link = document.createElement('a');
      link.href = url;
      link.download = `ticket_${ticketNumber}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download ticket:', error);
      alert('Failed to download ticket. Please try again.');
    } finally {
      setDownloadingTickets(prev => ({ ...prev, [ticketNumber]: false }));
    }
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
                {/* Guest Checkout Banner */}
                {isGuest && !isAuthenticated && (
                  <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h3 className="font-semibold text-blue-900">Continue as Guest</h3>
                        <p className="text-sm text-blue-700 mt-1">
                          You're checking out as a guest. Enter your details below to complete your booking.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <h2 className="text-xl font-bold text-gray-900 mb-2">Ticket Information</h2>
                <p className="text-gray-600 text-sm mb-6">
                  {quantity > 1
                    ? `You're booking ${quantity} tickets. Enter details for each attendee below.`
                    : "Enter attendee details for the ticket."}
                </p>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                    {error}
                  </div>
                )}

                <div className="space-y-5">
                  {/* Ticket Details - All tickets shown individually */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">Ticket Details ({quantity} {quantity === 1 ? 'ticket' : 'tickets'})</h3>
                      {quantity > 1 && (
                        <button
                          type="button"
                          onClick={copyFirstTicketToAll}
                          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                        >
                          Copy first ticket to all
                        </button>
                      )}
                    </div>

                    <div className="space-y-4">
                      {ticketDetails.map((ticket, index) => (
                        <div key={`ticket-${index}`} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <Ticket className="w-4 h-4 text-primary-600" />
                            <h4 className="font-medium text-gray-900">
                              Ticket #{index + 1}
                            </h4>
                            <span className="text-xs text-gray-500">({tier.name})</span>
                          </div>
                          <div className="grid md:grid-cols-3 gap-4">
                            <div>
                              <label className="label text-xs">Attendee Name *</label>
                              <input
                                type="text"
                                value={ticket.attendee_name}
                                onChange={(e) => updateTicketDetail(index, 'attendee_name', e.target.value)}
                                className="input text-sm"
                                placeholder="Full name"
                                required
                              />
                            </div>
                            <div>
                              <label className="label text-xs">Attendee Email *</label>
                              <input
                                type="email"
                                value={ticket.attendee_email}
                                onChange={(e) => updateTicketDetail(index, 'attendee_email', e.target.value)}
                                className="input text-sm"
                                placeholder="email@example.com"
                                required
                              />
                            </div>
                            <div>
                              <label className="label text-xs">Attendee Phone *</label>
                              <input
                                type="tel"
                                value={ticket.attendee_phone}
                                onChange={(e) => updateTicketDetail(index, 'attendee_phone', e.target.value)}
                                className="input text-sm"
                                placeholder="0712345678"
                                required
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleCreateBooking}
                    disabled={loading}
                    className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white font-semibold rounded-lg transition-colors"
                  >
                    {loading ? 'Creating Booking...' : `Continue to Payment - KES ${totalAmount.toLocaleString()}`}
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
                      placeholder="0712345678"
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
                  Please check your phone and enter your M-Pesa PIN to complete the payment.
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
                  Your tickets have been booked. Download them now or view them later in My Tickets.
                </p>

                {/* Warning Banner - Only for guests */}
                {isGuest && (
                  <div className="mb-6 p-4 bg-amber-50 border-2 border-amber-400 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
                      <div className="text-left">
                        <h4 className="font-bold text-amber-900 mb-1">Important: Download Your Tickets Now!</h4>
                        <p className="text-sm text-amber-800">
                          You're checking out as a guest. Please download your tickets before leaving this page. Once you leave, you won't be able to access them again.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Download Tickets Section */}
                {booking?.tickets?.length > 0 && (
                  <div className="mb-6 text-left">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3 text-center">
                      {booking.tickets.length > 1 ? 'Your Tickets' : 'Your Ticket'}
                    </h3>
                    <div className="space-y-2">
                      {booking.tickets.map((ticket, index) => (
                        <div key={ticket.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                          <div className="flex items-center gap-3">
                            <Ticket className="w-5 h-5 text-primary-600" />
                            <div>
                              <p className="text-sm font-medium text-gray-900">
                                {ticket.attendee_name || `Ticket #${index + 1}`}
                              </p>
                              <p className="text-xs text-gray-500">{ticket.ticket_number}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleDownloadTicket(ticket.ticket_number)}
                            disabled={downloadingTickets[ticket.ticket_number]}
                            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg disabled:opacity-50"
                          >
                            {downloadingTickets[ticket.ticket_number] ? (
                              <Loader className="w-4 h-4 animate-spin" />
                            ) : (
                              <Download className="w-4 h-4" />
                            )}
                            Download
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
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
