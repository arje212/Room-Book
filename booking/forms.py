from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Trip, Holiday, Profile
from .models import PasswordChangeRequest

COLOR_CHOICES = [
    ("#F1F50B", 'Yellow'),
    ('#3B82F6', 'Blue'),
    ('#10B981', 'Green'),
    ('#EF4444', 'Red'),
    ('#8B5CF6', 'Violet'),
    ('#6366F1', 'Indigo'),
    ('#F472B6', 'Pink'),
    ('#6B7280', 'Gray'),
    ('#374151', 'Dark Gray'),
    ('#D97706', 'Amber'),
    ('#14B8A6', 'Teal'),
    ('#0EA5E9', 'Sky'),
    ('#A3E635', 'Lime'),
    ('#84CC16', 'Light Green'),
    ('#22C55E', 'Emerald'),
    ('#EAB308', 'Gold'),
    ('#C026D3', 'Purple'),
    ('#F43F5E', 'Rose'),
    ('#BE123C', 'Dark Red'),
    ('#1E3A8A', 'Dark Blue'),
    ('#ffffff', 'White'),
]

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    color = forms.ChoiceField(choices=COLOR_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'color')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = True  # lahat ng bagong users = staff
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.color = self.cleaned_data['color']
            profile.save()
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('room', 'title', 'attendees', 'start', 'end')  # tanggalin 'status'
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ('destination', 'date', 'notes')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['date', 'name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('room', 'title', 'attendees', 'start', 'end', 'status')  # ✅ include status
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),  # optional styling
        }

# forms.py
class PasswordChangeRequestForm(forms.ModelForm):
    class Meta:
        model = PasswordChangeRequest
        fields = ['new_password']
        widgets = {
            'new_password': forms.PasswordInput(attrs={'class': 'input input-bordered w-full'}),
        }