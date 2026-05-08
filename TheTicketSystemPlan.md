┌─────────────────┐     ┌─────────────────────────┐     ┌─────────────────┐
│   React Frontend │────▶  Django REST API       │────▶  PostgreSQL    │
│  (Vite + Tailwind)│     │  (DRF Generic Views)    │     │   Database      │
└─────────────────┘     └─────────────────────────┘     └─────────────────┘
                               │
                        ┌──────┴──────┐
                        ▼             ▼
                   ┌─────────┐   ┌──────────┐
                   │  Redis  │   │ M-Pesa   │
                   │ (Cache) │   │ Daraja   │
                   └─────────┘   │  API     │
                                 └──────────┘


Implementation Plan
Phase 1: Backend (Django REST Framework)
Models:

User (extended) - phone number for M-Pesa
Category - Sports, Music, Theatre, Conferences, etc.
Event - title, description, venue, datetime, image, organizer
TicketTier - event FK, name, price, quantity, available_count
Booking - user FK, status, total_amount, mpesa_receipt
Ticket - booking FK, tier FK, QR code, status
Payment - booking FK, amount, mpesa_checkout_id, status
DRF Concrete Generic Views:

ListCreateAPIView for events listing
RetrieveUpdateDestroyAPIView for event details
ListCreateAPIView for bookings
CreateAPIView for M-Pesa STK push initiation
GenericAPIView for M-Pesa callback handling
Phase 2: M-Pesa Integration
Daraja API integration (STK Push)
Callback URL handling for payment confirmation
Payment status polling fallback
Phase 3: Frontend (React + Tailwind)
Pages:

Home (hero + featured events + categories)
Events listing with filters
Event detail (ticket tier selection)
Checkout flow
My Tickets (with QR codes)
User profile
Key UI Components:

Event cards with Kenyan shilling pricing (KES)
Seat/tier selection interface
M-Pesa payment modal (phone input + STK push simulation)
QR code ticket display
Phase 4: Admin Features
Organizer dashboard
Event creation/editing
Ticket sales analytics
Check-in app (scan QR codes)