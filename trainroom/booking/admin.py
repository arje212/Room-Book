from django.contrib import admin
from .models import Room, Booking, Trip, Profile

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'start', 'end', 'created_by')
    list_filter = ('room', 'start')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('destination', 'date', 'created_by')
    list_filter = ('date',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'color')
