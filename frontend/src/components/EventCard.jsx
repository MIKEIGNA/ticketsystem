import { Link } from 'react-router-dom';
import { Calendar, MapPin, Ticket as TicketIcon } from 'lucide-react';
import { cn } from '../utils/cn';

const EventCard = ({ event, featured = false }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return {
      day: date.toLocaleDateString('en-US', { day: 'numeric' }),
      month: date.toLocaleDateString('en-US', { month: 'short' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const date = formatDate(event.start_datetime);
  const isPastEvent = new Date(event.start_datetime) < new Date();

  return (
    <Link
      to={`/events/${event.slug}`}
      className={cn(
        'group block bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100',
        featured && 'md:col-span-2 md:grid md:grid-cols-2'
      )}
    >
      {/* Image */}
      <div className={cn('relative overflow-hidden', featured ? 'aspect-[4/3]' : 'aspect-[16/10]')}>
        {/* Sports fixtures without poster: show enlarged team logos */}
        {event.category?.slug === 'sports' &&
          !event.poster_image &&
          event.match_data?.home_team &&
          event.match_data?.away_team ? (
            <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center gap-8 p-8">
              {/* Home Team Logo */}
              <div className="flex-1 flex flex-col items-center">
                {event.match_data.home_team_logo ? (
                  <img
                    src={event.match_data.home_team_logo}
                    alt={event.match_data.home_team}
                    className="w-24 h-24 object-contain drop-shadow-lg"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg">
                    <span className="text-3xl font-bold text-gray-600">
                      {event.match_data.home_team.charAt(0)}
                    </span>
                  </div>
                )}
                <span className="text-sm font-semibold text-gray-800 mt-3 text-center line-clamp-2">
                  {event.match_data.home_team}
                </span>
              </div>

              {/* VS Badge */}
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-lg font-bold text-gray-800">VS</span>
                </div>
              </div>

              {/* Away Team Logo */}
              <div className="flex-1 flex flex-col items-center">
                {event.match_data.away_team_logo ? (
                  <img
                    src={event.match_data.away_team_logo}
                    alt={event.match_data.away_team}
                    className="w-24 h-24 object-contain drop-shadow-lg"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg">
                    <span className="text-3xl font-bold text-gray-600">
                      {event.match_data.away_team.charAt(0)}
                    </span>
                  </div>
                )}
                <span className="text-sm font-semibold text-gray-800 mt-3 text-center line-clamp-2">
                  {event.match_data.away_team}
                </span>
              </div>
            </div>
        ) : (
          <img
            src={event.poster_image || '/placeholder-event.jpg'}
            alt={event.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        )}
        
        {/* Category Badge */}
        {event.category && (
          <div className="absolute top-3 left-3">
            <span
              className="px-3 py-1 text-xs font-medium text-white rounded-full"
              style={{ backgroundColor: event.category.color || '#ec4899' }}
            >
              {event.category.name}
            </span>
          </div>
        )}

        {/* Event Ended Badge */}
        {isPastEvent && (
          <div className="absolute top-3 right-3">
            <span className="px-3 py-1 text-xs font-medium text-white bg-gray-900/80 backdrop-blur-sm rounded-full">
              Event Ended
            </span>
          </div>
        )}

        {/* Sports fixtures: club badges from match_data (KPL) - only show when poster exists */}
        {event.poster_image &&
          event.category?.slug === 'sports' &&
          event.match_data?.home_team &&
          event.match_data?.away_team && (
            <div className="absolute bottom-3 left-3 flex items-center gap-1.5 bg-white/95 backdrop-blur-sm rounded-full px-2 py-1 shadow-sm border border-gray-100">
              <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center overflow-hidden">
                {event.match_data.home_team_logo ? (
                  <img
                    src={event.match_data.home_team_logo}
                    alt=""
                    className="w-7 h-7 object-contain"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <span className="text-xs font-bold text-gray-400">
                    {event.match_data.home_team.charAt(0)}
                  </span>
                )}
              </div>
              <span className="text-[10px] font-bold text-gray-400 px-0.5">v</span>
              <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center overflow-hidden">
                {event.match_data.away_team_logo ? (
                  <img
                    src={event.match_data.away_team_logo}
                    alt=""
                    className="w-7 h-7 object-contain"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <span className="text-xs font-bold text-gray-400">
                    {event.match_data.away_team.charAt(0)}
                  </span>
                )}
              </div>
            </div>
          )}

        {/* Price Badge */}
        {event.lowest_price !== null && (
          <div className="absolute bottom-3 right-3">
            <span className="px-3 py-1 text-sm font-semibold text-white bg-dark-900/80 backdrop-blur-sm rounded-lg">
              KES {event.lowest_price?.toLocaleString()}
            </span>
          </div>
        )}

        {/* Featured Badge */}
        {event.featured && !featured && (
          <div className="absolute top-3 right-3">
            <span className="px-2 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
              Featured
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Date */}
        <div className="flex items-start gap-4 mb-3">
          <div className="flex-shrink-0 w-14 h-14 bg-primary-50 rounded-lg flex flex-col items-center justify-center text-primary-600">
            <span className="text-xs font-semibold uppercase">{date.month}</span>
            <span className="text-xl font-bold">{date.day}</span>
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className={cn(
              'font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2',
              featured ? 'text-xl' : 'text-lg'
            )}>
              {event.title}
            </h3>
            {event.subtitle && (
              <p className="text-sm text-gray-500 line-clamp-1 mt-1">{event.subtitle}</p>
            )}
          </div>
        </div>

        {/* Details */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Calendar className="w-4 h-4 flex-shrink-0" />
            <span>{date.time}</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <MapPin className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">{event.venue_name}, {event.venue_city}</span>
          </div>
          
          {/* Show stadium for sports events if available */}
          {event.category?.slug === 'sports' && event.match_data?.stadium && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <MapPin className="w-4 h-4 flex-shrink-0 text-secondary-600" />
              <span className="truncate font-medium">{event.match_data.stadium}</span>
            </div>
          )}
        </div>

        {/* CTA */}
        <div className="mt-4 flex items-center justify-between">
          {isPastEvent ? (
            <span className="text-sm font-medium text-gray-500 flex items-center gap-1">
              View Results
            </span>
          ) : (
            <span className="text-sm font-medium text-primary-600 group-hover:text-primary-700 flex items-center gap-1">
              <TicketIcon className="w-4 h-4" />
              Get Tickets
            </span>
          )}
          
          {event.days_until_event > 0 && !isPastEvent && (
            <span className="text-xs text-gray-400">
              In {event.days_until_event} days
            </span>
          )}
          {isPastEvent && (
            <span className="text-xs text-gray-400">
              Event ended
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default EventCard;
