from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Trip, TripStop, Activity, Budget, SharedTrip, UserProfile
from .forms import SignUpForm, TripForm, TripStopForm, ActivityForm, BudgetForm, UserProfileForm
from .currency_utils import convert_currency, get_currency_symbol, CURRENCIES, get_currency_by_country


# Test view for debugging
def test_view(request):
    """Simple test view to verify templates work"""
    return render(request, 'travel/test.html')


# Authentication Views
def signup_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'travel/signup.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'travel/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# Dashboard and Home
@login_required
@login_required
def dashboard_view(request):
    """User dashboard showing upcoming trips"""
    print(f"=== DASHBOARD VIEW CALLED === User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    try:
        upcoming_trips = Trip.objects.filter(
            user=request.user,
            end_date__gte=timezone.now().date()
        ).order_by('start_date')[:5]
        
        past_trips = Trip.objects.filter(
            user=request.user,
            end_date__lt=timezone.now().date()
        ).order_by('-end_date')[:3]
        
        total_trips = Trip.objects.filter(user=request.user).count()
        
        print(f"Stats: Total={total_trips}, Upcoming={upcoming_trips.count()}, Past={past_trips.count()}")
        
        context = {
            'upcoming_trips': upcoming_trips,
            'past_trips': past_trips,
            'total_trips': total_trips,
        }
        print(f"Rendering dashboard.html with context: {list(context.keys())}")
        return render(request, 'travel/dashboard.html', context)
    except Exception as e:
        print(f"Dashboard Error: {e}")
        import traceback
        traceback.print_exc()
        return render(request, 'travel/dashboard.html', {
            'upcoming_trips': [],
            'past_trips': [],
            'total_trips': 0,
            'error': str(e)
        })


# Trip Management Views
@login_required
def trip_list_view(request):
    """List all user trips"""
    trips = Trip.objects.filter(user=request.user)
    
    # Filter by status
    status = request.GET.get('status', 'all')
    if status == 'upcoming':
        trips = trips.filter(start_date__gte=timezone.now().date())
    elif status == 'past':
        trips = trips.filter(end_date__lt=timezone.now().date())
    elif status == 'ongoing':
        today = timezone.now().date()
        trips = trips.filter(start_date__lte=today, end_date__gte=today)
    
    context = {
        'trips': trips,
        'status': status,
    }
    return render(request, 'travel/trip_list.html', context)


@login_required
def trip_create_view(request):
    """Create a new trip"""
    if request.method == 'POST':
        form = TripForm(request.POST, request.FILES)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            # Create empty budget
            Budget.objects.create(trip=trip)
            messages.success(request, f'Trip "{trip.title}" created successfully!')
            return redirect('trip_detail', trip_id=trip.id)
    else:
        form = TripForm()
    
    return render(request, 'travel/trip_form.html', {'form': form, 'action': 'Create'})


@login_required
def trip_detail_view(request, trip_id):
    """View trip details"""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    stops = trip.stops.all()
    
    # Get or create budget
    budget, created = Budget.objects.get_or_create(trip=trip)
    
    # Calculate activity costs
    total_activity_cost = 0
    for stop in stops:
        stop_cost = stop.activities.aggregate(Sum('cost'))['cost__sum'] or 0
        total_activity_cost += stop_cost
    
    # Update budget activity cost if different
    if budget.activity_cost != total_activity_cost:
        budget.activity_cost = total_activity_cost
        budget.save()
    
    context = {
        'trip': trip,
        'stops': stops,
        'budget': budget,
    }
    return render(request, 'travel/trip_detail.html', context)


@login_required
def trip_edit_view(request, trip_id):
    """Edit existing trip"""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    if request.method == 'POST':
        form = TripForm(request.POST, request.FILES, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, f'Trip "{trip.title}" updated successfully!')
            return redirect('trip_detail', trip_id=trip.id)
    else:
        form = TripForm(instance=trip)
    
    return render(request, 'travel/trip_form.html', {'form': form, 'action': 'Edit', 'trip': trip})


@login_required
def trip_delete_view(request, trip_id):
    """Delete a trip"""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    if request.method == 'POST':
        trip_title = trip.title
        trip.delete()
        messages.success(request, f'Trip "{trip_title}" deleted successfully.')
        return redirect('trip_list')
    
    return render(request, 'travel/trip_confirm_delete.html', {'trip': trip})


# Itinerary Builder - Trip Stops
@login_required
def stop_create_view(request, trip_id):
    """Add a stop to a trip"""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    if request.method == 'POST':
        form = TripStopForm(request.POST)
        if form.is_valid():
            stop = form.save(commit=False)
            stop.trip = trip
            # Set order index
            max_order = trip.stops.aggregate(models.Max('order_index'))['order_index__max'] or 0
            stop.order_index = max_order + 1
            stop.save()
            
            # Suggest currency update based on location if this is the first stop
            if trip.stops.count() == 1:
                suggested_currency = get_currency_by_country(stop.country)
                if suggested_currency != trip.currency:
                    messages.info(request, 
                        f'💡 Tip: You might want to change your trip currency to {suggested_currency} '
                        f'for {stop.country}. You can do this by editing your trip.')
            
            messages.success(request, f'Stop "{stop.city_name}" added to trip!')
            return redirect('trip_detail', trip_id=trip.id)
    else:
        # Pre-fill dates based on trip dates
        initial_data = {
            'start_date': trip.start_date,
            'end_date': trip.end_date,
        }
        form = TripStopForm(initial=initial_data)
    
    return render(request, 'travel/stop_form.html', {'form': form, 'trip': trip, 'action': 'Add'})


@login_required
def stop_edit_view(request, stop_id):
    """Edit a trip stop"""
    stop = get_object_or_404(TripStop, id=stop_id, trip__user=request.user)
    
    if request.method == 'POST':
        form = TripStopForm(request.POST, instance=stop)
        if form.is_valid():
            form.save()
            messages.success(request, f'Stop "{stop.city_name}" updated!')
            return redirect('trip_detail', trip_id=stop.trip.id)
    else:
        form = TripStopForm(instance=stop)
    
    return render(request, 'travel/stop_form.html', {'form': form, 'trip': stop.trip, 'action': 'Edit', 'stop': stop})


@login_required
def stop_delete_view(request, stop_id):
    """Delete a trip stop"""
    stop = get_object_or_404(TripStop, id=stop_id, trip__user=request.user)
    trip = stop.trip
    
    if request.method == 'POST':
        stop.delete()
        messages.success(request, f'Stop "{stop.city_name}" removed from trip.')
        return redirect('trip_detail', trip_id=trip.id)
    
    return render(request, 'travel/stop_confirm_delete.html', {'stop': stop})


# Activities
@login_required
def activity_create_view(request, stop_id):
    """Add activity to a stop"""
    stop = get_object_or_404(TripStop, id=stop_id, trip__user=request.user)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.stop = stop
            activity.save()
            
            # Update budget
            budget = stop.trip.budget
            budget.activity_cost = stop.trip.stops.aggregate(
                total=Sum('activities__cost'))['total'] or 0
            budget.save()
            
            messages.success(request, f'Activity "{activity.name}" added!')
            return redirect('trip_detail', trip_id=stop.trip.id)
    else:
        form = ActivityForm()
    
    return render(request, 'travel/activity_form.html', {'form': form, 'stop': stop, 'action': 'Add'})


@login_required
def activity_edit_view(request, activity_id):
    """Edit an activity"""
    activity = get_object_or_404(Activity, id=activity_id, stop__trip__user=request.user)
    
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            
            # Update budget
            budget = activity.stop.trip.budget
            budget.activity_cost = activity.stop.trip.stops.aggregate(
                total=Sum('activities__cost'))['total'] or 0
            budget.save()
            
            messages.success(request, f'Activity "{activity.name}" updated!')
            return redirect('trip_detail', trip_id=activity.stop.trip.id)
    else:
        form = ActivityForm(instance=activity)
    
    return render(request, 'travel/activity_form.html', {'form': form, 'stop': activity.stop, 'action': 'Edit', 'activity': activity})


@login_required
def activity_delete_view(request, activity_id):
    """Delete an activity"""
    activity = get_object_or_404(Activity, id=activity_id, stop__trip__user=request.user)
    trip = activity.stop.trip
    
    if request.method == 'POST':
        activity.delete()
        
        # Update budget
        budget = trip.budget
        budget.activity_cost = trip.stops.aggregate(
            total=Sum('activities__cost'))['total'] or 0
        budget.save()
        
        messages.success(request, f'Activity "{activity.name}" removed.')
        return redirect('trip_detail', trip_id=trip.id)
    
    return render(request, 'travel/activity_confirm_delete.html', {'activity': activity})


# Budget Management
@login_required
def budget_edit_view(request, trip_id):
    """Edit trip budget with currency conversion"""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    budget, created = Budget.objects.get_or_create(trip=trip)
    
    # Calculate actual activity costs from activities
    actual_activity_cost = trip.stops.aggregate(total=Sum('activities__cost'))['total'] or 0
    
    if request.method == 'POST':
        # Check if currency conversion is requested
        if 'convert_currency' in request.POST:
            try:
                from_currency = request.POST.get('convert_from')
                to_currency = trip.currency
                
                # Convert each cost field
                transport = float(request.POST.get('transport_cost', 0))
                stay = float(request.POST.get('stay_cost', 0))
                meals = float(request.POST.get('meals_cost', 0))
                misc = float(request.POST.get('miscellaneous_cost', 0))
                limit = float(request.POST.get('budget_limit', 0)) if request.POST.get('budget_limit') else None
                
                budget.transport_cost = convert_currency(transport, from_currency, to_currency)
                budget.stay_cost = convert_currency(stay, from_currency, to_currency)
                budget.meals_cost = convert_currency(meals, from_currency, to_currency)
                budget.miscellaneous_cost = convert_currency(misc, from_currency, to_currency)
                if limit:
                    budget.budget_limit = convert_currency(limit, from_currency, to_currency)
                budget.activity_cost = actual_activity_cost
                budget.save()
                
                messages.success(request, f'Budget converted from {from_currency} to {to_currency}!')
                return redirect('budget_edit', trip_id=trip.id)
            except Exception as e:
                messages.error(request, f'Conversion error: {str(e)}')
        else:
            form = BudgetForm(request.POST, instance=budget)
            if form.is_valid():
                budget = form.save(commit=False)
                # Always use actual activity cost
                budget.activity_cost = actual_activity_cost
                budget.save()
                messages.success(request, 'Budget updated successfully!')
                return redirect('trip_detail', trip_id=trip.id)
    else:
        # Pre-fill with actual activity cost
        budget.activity_cost = actual_activity_cost
        budget.save()
        form = BudgetForm(instance=budget)
    
    context = {
        'form': form,
        'trip': trip,
        'budget': budget,
        'actual_activity_cost': actual_activity_cost,
        'currencies': CURRENCIES,
    }
    return render(request, 'travel/budget_form.html', context)


# Sharing
@login_required
def trip_share_view(request, trip_id):
    """Create or get share link for trip"""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    # Make trip public
    trip.is_public = True
    trip.save()
    
    # Get or create share link
    share, created = SharedTrip.objects.get_or_create(trip=trip)
    
    share_url = request.build_absolute_uri(f'/share/{share.public_url}/')
    
    context = {
        'trip': trip,
        'share': share,
        'share_url': share_url,
    }
    return render(request, 'travel/trip_share.html', context)


def shared_trip_view(request, public_url):
    """Public view of shared trip"""
    share = get_object_or_404(SharedTrip, public_url=public_url)
    
    if not share.trip.is_public:
        messages.error(request, 'This trip is no longer publicly accessible.')
        return redirect('login')
    
    # Increment view count
    share.views_count += 1
    share.save()
    
    trip = share.trip
    stops = trip.stops.all()
    budget = trip.budget
    
    context = {
        'trip': trip,
        'stops': stops,
        'budget': budget,
        'is_shared_view': True,
    }
    return render(request, 'travel/shared_trip.html', context)


# User Profile
@login_required
def profile_view(request):
    """User profile view and edit"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'travel/profile.html', context)


# Home page (landing)
def home_view(request):
    """Landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'travel/home.html')


# Currency Converter
@login_required
def currency_converter_view(request):
    """Currency converter tool"""
    result = None
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            from_currency = request.POST.get('from_currency', 'USD')
            to_currency = request.POST.get('to_currency', 'EUR')
            
            converted = convert_currency(amount, from_currency, to_currency)
            result = {
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': converted,
                'from_symbol': get_currency_symbol(from_currency),
                'to_symbol': get_currency_symbol(to_currency),
            }
        except Exception as e:
            messages.error(request, f'Error converting currency: {str(e)}')
    
    context = {
        'currencies': CURRENCIES,
        'result': result,
    }
    return render(request, 'travel/currency_converter.html', context)
