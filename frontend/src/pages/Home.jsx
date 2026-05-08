import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { eventService } from '../services/events';
import Hero from '../components/Hero';
import EventCard from '../components/EventCard';
import { Music, Trophy, Drama, Briefcase, Calendar, ArrowRight } from 'lucide-react';
import { cn } from '../utils/cn';

const Home = () => {
  const [featuredEvents, setFeaturedEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [eventsRes, categoriesRes] = await Promise.all([
          eventService.getFeaturedEvents(),
          eventService.getCategories(),
        ]);
        setFeaturedEvents(eventsRes.data || []);
        setCategories(Array.isArray(categoriesRes.data) ? categoriesRes.data : categoriesRes.data?.results || []);
      } catch (error) {
        console.error('Failed to fetch home data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const categoryIcons = {
    'Music': Music,
    'Sports': Trophy,
    'Theatre': Drama,
    'Conferences': Briefcase,
    'Comedy': Drama,
    'Festivals': Calendar,
  };

  return (
    <div className="animate-fade-in">
      <Hero />

      {/* Categories Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Browse by Category
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Find the perfect event for you. From electrifying concerts to thrilling sports matches.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {categories.map((category) => {
              const Icon = categoryIcons[category.name] || Calendar;
              return (
                <Link
                  key={category.id}
                  to={`/events?category=${category.slug}`}
                  className="group p-6 bg-gray-50 rounded-xl hover:bg-primary-50 transition-colors"
                >
                  <div
                    className={cn(
                      'w-12 h-12 rounded-lg flex items-center justify-center mb-3 mx-auto',
                      'bg-white group-hover:scale-110 transition-transform'
                    )}
                    style={{ color: category.color || '#ec4899' }}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 text-center">
                    {category.name}
                  </h3>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Featured Events Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Featured Events
              </h2>
              <p className="text-gray-600">
                Don&apos;t miss out on these upcoming highlights
              </p>
            </div>
            <Link
              to="/events?filter=upcoming"
              className="hidden md:inline-flex items-center gap-2 text-primary-600 font-semibold hover:text-primary-700"
            >
              View All Events
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="bg-white rounded-xl h-80 animate-pulse" />
              ))}
            </div>
          ) : featuredEvents.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredEvents.map((event, index) => (
                <EventCard
                  key={event.id}
                  event={event}
                  featured={index === 0}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No featured events at the moment.</p>
            </div>
          )}

          <div className="mt-8 text-center md:hidden">
            <Link
              to="/events"
              className="inline-flex items-center gap-2 text-primary-600 font-semibold"
            >
              View All Events
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Get your tickets in just a few simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '1',
                title: 'Find Your Event',
                description: 'Browse through thousands of events or search for your favorite artists and venues.',
                color: 'bg-primary-100 text-primary-600',
              },
              {
                step: '2',
                title: 'Select Your Tickets',
                description: 'Choose your preferred seats and ticket tiers. Prices are all-inclusive.',
                color: 'bg-secondary-100 text-secondary-600',
              },
              {
                step: '3',
                title: 'Pay with M-Pesa',
                description: 'Secure payment via M-Pesa. Get your digital tickets instantly via email.',
                color: 'bg-green-100 text-green-600',
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className={cn('w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4', item.color)}>
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-primary-600 to-secondary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Experience Amazing Events?
          </h2>
          <p className="text-white/80 mb-8 max-w-2xl mx-auto">
            Join thousands of event-goers who trust TicketHub for their ticketing needs.
            Sign up today and never miss out on the best events in Kenya.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/register"
              className="px-8 py-3 bg-white text-primary-600 font-semibold rounded-xl hover:bg-gray-100 transition-colors"
            >
              Create Account
            </Link>
            <Link
              to="/events"
              className="px-8 py-3 bg-white/10 text-white font-semibold rounded-xl hover:bg-white/20 transition-colors"
            >
              Browse Events
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
