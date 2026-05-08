import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { bookingService } from '../services/bookings';
import { 
  Ticket, Calendar, MapPin, QrCode, Download, 
  CheckCircle, Clock, AlertCircle, ChevronRight 
} from 'lucide-react';
import { cn } from '../utils/cn';

const MyTickets = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const response = await bookingService.getMyTickets();
        setTickets(response.data);
      } catch (error) {
        console.error('Failed to fetch tickets:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'valid':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'used':
        return <CheckCircle className="w-5 h-5 text-gray-500" />;
      case 'cancelled':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'valid':
        return 'Valid';
      case 'used':
        return 'Used';
      case 'cancelled':
        return 'Cancelled';
      default:
        return 'Pending';
    }
  };

  const upcomingTickets = tickets.filter(t => 
    t.status === 'valid' && new Date(t.event_date) >= new Date()
  );
  const pastTickets = tickets.filter(t => 
    t.status === 'used' || new Date(t.event_date) < new Date()
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="animate-pulse space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-xl h-32" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Tickets</h1>
          <p className="text-gray-600">
            Manage your event tickets and bookings
          </p>
        </div>

        {tickets.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Ticket className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No tickets yet</h3>
            <p className="text-gray-600 mb-6">
              Browse events and book your first tickets
            </p>
            <Link
              to="/events"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700"
            >
              Browse Events
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Upcoming Events */}
            {upcomingTickets.length > 0 && (
              <section>
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-primary-600" />
                  Upcoming Events
                </h2>
                <div className="space-y-4">
                  {upcomingTickets.map((ticket) => (
                    <TicketCard
                      key={ticket.id}
                      ticket={ticket}
                      formatDate={formatDate}
                      getStatusIcon={getStatusIcon}
                      getStatusText={getStatusText}
                    />
                  ))}
                </div>
              </section>
            )}

            {/* Past Events */}
            {pastTickets.length > 0 && (
              <section>
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-gray-500" />
                  Past Events
                </h2>
                <div className="space-y-4">
                  {pastTickets.map((ticket) => (
                    <TicketCard
                      key={ticket.id}
                      ticket={ticket}
                      formatDate={formatDate}
                      getStatusIcon={getStatusIcon}
                      getStatusText={getStatusText}
                      isPast
                    />
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const TicketCard = ({ ticket, formatDate, getStatusIcon, getStatusText, isPast }) => {
  return (
    <div className={cn(
      'bg-white rounded-xl p-6 shadow-sm border border-gray-100',
      isPast && 'opacity-75'
    )}>
      <div className="flex flex-col md:flex-row gap-6">
        {/* QR Code */}
        <div className="flex-shrink-0">
          <div className="w-32 h-32 bg-gray-100 rounded-lg flex items-center justify-center">
            {ticket.qr_code_url ? (
              <img
                src={ticket.qr_code_url}
                alt="Ticket QR Code"
                className="w-28 h-28"
              />
            ) : (
              <QrCode className="w-12 h-12 text-gray-400" />
            )}
          </div>
        </div>

        {/* Ticket Info */}
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className="text-lg font-bold text-gray-900">{ticket.event_title}</h3>
              <p className="text-primary-600 font-medium">{ticket.ticket_tier_name}</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full">
              {getStatusIcon(ticket.status)}
              <span className="text-sm font-medium text-gray-700">
                {getStatusText(ticket.status)}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="flex items-center gap-2 text-gray-600">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">{formatDate(ticket.event_date)}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <MapPin className="w-4 h-4" />
              <span className="text-sm">{ticket.venue_name}</span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <div>
              <p className="text-sm text-gray-500">Ticket Number</p>
              <p className="font-mono font-semibold text-gray-900">{ticket.ticket_number}</p>
            </div>

            {!isPast && (
              <div className="flex gap-2">
                <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg">
                  <Download className="w-4 h-4" />
                  Download
                </button>
                <Link
                  to={`/tickets/${ticket.ticket_number}`}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg"
                >
                  View Details
                  <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyTickets;
