import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { eventService } from '../services/events';
import EventCard from '../components/EventCard';
import { Search, Filter, Calendar, MapPin, X } from 'lucide-react';
import { cn } from '../utils/cn';

const Events = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    filter: searchParams.get('filter') || 'upcoming',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    city: searchParams.get('city') || '',
    date_from: searchParams.get('date_from') || '',
    date_to: searchParams.get('date_to') || '',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [eventsRes, categoriesRes] = await Promise.all([
          eventService.getEvents({
            ...filters,
            page: 1,
          }),
          eventService.getCategories(),
        ]);
        setEvents(eventsRes.data.results || eventsRes.data || []);
        setCategories(Array.isArray(categoriesRes.data) ? categoriesRes.data : categoriesRes.data.results || []);
      } catch (error) {
        console.error('Failed to fetch events:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  const updateFilter = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    // Update URL params
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    setSearchParams(params);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      filter: 'upcoming',
      min_price: '',
      max_price: '',
      city: '',
      date_from: '',
      date_to: '',
    });
    setSearchParams(new URLSearchParams());
  };

  const activeFiltersCount = Object.values(filters).filter(v => v && v !== 'upcoming').length;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Discover Events
          </h1>
          <p className="text-gray-600">
            Find the perfect event for you
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search events..."
                value={filters.search}
                onChange={(e) => updateFilter('search', e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <select
              value={filters.category}
              onChange={(e) => updateFilter('category', e.target.value)}
              className="lg:w-48 px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.slug}>
                  {cat.name}
                </option>
              ))}
            </select>

            {/* Date Filter */}
            <select
              value={filters.filter}
              onChange={(e) => updateFilter('filter', e.target.value)}
              className="lg:w-40 px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="upcoming">Upcoming</option>
              <option value="today">Today</option>
              <option value="this_week">This Week</option>
              <option value="this_month">This Month</option>
              <option value="custom">Custom Range</option>
              <option value="finished">Past Events</option>
            </select>
          </div>

          {/* Additional Filters */}
          <div className="mt-4 pt-4 border-t flex flex-wrap items-center gap-4">
            {/* Price Range */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Price:</span>
              <input
                type="number"
                placeholder="Min"
                value={filters.min_price}
                onChange={(e) => updateFilter('min_price', e.target.value)}
                className="w-24 px-3 py-2 text-sm border border-gray-200 rounded-lg"
              />
              <span className="text-gray-400">-</span>
              <input
                type="number"
                placeholder="Max"
                value={filters.max_price}
                onChange={(e) => updateFilter('max_price', e.target.value)}
                className="w-24 px-3 py-2 text-sm border border-gray-200 rounded-lg"
              />
            </div>

            {/* City Filter */}
            <select
              value={filters.city}
              onChange={(e) => updateFilter('city', e.target.value)}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg"
            >
              <option value="">All Cities</option>
              <option value="Nairobi">Nairobi</option>
              <option value="Mombasa">Mombasa</option>
              <option value="Kisumu">Kisumu</option>
              <option value="Nakuru">Nakuru</option>
            </select>

            {/* Custom Date Range */}
            {filters.filter === 'custom' && (
              <div className="flex items-center gap-2">
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) => updateFilter('date_from', e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-200 rounded-lg"
                />
                <span className="text-gray-400">to</span>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) => updateFilter('date_to', e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-200 rounded-lg"
                />
              </div>
            )}

            {/* Clear Filters */}
            {activeFiltersCount > 0 && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 text-sm text-red-600 hover:text-red-700"
              >
                <X className="w-4 h-4" />
                Clear ({activeFiltersCount})
              </button>
            )}
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-white rounded-xl h-80 animate-pulse" />
            ))}
          </div>
        ) : events.length > 0 ? (
          <>
            <div className="flex items-center justify-between mb-4">
              <p className="text-gray-600">
                Showing <span className="font-semibold">{events.length}</span> events
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No events found
            </h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your filters or search for something else
            </p>
            <button
              onClick={clearFilters}
              className="text-primary-600 font-semibold hover:text-primary-700"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Events;
