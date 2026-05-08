import api from './api';

export const eventService = {
  // Categories
  getCategories: () => api.get('/events/categories/'),
  getCategory: (slug) => api.get(`/events/categories/${slug}/`),

  // Events
  getEvents: (params = {}) => api.get('/events/', { params }),
  getEvent: (slug) => api.get(`/events/${slug}/`),
  getFeaturedEvents: () => api.get('/events/featured/'),
  getMyEvents: () => api.get('/events/my-events/'),
  searchEvents: (query) => api.get('/events/search/', { params: { q: query } }),
  createEvent: (data) => api.post('/events/', data),
  updateEvent: (slug, data) => api.patch(`/events/${slug}/`, data),

  // Venues
  getVenues: () => api.get('/events/venues/'),
  getVenue: (id) => api.get(`/events/venues/${id}/`),

  // Ticket Tiers
  getTicketTiers: (eventId) => api.get(`/events/${eventId}/tiers/`),
  createTicketTier: (eventId, data) => api.post(`/events/${eventId}/tiers/`, data),
};
