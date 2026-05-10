# brightpassticket - Kenyan Event Ticketing Platform

A full-stack ticket booking system for events, sports, concerts, and more in Kenya. Built with Django REST Framework and React, featuring M-Pesa payment integration.

## Features

### Backend (Django REST Framework)
- **User Management**: Custom user model with phone number support for M-Pesa
- **Events System**: Categories, venues, events, and ticket tiers
- **Booking System**: Booking creation with automatic ticket generation
- **Payment Integration**: Full M-Pesa Daraja API integration with STK Push
- **QR Code Tickets**: Generated QR codes for ticket validation
- **Admin Dashboard**: Complete Django admin interface

### Frontend (React + Tailwind CSS)
- **Modern UI**: Responsive design with Tailwind CSS
- **Event Discovery**: Search, filter, and browse events
- **User Authentication**: JWT-based auth with login/register
- **Booking Flow**: Step-by-step checkout with M-Pesa payment
- **My Tickets**: View and manage purchased tickets with QR codes
- **Mobile-First**: Optimized for mobile devices

## Tech Stack

### Backend
- Django 6.0+
- Django REST Framework
- Django CORS Headers
- Simple JWT for authentication
- PostgreSQL/SQLite database
- M-Pesa Daraja API integration
- QR Code generation

### Frontend
- React 19
- Vite
- Tailwind CSS
- React Router DOM
- Axios
- Lucide React icons

## Project Structure

```
ticketsystem/
├── backend/
│   ├── accounts/          # User authentication and profiles
│   ├── events/            # Events, categories, venues
│   ├── bookings/          # Bookings and tickets
│   ├── payments/          # M-Pesa integration
│   ├── ticketsystem/      # Django settings
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React contexts
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- M-Pesa Daraja API credentials (for payments)

### Backend Setup

1. **Create virtual environment and install dependencies:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. **Create .env file:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Run migrations and create superuser:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

4. **Start the development server:**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Create .env file:**
```bash
cp .env.example .env.local
```

3. **Start the development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### M-Pesa Configuration

1. **Get Daraja API credentials from Safaricom:**
   - Register at https://developer.safaricom.co.ke
   - Create a new app to get Consumer Key and Consumer Secret
   - Get Passkey from your M-Pesa account

2. **Configure callback URL:**
   - For local development, use ngrok to expose your local server
   - Install ngrok: https://ngrok.com
   - Run: `ngrok http 8000`
   - Update `MPESA_CALLBACK_URL` in your .env file with the ngrok URL

3. **Update environment variables:**
```env
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_PASSKEY=your-passkey
MPESA_SHORTCODE=174379  # Test shortcode for sandbox
MPESA_ENVIRONMENT=sandbox
MPESA_CALLBACK_URL=https://your-ngrok-url.ngrok.io/api/payments/mpesa/callback/
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (returns JWT)
- `POST /api/auth/refresh/` - Refresh token
- `GET/PUT /api/auth/profile/` - User profile

### Events
- `GET /api/events/` - List events
- `GET /api/events/<slug>/` - Event details
- `GET /api/events/featured/` - Featured events
- `GET /api/events/categories/` - List categories
- `GET /api/events/venues/` - List venues

### Bookings
- `GET/POST /api/bookings/` - List/create bookings
- `GET /api/bookings/<booking_number>/` - Booking details
- `GET /api/bookings/tickets/my-tickets/` - My tickets

### Payments (M-Pesa)
- `POST /api/payments/mpesa/initiate/` - Initiate STK Push
- `POST /api/payments/mpesa/callback/` - M-Pesa callback (webhook)
- `GET /api/payments/<id>/status/` - Check payment status

## Key Features Explained

### M-Pesa Payment Flow
1. User selects tickets and proceeds to checkout
2. System creates a booking with "pending" status
3. User enters M-Pesa phone number and clicks "Pay"
4. Backend initiates STK Push to user's phone
5. User receives push notification and enters PIN
6. M-Pesa sends callback to our server with result
7. If successful, booking is confirmed and tickets are generated
8. User sees QR code tickets in "My Tickets"

### DRF Concrete Generic Views Used
- `ListCreateAPIView` - For listing and creating resources
- `RetrieveUpdateDestroyAPIView` - For CRUD operations
- `RetrieveAPIView` - For retrieving single resources
- `ListAPIView` - For listing resources
- `CreateAPIView` - For creating resources

### Ticket Generation
- Each booking creates individual tickets
- QR codes are generated with unique ticket data
- Tickets can be validated at venue entry
- QR codes contain encrypted ticket information

## Testing

### Creating Test Data
```bash
# Access Django shell
python manage.py shell

# Create categories
from events.models import Category
Category.objects.create(name="Music", slug="music", color="#ec4899")
Category.objects.create(name="Sports", slug="sports", color="#3b82f6")

# Create venue
from events.models import Venue
Venue.objects.create(name="KICC", city="Nairobi", address="Kenyatta International Convention Centre")
```

### Testing M-Pesa (Sandbox)
1. Use test shortcode: `174379`
2. Use test phone numbers from Safaricom documentation
3. Use test PIN: Any 4 digits
4. Check M-Pesa sandbox dashboard for transactions

## Production Deployment

### Backend
- Use PostgreSQL database
- Set `DEBUG=False`
- Configure proper allowed hosts
- Set up proper M-Pesa production credentials
- Use environment variables for secrets
- Configure WhiteNoise for static files

### Frontend
- Run `npm run build` to create production build
- Serve static files from `dist/` folder
- Configure API URL for production

## License

MIT License - Feel free to use for your projects!

## Support

For issues or questions:
- Create an issue in the repository
- Contact: support@brightpassticket.co.ke

---

Built with  for Kenya
