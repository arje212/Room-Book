from django.contrib import admin
from django.urls import path
from booking import views

urlpatterns = [
    # Django admin panel
    path("admin/", admin.site.urls),

    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("redirect/", views.redirect_after_login, name="redirect_after_login"),
    path("api/pending-user-registrations/", views.pending_user_registrations_api, name="pending_user_registrations_api"),

    # Custom password reset & approval flow
    path("custom-reset-password/", views.reset_password_view, name="custom_reset_password"),
    path("staff/request-password-change/", views.request_password_change, name="request_password_change"),
    path("dashboard-admin/approve-password/<int:request_id>/", views.approve_password_change, name="approve_password_change"),
    path("dashboard-admin/reject-password/<int:request_id>/", views.reject_password_change, name="reject_password_change"),
    path("api/pending-password-requests/", views.pending_password_requests_api, name="pending_password_requests_api"),
    path("dashboard-admin/approve-user/<int:user_id>/", views.approve_user, name="approve_user"),
    path('api/pending_user_registrations/', views.pending_user_registrations_api, name='pending_user_registrations_api'),
   
    path("dashboard-admin/approve-user/<int:user_id>/", views.approve_user, name="approve_user"),
    path("dashboard-admin/reject-user/<int:user_id>/", views.reject_user, name="reject_user"),  # <-- add this

    # Bookings
    path("bookings/new/", views.booking_create, name="booking_create"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
    path("rooms/choose/", views.choose_room, name="choose_room"),

    # Trips
    path("trips/new/", views.trip_create, name="trip_create"),

    # Holidays
    path("holidays/new/", views.holiday_create, name="holiday_create"),
    path("api/ph_holidays/", views.ph_holidays, name="api_ph_holidays"),

    # API
    path("api/bookings/", views.api_bookings, name="api_bookings"),

    # Admin views
    path("dashboard-admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard-admin/export-bookings/", views.export_bookings_excel, name="export_bookings"),
    path("dashboard-admin/bookings/", views.booking_history, name="booking_history"),
    path("dashboard-admin/staff/", views.staff_accounts, name="staff_accounts"),
    path("dashboard-admin/staff/edit/<int:user_id>/", views.edit_staff, name="edit_staff"),

    # 🔹 Bagong URL para sa room update
    # Admin views for rooms
    path("dashboard-admin/rooms/", views.manage_rooms, name="manage_rooms"),
    path("dashboard-admin/rooms/delete/<int:room_id>/", views.delete_room, name="delete_room"),
    path("dashboard-admin/rooms/update/<int:room_id>/", views.update_room, name="update_room"),
]
