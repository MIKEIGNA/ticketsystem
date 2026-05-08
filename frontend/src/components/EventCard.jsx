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
        <img
          src={event.poster_image || '/placeholder-event.jpg'}
          alt={event.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        
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
        </div>

        {/* CTA */}
        <div className="mt-4 flex items-center justify-between">
          <span className="text-sm font-medium text-primary-600 group-hover:text-primary-700 flex items-center gap-1">
            <TicketIcon className="w-4 h-4" />
            Get Tickets
          </span>
          
          {event.days_until_event > 0 && (
            <span className="text-xs text-gray-400">
              In {event.days_until_event} days
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default EventCard;
