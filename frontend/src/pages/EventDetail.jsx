import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { eventService } from '../services/events';
import { useAuth } from '../context/AuthContext';
import { 
  Calendar, MapPin, Clock, Users, AlertCircle, 
  Check, Share2, Heart, ChevronRight, Ticket, UserPlus, LogIn, User
} from 'lucide-react';
import { cn } from '../utils/cn';
import '../styles/clubColors.css';
import MatchScore from '../components/MatchScore';

const EventDetail = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [event, setEvent] = useState(null);
  const [selectedTier, setSelectedTier] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);

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

  const isPastEvent = event ? new Date(event.start_datetime) < new Date() : false;

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return {
      weekday: date.toLocaleDateString('en-US', { weekday: 'long' }),
      date: date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const handleBookNow = () => {
    if (!selectedTier) {
      return;
    }

    // If not authenticated, show auth options modal
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    // Proceed to checkout for authenticated users
    navigate('/checkout', {
      state: {
        event,
        tier: selectedTier,
        quantity,
        isGuest: false,
      },
    });
  };

  const handleContinueAsGuest = () => {
    setShowAuthModal(false);
    navigate('/checkout', {
      state: {
        event,
        tier: selectedTier,
        quantity,
        isGuest: true,
      },
    });
  };

  const handleSignIn = () => {
    navigate('/login', { state: { from: `/events/${slug}`, redirectToCheckout: true, event, tier: selectedTier, quantity } });
  };

  const handleCreateAccount = () => {
    navigate('/register', { state: { from: `/events/${slug}`, redirectToCheckout: true, event, tier: selectedTier, quantity } });
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

            {/* Match Score - Only for sports events with match_data */}
            {event.match_data?.home_team && event.match_data?.away_team && (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-xl font-bold text-gray-900">Match Score</h2>
                  <div className="flex gap-2">
                    <span className="fkf-badge">FKF</span>
                    <span className="sportpesa-badge">SportPesa</span>
                    {event.match_data.category && (
                      <span className={`category-${event.match_data.category?.toLowerCase()}-badge`}>
                        {event.match_data.category} Category
                      </span>
                    )}
                  </div>
                </div>
                <MatchScore
                  slug={event.slug}
                  matchData={event.match_data}
                  startDatetime={event.start_datetime}
                />
              </div>
            )}

            {/* Description */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-bold text-gray-900 mb-4">About This Event</h2>
              <div 
                className="event-description text-gray-700 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: event.description }}
                style={{
                  '& h2': { fontSize: '1.5rem', fontWeight: '700', color: '#111827', marginBottom: '0.75rem', marginTop: '1rem' },
                  '& h3': { fontSize: '1.125rem', fontWeight: '600', color: '#374151', marginBottom: '0.5rem', marginTop: '1rem' },
                  '& p': { marginBottom: '0.75rem', lineHeight: '1.625' },
                  '& ul': { listStyleType: 'disc', paddingLeft: '1.25rem', marginBottom: '0.75rem' },
                  '& li': { marginBottom: '0.25rem' },
                  '& strong': { fontWeight: '600', color: '#111827' },
                  '& em': { fontStyle: 'italic', color: '#6B7280' },
                }}
              />
              {/* Custom CSS for event description HTML */}
              <style>{`
                .event-description h2 {
                  font-size: 1.25rem;
                  font-weight: 700;
                  color: #111827;
                  margin-bottom: 0.75rem;
                  margin-top: 1rem;
                }
                .event-description h2:first-child {
                  margin-top: 0;
                }
                .event-description h3 {
                  font-size: 1.125rem;
                  font-weight: 600;
                  color: #374151;
                  margin-bottom: 0.5rem;
                  margin-top: 1rem;
                }
                .event-description p {
                  margin-bottom: 0.75rem;
                  line-height: 1.625;
                }
                .event-description ul {
                  list-style-type: disc;
                  padding-left: 1.5rem;
                  margin-bottom: 0.75rem;
                }
                .event-description li {
                  margin-bottom: 0.375rem;
                }
                .event-description strong {
                  font-weight: 600;
                  color: #111827;
                }
                .event-description em {
                  font-style: italic;
                  color: #6B7280;
                  font-size: 0.875rem;
                }
              `}</style>
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

          {/* Sidebar - Tickets or Results */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 sticky top-24">
              {isPastEvent ? (
                <>
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Match Results</h2>
                  {event.match_data?.home_team && event.match_data?.away_team ? (
                    <div className="text-center py-6">
                      <div className="flex items-center justify-center gap-4 mb-6">
                        {/* Home Team */}
                        <div className="flex flex-col items-center">
                          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden mb-2">
                            {event.match_data.home_team_logo ? (
                              <img
                                src={event.match_data.home_team_logo}
                                alt={event.match_data.home_team}
                                className="w-12 h-12 object-contain"
                                referrerPolicy="no-referrer"
                              />
                            ) : (
                              <div className="text-xl font-bold text-gray-400">
                                {event.match_data.home_team.charAt(0)}
                              </div>
                            )}
                          </div>
                          <p className="font-semibold text-gray-900 text-sm">{event.match_data.home_team}</p>
                        </div>

                        {/* Score */}
                        <div className="flex flex-col items-center px-4">
                          <div className="text-3xl font-bold text-gray-900">
                            {event.match_data.home_score ?? 0} - {event.match_data.away_score ?? 0}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">Final Score</p>
                        </div>

                        {/* Away Team */}
                        <div className="flex flex-col items-center">
                          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden mb-2">
                            {event.match_data.away_team_logo ? (
                              <img
                                src={event.match_data.away_team_logo}
                                alt={event.match_data.away_team}
                                className="w-12 h-12 object-contain"
                                referrerPolicy="no-referrer"
                              />
                            ) : (
                              <div className="text-xl font-bold text-gray-400">
                                {event.match_data.away_team.charAt(0)}
                              </div>
                            )}
                          </div>
                          <p className="font-semibold text-gray-900 text-sm">{event.match_data.away_team}</p>
                        </div>
                      </div>
                      <div className="bg-gray-100 rounded-lg p-4 text-center">
                        <p className="text-sm text-gray-600">This event has ended</p>
                        <p className="text-xs text-gray-500 mt-1">Ticket sales are closed</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-2">This event has ended</p>
                      <p className="text-sm text-gray-500">Ticket sales are closed</p>
                    </div>
                  )}
                </>
              ) : (
                <>
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
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Auth Options Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Ticket className="w-8 h-8 text-primary-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Continue Booking</h2>
              <p className="text-gray-600">Choose how you'd like to proceed with your ticket purchase</p>
            </div>

            <div className="space-y-3">
              {/* Sign In Option */}
              <button
                onClick={handleSignIn}
                className="w-full p-4 border-2 border-gray-200 rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                    <LogIn className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">Sign In</h3>
                    <p className="text-sm text-gray-500">Already have an account</p>
                  </div>
                </div>
              </button>

              {/* Create Account Option */}
              <button
                onClick={handleCreateAccount}
                className="w-full p-4 border-2 border-gray-200 rounded-xl hover:border-green-500 hover:bg-green-50 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center group-hover:bg-green-200 transition-colors">
                    <UserPlus className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">Create Account</h3>
                    <p className="text-sm text-gray-500">New to TicketHub</p>
                  </div>
                </div>
              </button>

              {/* Continue as Guest Option */}
              <button
                onClick={handleContinueAsGuest}
                className="w-full p-4 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                    <User className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">Continue as Guest</h3>
                    <p className="text-sm text-gray-500">Quick checkout without account</p>
                  </div>
                </div>
              </button>
            </div>

            <button
              onClick={() => setShowAuthModal(false)}
              className="w-full mt-6 py-3 text-gray-500 hover:text-gray-700 font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EventDetail;
