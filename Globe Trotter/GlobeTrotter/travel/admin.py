from django.contrib import admin
from .models import Trip, TripStop, Activity, Budget, SharedTrip, UserProfile


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'end_date', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'start_date')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TripStop)
class TripStopAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'country', 'trip', 'start_date', 'end_date', 'order_index')
    list_filter = ('country', 'start_date')
    search_fields = ('city_name', 'country', 'trip__title')
    ordering = ('trip', 'order_index')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'stop', 'cost', 'duration', 'scheduled_time')
    list_filter = ('category', 'scheduled_time')
    search_fields = ('name', 'stop__city_name', 'notes')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('trip', 'total_cost', 'budget_limit', 'is_over_budget')
    list_filter = ('created_at',)
    search_fields = ('trip__title',)
    readonly_fields = ('total_cost', 'created_at', 'updated_at')


@admin.register(SharedTrip)
class SharedTripAdmin(admin.ModelAdmin):
    list_display = ('trip', 'public_url', 'views_count', 'created_at')
    readonly_fields = ('public_url', 'created_at')
    search_fields = ('trip__title',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
