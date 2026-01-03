from django.urls import path
from . import views

urlpatterns = [
    # Home and Authentication
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Trips
    path('trips/', views.trip_list_view, name='trip_list'),
    path('trips/create/', views.trip_create_view, name='trip_create'),
    path('trips/<int:trip_id>/', views.trip_detail_view, name='trip_detail'),
    path('trips/<int:trip_id>/edit/', views.trip_edit_view, name='trip_edit'),
    path('trips/<int:trip_id>/delete/', views.trip_delete_view, name='trip_delete'),
    
    # Trip Stops
    path('trips/<int:trip_id>/stops/add/', views.stop_create_view, name='stop_create'),
    path('stops/<int:stop_id>/edit/', views.stop_edit_view, name='stop_edit'),
    path('stops/<int:stop_id>/delete/', views.stop_delete_view, name='stop_delete'),
    
    # Activities
    path('stops/<int:stop_id>/activities/add/', views.activity_create_view, name='activity_create'),
    path('activities/<int:activity_id>/edit/', views.activity_edit_view, name='activity_edit'),
    path('activities/<int:activity_id>/delete/', views.activity_delete_view, name='activity_delete'),
    
    # Budget
    path('trips/<int:trip_id>/budget/', views.budget_edit_view, name='budget_edit'),
    
    # Sharing
    path('trips/<int:trip_id>/share/', views.trip_share_view, name='trip_share'),
    path('share/<uuid:public_url>/', views.shared_trip_view, name='shared_trip'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Currency Converter
    path('currency-converter/', views.currency_converter_view, name='currency_converter'),
]
