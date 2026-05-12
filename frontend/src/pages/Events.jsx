import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { eventService } from '../services/events';
import EventCard from '../components/EventCard';
import { Search, Calendar, MapPin, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../utils/cn';

// Quick-filter tabs shown above the grid
const TABS = [
  { value: '',           label: 'All Events' },
  { value: 'upcoming',   label: 'Upcoming' },
  { value: 'today',      label: 'Today' },
  { value: 'this_week',  label: 'This Week' },
  { value: 'this_month', label: 'This Month' },
  { value: 'finished',   label: 'Past' },
];

const CITIES = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Kakamega', 'Kisii', 'Machakos', 'Murang\'a'];

// Format a Date object to YYYY-MM-DD for <input type="date">
const toInputDate = (d) => d.toISOString().slice(0, 10);

// Human-readable label for a selected date
const formatDateLabel = (dateStr) => {
  if (!dateStr) return null;
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-KE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
};

const Events = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [events, setEvents]       = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [total, setTotal]         = useState(0);

  const [filters, setFilters] = useState({
    search:        searchParams.get('search')        || '',
    category_slug: searchParams.get('category_slug') || '',
    filter:        searchParams.get('filter')        || '',   // tab value
    city:          searchParams.get('city')          || '',
    date:          searchParams.get('date')          || '',   // YYYY-MM-DD exact day
    min_price:     searchParams.get('min_price')     || '',
    max_price:     searchParams.get('max_price')     || '',
  });

  // ── Fetch events whenever filters change ──────────────────────────────────
  const fetchEvents = useCallback(async (f) => {
    setLoading(true);
    try {
      // Build params — omit empty strings
      const params = {};
      Object.entries(f).forEach(([k, v]) => { if (v !== '') params[k] = v; });

      const [eventsRes, catsRes] = await Promise.all([
        eventService.getEvents({ ...params, ordering: 'start_datetime' }),
        categories.length ? Promise.resolve(null) : eventService.getCategories(),
      ]);

      const data = eventsRes.data;
      setEvents(data.results ?? data ?? []);
      setTotal(data.count ?? (data.results ?? data ?? []).length);

      if (catsRes) {
        const cats = catsRes.data;
        setCategories(Array.isArray(cats) ? cats : cats.results ?? []);
      }
    } catch (err) {
      console.error('Failed to fetch events:', err);
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchEvents(filters);
  }, [filters, fetchEvents]);

  // ── Update a single filter ────────────────────────────────────────────────
  const setFilter = (key, value) => {
    const next = { ...filters, [key]: value };

    // When a specific date is picked, clear the tab filter (they conflict)
    if (key === 'date' && value) next.filter = '';
    // When a tab is picked, clear the specific date
    if (key === 'filter' && value) next.date = '';

    setFilters(next);

    const params = new URLSearchParams();
    Object.entries(next).forEach(([k, v]) => { if (v) params.set(k, v); });
    setSearchParams(params);
  };

  const clearAll = () => {
    const empty = { search: '', category_slug: '', filter: '', city: '', date: '', min_price: '', max_price: '' };
    setFilters(empty);
    setSearchParams(new URLSearchParams());
  };

  // ── Date navigation (prev / next day when a date is selected) ────────────
  const shiftDate = (days) => {
    const base = filters.date ? new Date(filters.date + 'T00:00:00') : new Date();
    base.setDate(base.getDate() + days);
    setFilter('date', toInputDate(base));
  };

  const hasActiveFilters = Object.entries(filters).some(([k, v]) => v && k !== 'filter');
  const activeCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ── Page header ── */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Events</h1>
          <p className="text-gray-500 mt-1">Browse and book tickets for upcoming events across Kenya</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">

        {/* ── Search + primary filters ── */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex flex-col lg:flex-row gap-3">

            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events, teams, venues…"
                value={filters.search}
                onChange={(e) => setFilter('search', e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Category */}
            <select
              value={filters.category_slug}
              onChange={(e) => setFilter('category_slug', e.target.value)}
              className="lg:w-44 px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.slug}>{c.name}</option>
              ))}
            </select>

            {/* City */}
            <select
              value={filters.city}
              onChange={(e) => setFilter('city', e.target.value)}
              className="lg:w-40 px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Cities</option>
              {CITIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>

            {/* Clear */}
            {activeCount > 0 && (
              <button
                onClick={clearAll}
                className="flex items-center gap-1.5 px-3 py-2.5 text-sm text-red-600 hover:text-red-700 border border-red-200 rounded-lg hover:bg-red-50 transition-colors whitespace-nowrap"
              >
                <X className="w-4 h-4" />
                Clear all
              </button>
            )}
          </div>

          {/* Price range */}
          <div className="mt-3 pt-3 border-t border-gray-100 flex flex-wrap items-center gap-3">
            <span className="text-xs text-gray-500 font-medium">Price (KES):</span>
            <input
              type="number"
              placeholder="Min"
              value={filters.min_price}
              onChange={(e) => setFilter('min_price', e.target.value)}
              className="w-24 px-3 py-1.5 text-sm border border-gray-200 rounded-lg"
            />
            <span className="text-gray-400 text-sm">–</span>
            <input
              type="number"
              placeholder="Max"
              value={filters.max_price}
              onChange={(e) => setFilter('max_price', e.target.value)}
              className="w-24 px-3 py-1.5 text-sm border border-gray-200 rounded-lg"
            />
          </div>
        </div>

        {/* ── Date picker row ── */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Calendar className="w-4 h-4 text-primary-500" />
              Pick a date
            </div>

            <div className="flex items-center gap-2 flex-1">
              {/* Prev day */}
              {filters.date && (
                <button
                  onClick={() => shiftDate(-1)}
                  className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  title="Previous day"
                >
                  <ChevronLeft className="w-4 h-4 text-gray-500" />
                </button>
              )}

              <input
                type="date"
                value={filters.date}
                onChange={(e) => setFilter('date', e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />

              {/* Next day */}
              {filters.date && (
                <button
                  onClick={() => shiftDate(1)}
                  className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  title="Next day"
                >
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                </button>
              )}

              {/* Selected date label */}
              {filters.date && (
                <div className="flex items-center gap-2 ml-1">
                  <span className="text-sm font-semibold text-primary-700 bg-primary-50 px-3 py-1 rounded-full">
                    {formatDateLabel(filters.date)}
                  </span>
                  <button
                    onClick={() => setFilter('date', '')}
                    className="text-gray-400 hover:text-gray-600"
                    title="Clear date"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Quick-filter tabs ── */}
        {!filters.date && (
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {TABS.map((tab) => (
              <button
                key={tab.value}
                onClick={() => setFilter('filter', tab.value)}
                className={cn(
                  'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors border',
                  filters.filter === tab.value
                    ? 'bg-primary-600 text-white border-primary-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300 hover:text-primary-600'
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        )}

        {/* ── Results ── */}
        <div>
          {/* Result count + active date banner */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-500">
              {loading ? 'Loading…' : (
                <>
                  <span className="font-semibold text-gray-900">{total}</span>
                  {' '}event{total !== 1 ? 's' : ''}
                  {filters.date && (
                    <span className="text-primary-600"> on {formatDateLabel(filters.date)}</span>
                  )}
                  {filters.filter && !filters.date && (
                    <span className="text-gray-500"> · {TABS.find(t => t.value === filters.filter)?.label}</span>
                  )}
                </>
              )}
            </p>
          </div>

          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="bg-white rounded-xl h-72 animate-pulse" />
              ))}
            </div>
          ) : events.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 bg-white rounded-xl border border-gray-100">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">No events found</h3>
              <p className="text-gray-500 text-sm mb-4">
                {filters.date
                  ? `No events scheduled for ${formatDateLabel(filters.date)}`
                  : 'Try adjusting your filters'}
              </p>
              <div className="flex justify-center gap-3">
                {filters.date && (
                  <>
                    <button
                      onClick={() => shiftDate(-1)}
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                    >
                      ← Previous day
                    </button>
                    <button
                      onClick={() => shiftDate(1)}
                      className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Next day →
                    </button>
                  </>
                )}
                <button
                  onClick={clearAll}
                  className="text-sm text-gray-500 hover:text-gray-700 font-medium"
                >
                  Clear filters
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Events;
