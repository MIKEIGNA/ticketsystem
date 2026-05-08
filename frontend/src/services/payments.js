import api from './api';

export const paymentService = {
  // Payments
  getPayments: () => api.get('/payments/'),
  getPayment: (id) => api.get(`/payments/${id}/`),
  getPaymentStatus: (id) => api.get(`/payments/${id}/status/`),

  // M-Pesa
  initiateMpesa: (data) => api.post('/payments/mpesa/initiate/', data),
  queryMpesaStatus: (paymentId) => api.post(`/payments/mpesa/query/${paymentId}/`),
};
