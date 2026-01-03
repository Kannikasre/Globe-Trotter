# GlobeTrotter - Travel Planning Web Application

A comprehensive web application for planning multi-city trips with budget tracking, itinerary management, and trip sharing capabilities.

## 🚀 Features

- **User Authentication**: Secure signup/login system
- **Trip Management**: Create, edit, and delete trips with dates and details
- **Multi-City Itineraries**: Add multiple stops with cities, dates, and activities
- **Activity Planning**: Organize activities by category with costs and durations
- **Budget Tracking**: Automatic budget calculation with category breakdowns
- **Trip Sharing**: Share trips publicly via unique URLs
- **Responsive Design**: Works on desktop and mobile devices
- **Admin Panel**: Full Django admin for managing all data

## 📋 Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (easily switchable to PostgreSQL/MySQL)
- **Frontend**: HTML, CSS (responsive design)
- **Authentication**: Django's built-in auth system

## 🗄 Database Models

- **User**: Django's built-in User model
- **Trip**: Main trip information
- **TripStop**: Cities/destinations within a trip
- **Activity**: Things to do at each stop
- **Budget**: Budget breakdown by category
- **SharedTrip**: Public sharing links
- **UserProfile**: Extended user information

## 🛠 Setup Instructions

### 1. Navigate to project directory

```bash
cd "c:\Users\Admin\Desktop\Globe Trotter\GlobeTrotter"
```

### 2. Install dependencies (if needed)

```bash
pip install django pillow
```

### 3. Database is already migrated

The migrations have been created and applied.

### 4. Create a superuser for admin access

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 5. Run the development server

```bash
python manage.py runserver
```

### 6. Access the application

- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📱 Key URLs

- `/` - Home/Landing page
- `/signup/` - User registration
- `/login/` - User login
- `/dashboard/` - User dashboard
- `/trips/` - List all trips
- `/trips/create/` - Create new trip
- `/trips/<id>/` - View trip details
- `/share/<uuid>/` - Public shared trip view
- `/profile/` - User profile
- `/admin/` - Django admin panel

## 🎯 Usage Guide

### Creating Your First Trip

1. **Sign up** for a new account or **login**
2. Click **"Plan New Trip"** from dashboard
3. Fill in trip details (title, dates, description, cover image)
4. Click **"Create Trip"**

### Adding Stops and Activities

1. From trip detail page, click **"+ Add Stop"**
2. Enter city name, country, and dates
3. After adding a stop, click **"+ Activity"**
4. Add activity details (name, category, cost, duration)

### Managing Budget

1. Click **"Manage Budget"** on trip detail page
2. Enter costs for:
   - Transport
   - Stay/Accommodation
   - Meals
   - Miscellaneous
3. Activity costs are calculated automatically
4. Set a budget limit to track overspending

### Sharing Your Trip

1. Click **"Share Trip"** on trip detail page
2. Trip becomes public automatically
3. Copy the share link
4. Share with friends or on social media

## 🔐 Admin Features

Access the admin panel at `/admin/` to:

- Manage all users, trips, stops, and activities
- View detailed statistics
- Moderate shared content
- Export data

## 📊 Project Structure

```
GlobeTrotter/
├── manage.py
├── db.sqlite3
├── GlobeTrotter/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── travel/
    ├── models.py          # Database models
    ├── views.py           # View functions
    ├── forms.py           # Form definitions
    ├── urls.py            # URL patterns
    ├── admin.py           # Admin configuration
    ├── templates/
    │   └── travel/        # HTML templates
    └── migrations/        # Database migrations
```

## 🎨 Customization

The application uses inline CSS for simplicity. To customize:

1. **Colors**: Search for color codes (e.g., `#667eea`) in `base.html`
2. **Layout**: Modify grid classes and card styles
3. **Features**: Extend models and views as needed

## 📝 Future Enhancements

- Map integration for visualizing routes
- AI-powered activity recommendations
- Collaboration features (multi-user trips)
- Mobile apps (iOS/Android)
- Export to PDF/calendar
- Weather forecasts
- Currency conversion
- Photo galleries

## 🐛 Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic
```

### Database issues
```bash
python manage.py makemigrations
python manage.py migrate
```

---

**Happy Traveling! 🌎✈️**
