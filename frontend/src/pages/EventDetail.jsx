import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { eventService } from '../services/events';
import { useAuth } from '../context/AuthContext';
import { 
  Calendar, MapPin, Clock, Users, AlertCircle, 
  Check, Share2, Heart, ChevronRight, Ticket
} from 'lucide-react';
import { cn } from '../utils/cn';

const EventDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [event, setEvent] = useState(null);
  const [selectedTier, setSelectedTier] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const response = await eventService.getEvent(slug);
        setEvent(response.data);
      } catch (error) {
        console.error('Failed to fetch event:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvent();
  }, [slug]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return {
      weekday: date.toLocaleDateString('en-US', { weekday: 'long' }),
      date: date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const handleBookNow = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/events/${slug}` } });
      return;
    }

    if (!selectedTier) {
      return;
    }

    navigate('/checkout', {
      state: {
        event,
        tier: selectedTier,
        quantity,
      },
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="bg-white rounded-xl h-96 animate-pulse" />
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Event Not Found</h1>
          <Link to="/events" className="text-primary-600 font-semibold">
            Browse Events
          </Link>
        </div>
      </div>
    );
  }

  const date = formatDate(event.start_datetime);
  const availableTiers = event.ticket_tiers?.filter(t => t.is_on_sale) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Banner */}
      <div className="relative h-64 md:h-96">
        <img
          src={event.banner_image || event.poster_image || '/placeholder-event.jpg'}
          alt={event.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
        
        {/* Category Badge */}
        {event.category && (
          <div className="absolute top-4 left-4">
            <span
              className="px-4 py-2 text-sm font-medium text-white rounded-full"
              style={{ backgroundColor: event.category.color || '#ec4899' }}
            >
              {event.category.name}
            </span>
          </div>
        )}

        {/* Quick Actions */}
        <div className="absolute top-4 right-4 flex gap-2">
          <button className="p-2 bg-white/20 backdrop-blur-sm rounded-full text-white hover:bg-white/30 transition-colors">
            <Share2 className="w-5 h-5" />
          </button>
          <button className="p-2 bg-white/20 backdrop-blur-sm rounded-full text-white hover:bg-white/30 transition-colors">
            <Heart className="w-5 h-5" />
          </button>
        </div>

        {/* Title Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-2xl md:text-4xl font-bold text-white mb-2">
              {event.title}
            </h1>
            {event.subtitle && (
              <p className="text-white/80 text-lg">{event.subtitle}</p>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Event Info */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Event Details</h2>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Calendar className="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Date & Time</p>
                    <p className="font-semibold text-gray-900">{date.weekday}</p>
                    <p className="text-gray-700">{date.date}</p>
                    <p className="text-gray-700">{date.time}</p>
                    {event.doors_open && (
                      <p className="text-sm text-gray-500">
                        Doors open: {event.doors_open}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-secondary-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MapPin className="w-5 h-5 text-secondary-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Venue</p>
                    <p className="font-semibold text-gray-900">{event.venue?.name}</p>
                    <p className="text-gray-700">{event.venue?.address}</p>
                    <p className="text-gray-700">{event.venue?.city}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-bold text-gray-900 mb-4">About This Event</h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                {event.description}
              </p>
            </div>

            {/* Tags */}
            {event.tags && event.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {event.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar - Tickets */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Select Tickets</h2>

              {availableTiers.length > 0 ? (
                <div className="space-y-4">
                  {availableTiers.map((tier) => (
                    <div
                      key={tier.id}
                      onClick={() => setSelectedTier(tier)}
                      className={cn(
                        'p-4 rounded-lg border-2 cursor-pointer transition-all',
                        selectedTier?.id === tier.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-primary-300'
                      )}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-gray-900">{tier.name}</h3>
                        {selectedTier?.id === tier.id && (
                          <Check className="w-5 h-5 text-primary-600" />
                        )}
                      </div>
                      
                      {tier.description && (
                        <p className="text-sm text-gray-600 mb-2">{tier.description}</p>
                      )}

                      {tier.benefits && tier.benefits.length > 0 && (
                        <ul className="text-sm text-gray-600 mb-3 space-y-1">
                          {tier.benefits.map((benefit, idx) => (
                            <li key={idx} className="flex items-center gap-1">
                              <Check className="w-3 h-3 text-green-500" />
                              {benefit}
                            </li>
                          ))}
                        </ul>
                      )}

                      <div className="flex items-center justify-between">
                        <span className="text-xl font-bold text-primary-600">
                          KES {tier.price.toLocaleString()}
                        </span>
                        <span className="text-sm text-gray-500">
                          {tier.available_quantity} left
                        </span>
                      </div>
                    </div>
                  ))}

                  {/* Quantity Selector */}
                  {selectedTier && (
                    <div className="pt-4 border-t">
                      <label className="text-sm font-medium text-gray-700 mb-2 block">
                        Quantity
                      </label>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => setQuantity(Math.max(1, quantity - 1))}
                          className="w-10 h-10 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50"
                          disabled={quantity <= 1}
                        >
                          -
                        </button>
                        <span className="w-12 text-center font-semibold">{quantity}</span>
                        <button
                          onClick={() => setQuantity(Math.min(selectedTier.max_per_order, quantity + 1))}
                          className="w-10 h-10 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50"
                          disabled={quantity >= selectedTier.max_per_order}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Total and CTA */}
                  {selectedTier && (
                    <div className="pt-4 border-t">
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-gray-600">Total</span>
                        <span className="text-2xl font-bold text-primary-600">
                          KES {(selectedTier.price * quantity).toLocaleString()}
                        </span>
                      </div>
                      <button
                        onClick={handleBookNow}
                        className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <Ticket className="w-5 h-5" />
                        Book Now
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600">No tickets available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventDetail;
