import api from './api';

export const bookingService = {
  // Bookings
  getBookings: () => api.get('/bookings/'),
  getBooking: (bookingNumber) => api.get(`/bookings/${bookingNumber}/`),
  createBooking: (data) => api.post('/bookings/', data),

  // Tickets
  getMyTickets: () => api.get('/bookings/tickets/my-tickets/'),
  getTicket: (ticketNumber) => api.get(`/bookings/tickets/${ticketNumber}/`),
  getTicketDetail: (ticketNumber) => api.get(`/bookings/tickets/${ticketNumber}/`), // Alias for clarity
  
  // Download ticket PDF
  downloadTicket: (ticketNumber) => api.get(
    `/bookings/tickets/${ticketNumber}/download/`,
    {
      responseType: 'blob',
    }
  ),
};
