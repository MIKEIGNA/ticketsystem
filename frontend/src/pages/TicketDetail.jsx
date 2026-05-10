import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { bookingService } from '../services/bookings';
import { 
  Ticket, Calendar, MapPin, QrCode, Download, 
  CheckCircle, Clock, AlertCircle, User, Phone, 
  Mail, CreditCard, ArrowLeft, Share2, Printer
} from 'lucide-react';

const TicketDetail = () => {
  const { ticketNumber } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const response = await bookingService.getTicketDetail(ticketNumber);
        setTicket(response.data);
      } catch (error) {
        console.error('Failed to fetch ticket:', error);
      } finally {
        setLoading(false);
      }
    };

    if (ticketNumber) {
      fetchTicket();
    }
  }, [ticketNumber]);

  const handleDownload = async () => {
    setDownloading(true);
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
      setDownloading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'valid':
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Valid</span>
          </div>
        );
      case 'used':
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 text-gray-700 rounded-full">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Used</span>
          </div>
        );
      case 'cancelled':
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-red-100 text-red-700 rounded-full">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Cancelled</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-medium">Pending</span>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="animate-pulse space-y-4">
            <div className="bg-white rounded-xl h-64" />
            <div className="bg-white rounded-xl h-32" />
          </div>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-xl p-12 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">Ticket Not Found</h3>
            <p className="text-gray-600 mb-6">
              The ticket you're looking for doesn't exist or you don't have access to it.
            </p>
            <Link
              to="/my-tickets"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to My Tickets
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            to="/my-tickets"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to My Tickets
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Ticket Details</h1>
        </div>

        <div className="space-y-6">
          {/* Main Ticket Card */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            {/* Ticket Header */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Ticket className="w-6 h-6 text-white" />
                  <h2 className="text-xl font-bold text-white">{ticket.event_title}</h2>
                </div>
                {getStatusBadge(ticket.status)}
              </div>
            </div>

            <div className="p-6">
              <div className="flex flex-col md:flex-row gap-6">
                {/* QR Code Section */}
                <div className="flex-shrink-0">
                  <div className="w-48 h-48 bg-gray-100 rounded-xl flex items-center justify-center border-2 border-dashed border-gray-300">
                    {ticket.qr_code_url ? (
                      <img
                        src={ticket.qr_code_url}
                        alt="Ticket QR Code"
                        className="w-40 h-40"
                      />
                    ) : (
                      <div className="text-center">
                        <QrCode className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-xs text-gray-500">QR Code</p>
                      </div>
                    )}
                  </div>
                  {ticket.checked_in && (
                    <div className="mt-2 text-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mx-auto" />
                      <p className="text-xs text-green-600 font-medium mt-1">Checked In</p>
                      {ticket.checked_in_at && (
                        <p className="text-xs text-gray-500">
                          {new Date(ticket.checked_in_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Ticket Details */}
                <div className="flex-1 space-y-4">
                  {/* Event Information */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="flex items-start gap-3">
                      <Calendar className="w-5 h-5 text-primary-600 mt-0.5" />
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Date & Time</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {formatDate(ticket.event_date)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <MapPin className="w-5 h-5 text-primary-600 mt-0.5" />
                      <div>
                        <p className="text-xs text-gray-500 mb-1">Venue</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {ticket.venue_name}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Ticket Information */}
                  <div className="border-t pt-4">
                    <h3 className="text-sm font-semibold text-gray-900 mb-3">Ticket Information</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Ticket Number</span>
                        <span className="text-sm font-mono font-semibold text-gray-900">
                          {ticket.ticket_number}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Ticket Type</span>
                        <span className="text-sm font-semibold text-gray-900">
                          {ticket.ticket_tier_name}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Price Paid</span>
                        <span className="text-sm font-semibold text-gray-900">
                          KES {ticket.price_paid?.toLocaleString() || '0'}
                        </span>
                      </div>
                      {ticket.seat_number && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Seat Number</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {ticket.seat_number}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Attendee Information */}
                  {(ticket.attendee_name || ticket.attendee_email || ticket.attendee_phone) && (
                    <div className="border-t pt-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3">Attendee Information</h3>
                      <div className="space-y-2">
                        {ticket.attendee_name && (
                          <div className="flex items-center gap-3">
                            <User className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-900">{ticket.attendee_name}</span>
                          </div>
                        )}
                        {ticket.attendee_email && (
                          <div className="flex items-center gap-3">
                            <Mail className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-900">{ticket.attendee_email}</span>
                          </div>
                        )}
                        {ticket.attendee_phone && (
                          <div className="flex items-center gap-3">
                            <Phone className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-900">{ticket.attendee_phone}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleDownload}
                disabled={downloading || ticket.status !== 'valid'}
                className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {downloading ? (
                  <>
                    <Clock className="w-4 h-4 animate-spin" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Download PDF
                  </>
                )}
              </button>
              
              <button
                onClick={() => window.print()}
                className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200"
              >
                <Printer className="w-4 h-4" />
                Print Ticket
              </button>

              <button
                onClick={() => {
                  if (navigator.share) {
                    navigator.share({
                      title: ticket.event_title,
                      text: `My ticket for ${ticket.event_title} - Ticket #${ticket.ticket_number}`,
                      url: window.location.href
                    });
                  } else {
                    navigator.clipboard.writeText(window.location.href);
                    alert('Link copied to clipboard!');
                  }
                }}
                className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
            </div>
          </div>

          {/* Important Information */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="text-sm font-bold text-blue-900 mb-2">Important Information</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• This ticket is valid only for the event and date shown above</li>
              <li>• Present this QR code at the venue for entry</li>
              <li>• Do not share your QR code with others</li>
              <li>• This ticket cannot be transferred or resold</li>
              <li>• For assistance, contact support at support@brightpassticket.co.ke</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;
