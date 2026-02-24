from django.contrib import admin
from .models import Room, Booking, Trip, Profile, Todo, ChatMessage, FutureProject


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'projector', 'speaker', 'price_per_hour')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'room', 'start', 'end', 'created_by', 'status', 'hours_used', 'total_cost')
    list_filter   = ('room', 'status', 'start')
    search_fields = ('title', 'created_by__username')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('destination', 'date', 'created_by')
    list_filter  = ('date',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'color')


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'priority', 'due_date', 'is_done')
    list_filter   = ('priority', 'is_done')
    search_fields = ('title', 'user__username')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ('sender', 'message', 'created_at', 'is_deleted')
    list_filter   = ('is_deleted',)
    search_fields = ('sender__username', 'message')


@admin.register(FutureProject)
class FutureProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'provider', 'status', 'target_date', 'budget', 'created_by')
    list_filter   = ('status',)
    search_fields = ('title', 'provider')
