from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Trip, TripStop, Activity, Budget, UserProfile


class SignUpForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class TripForm(forms.ModelForm):
    """Form for creating and editing trips"""
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Trip
        fields = ['title', 'start_date', 'end_date', 'description', 'cover_image', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data


class TripStopForm(forms.ModelForm):
    """Form for adding trip stops"""
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = TripStop
        fields = ['city_name', 'country', 'start_date', 'end_date', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data


class ActivityForm(forms.ModelForm):
    """Form for adding activities"""
    scheduled_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Optional: Schedule a specific time for this activity'
    )
    duration = forms.DurationField(
        help_text='Format: HH:MM:SS or D HH:MM:SS',
        widget=forms.TextInput(attrs={'placeholder': '02:00:00 (2 hours)'})
    )

    class Meta:
        model = Activity
        fields = ['name', 'category', 'cost', 'duration', 'scheduled_time', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class BudgetForm(forms.ModelForm):
    """Form for managing trip budget"""
    class Meta:
        model = Budget
        fields = ['transport_cost', 'stay_cost', 'meals_cost', 'activity_cost', 'miscellaneous_cost', 'budget_limit']
        widgets = {
            'transport_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'stay_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'meals_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'activity_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'miscellaneous_cost': forms.NumberInput(attrs={'step': '0.01'}),
            'budget_limit': forms.NumberInput(attrs={'step': '0.01'}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for user profile"""
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
