# BistroBoard - Restaurant Supplier Management System

A modern, full-stack web application for managing restaurant-supplier relationships and order processing.

## 🚀 Features

- **Role-based Authentication**: Separate interfaces for restaurants and vendors
- **Order Management**: Complete order lifecycle from creation to fulfillment
- **Vendor Marketplace**: Browse and discover suppliers with advanced filtering
- **Real-time Updates**: Live order status tracking and notifications
- **Modern UI**: Responsive design with Tailwind CSS
- **Professional Dashboard**: Intuitive interfaces for both user types

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (easily replaceable with PostgreSQL/MySQL)
- **Pydantic**: Data validation and serialization

### Frontend
- **Next.js 14**: React framework with App Router
- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: Beautiful SVG icons
- **Headless UI**: Unstyled, accessible UI components

## 📦 Installation

### Prerequisites
- Python 3.7+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements_simple.txt
```

3. Initialize the database:
```bash
python create_tables.py
python seed_data.py
```

4. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## 🎯 Usage

1. **Access the application**: Open http://localhost:3000 in your browser
2. **Login with demo accounts**:
   - **Restaurant**: Username: `restaurant1`, Password: `demo123` (Mario's Pizzeria)
   - **Vendor**: Username: `vendor1`, Password: `demo123` (Fresh Valley Produce)

### Restaurant Features
- View order dashboard with statistics
- Create new orders with vendor selection
- Track order status and history
- Browse vendor marketplace
- Manage business profile

### Vendor Features
- View incoming orders dashboard
- Update order status (pending → confirmed → fulfilled)
- Manage business profile and information
- Track order history and statistics

## 🏗 Project Structure

```
bistroboard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Database models
│   │   ├── database.py     # Database configuration
│   │   ├── auth_simple.py  # Authentication logic
│   │   └── routers/        # API route handlers
│   ├── create_tables.py    # Database initialization
│   ├── seed_data.py        # Sample data seeding
│   └── requirements_simple.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   └── lib/          # Utility functions and API client
│   ├── package.json
│   └── tailwind.config.js
├── demo.html              # Standalone HTML demo
├── modern-demo.html       # Enhanced HTML demo
└── README.md
```

## 🔧 API Endpoints

### Authentication
- `POST /token` - User login
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Orders
- `GET /api/orders` - Get user orders
- `POST /api/orders` - Create new order
- `PUT /api/orders/{id}/status` - Update order status
- `PUT /api/orders/{id}/notes` - Update order notes

### Marketplace
- `GET /api/marketplace/vendors` - Get vendor listings
- `GET /api/marketplace/categories` - Get vendor categories
- `GET /api/vendors` - Get vendor list (simplified)

## 🎨 Demo Accounts

The application comes with pre-seeded demo data:

### Restaurant Account
- **Username**: `restaurant1`
- **Password**: `demo123`
- **Business**: Mario's Pizzeria
- **Role**: Restaurant owner

### Vendor Account
- **Username**: `vendor1`
- **Password**: `demo123`
- **Business**: Fresh Valley Produce
- **Role**: Supplier/Vendor

## 🚀 Deployment

### Backend Deployment
1. Set up a production database (PostgreSQL recommended)
2. Update database configuration in `database.py`
3. Set environment variables for production
4. Deploy using services like Heroku, DigitalOcean, or AWS

### Frontend Deployment
1. Build the production version:
```bash
npm run build
```
2. Deploy to Vercel, Netlify, or any static hosting service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by real-world restaurant-supplier workflows
- Designed for scalability and maintainability