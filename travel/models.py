from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Trip(models.Model):
    """Model for storing trip information"""
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('CAD', 'Canadian Dollar ($)'),
        ('AUD', 'Australian Dollar ($)'),
        ('CHF', 'Swiss Franc (Fr)'),
        ('MXN', 'Mexican Peso ($)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('ZAR', 'South African Rand (R)'),
        ('SGD', 'Singapore Dollar ($)'),
        ('HKD', 'Hong Kong Dollar ($)'),
        ('NZD', 'New Zealand Dollar ($)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('KRW', 'South Korean Won (₩)'),
        ('TRY', 'Turkish Lira (₺)'),
        ('RUB', 'Russian Ruble (₽)'),
        ('AED', 'UAE Dirham (د.إ)'),
        ('THB', 'Thai Baht (฿)'),
        ('PLN', 'Polish Zloty (zł)'),
        ('DKK', 'Danish Krone (kr)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='trip_covers/', blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', help_text='Currency for this trip')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def get_duration_days(self):
        """Calculate trip duration in days"""
        return (self.end_date - self.start_date).days + 1

    def get_total_budget(self):
        """Get total budget for this trip"""
        try:
            return self.budget.total_cost
        except Budget.DoesNotExist:
            return 0


class TripStop(models.Model):
    """Model for cities/stops in a trip"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stops')
    city_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    order_index = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order_index', 'start_date']

    def __str__(self):
        return f"{self.city_name}, {self.country} - {self.trip.title}"

    def get_duration_days(self):
        """Calculate stop duration in days"""
        return (self.end_date - self.start_date).days + 1


class Activity(models.Model):
    """Model for activities in each trip stop"""
    CATEGORY_CHOICES = [
        ('sightseeing', 'Sightseeing'),
        ('food', 'Food & Dining'),
        ('adventure', 'Adventure'),
        ('culture', 'Culture'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment'),
        ('relaxation', 'Relaxation'),
        ('other', 'Other'),
    ]

    stop = models.ForeignKey(TripStop, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.DurationField(help_text="Duration of activity")
    notes = models.TextField(blank=True, null=True)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_time', 'created_at']
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f"{self.name} - {self.stop.city_name}"


class Budget(models.Model):
    """Model for trip budget breakdown"""
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='budget')
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stay_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    meals_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activity_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    miscellaneous_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Budget for {self.trip.title}"

    def calculate_total(self):
        """Calculate and update total cost"""
        self.total_cost = (
            self.transport_cost + 
            self.stay_cost + 
            self.meals_cost + 
            self.activity_cost + 
            self.miscellaneous_cost
        )
        return self.total_cost

    def is_over_budget(self):
        """Check if over budget limit"""
        if self.budget_limit:
            return self.total_cost > self.budget_limit
        return False

    def save(self, *args, **kwargs):
        """Override save to auto-calculate total"""
        self.calculate_total()
        super().save(*args, **kwargs)


class SharedTrip(models.Model):
    """Model for publicly shared trips"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='shares')
    public_url = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Share link for {self.trip.title}"

    def get_share_url(self):
        """Get the full share URL"""
        return f"/share/{self.public_url}/"


class UserProfile(models.Model):
    """Extended user profile"""
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('CAD', 'Canadian Dollar ($)'),
        ('AUD', 'Australian Dollar ($)'),
        ('CHF', 'Swiss Franc (Fr)'),
        ('MXN', 'Mexican Peso ($)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('ZAR', 'South African Rand (R)'),
        ('SGD', 'Singapore Dollar ($)'),
        ('HKD', 'Hong Kong Dollar ($)'),
        ('NZD', 'New Zealand Dollar ($)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('KRW', 'South Korean Won (₩)'),
        ('TRY', 'Turkish Lira (₺)'),
        ('RUB', 'Russian Ruble (₽)'),
        ('AED', 'UAE Dirham (د.إ)'),
        ('THB', 'Thai Baht (฿)'),
        ('PLN', 'Polish Zloty (zł)'),
        ('DKK', 'Danish Krone (kr)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    preferred_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    saved_destinations = models.TextField(blank=True, null=True, help_text="JSON list of saved destinations")
    preferences = models.TextField(blank=True, null=True, help_text="JSON preferences")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.user.username}"
