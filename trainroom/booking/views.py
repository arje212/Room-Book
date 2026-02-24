from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, date
from calendar import monthrange
from openpyxl import Workbook
from django.contrib.auth.models import User

from .models import Room, Booking, Trip, Holiday, PasswordChangeRequest
from .forms import RegisterForm, BookingForm, TripForm, HolidayForm, PasswordChangeRequestForm

# -------------------- AUTHENTICATION --------------------

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Hindi pa makaka-login
            user.is_approved = False
            user.save()
            messages.success(request, 'Registration submitted. Wait for admin approval.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'booking/register.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def pending_user_registrations_api(request):
    pending_users = User.objects.filter(is_active=False, is_approved=False)
    data = [{"id": u.id, "username": u.username, "date_joined": u.date_joined.strftime("%Y-%m-%d %H:%M:%S")} for u in pending_users]
    pending_users.update(is_approved=True)  # Mark as notified
    return JsonResponse(data, safe=False)

def login_view(request):
    # Get the failed login attempts from session (default to 0)
    failed_attempts = request.session.get("failed_login_attempts", 0)
    show_reset = failed_attempts >= 2  # Show reset link only if failed twice
    username_value = ""

    if request.method == "POST":
        username_value = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username_value, password=password)

        if user:
            login(request, user)
            request.session["failed_login_attempts"] = 0  # reset counter
            return redirect("redirect_after_login")
        else:
            messages.error(request, "Invalid credentials.")
            failed_attempts += 1
            request.session["failed_login_attempts"] = failed_attempts

    return render(request, "booking/login.html", {
        "show_reset": show_reset,
        "username": username_value,
    })



@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def redirect_after_login(request):
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    elif request.user.is_staff:
        return redirect("dashboard")
    else:
        return redirect("login")


# -------------------- DASHBOARD --------------------

@login_required
def dashboard(request):
    # Selected date
    date_str = request.GET.get('date')
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.localdate()
    except ValueError:
        selected_date = timezone.localdate()

    # Rooms and bookings
    rooms = Room.objects.all().order_by('id')
    room_bookings = [
        {
            'room': room,
            'bookings': Booking.objects.filter(room=room, start__date=selected_date).order_by('start')
        }
        for room in rooms
    ]

    # Trips
    trips = Trip.objects.filter(date__gte=selected_date).order_by('date')[:10]

    # Prepare room data with image URLs (kung gusto mo pa ring gumamit elsewhere)
    room_data = []
    for room in rooms:
        room_data.append({
            'id': room.id,
            'name': room.name,
            'capacity': room.capacity,
            'projector': room.projector,
            'speaker': room.speaker,
            'tables': room.tables,
            'chairs': room.chairs,
            'image_url': room.image.url if room.image else '/static/img/placeholder.png',
            'object': room,  # keep the original Room object if needed
        })

    context = {
        'room_bookings': room_bookings,
        'selected_date': selected_date,
        'trips': trips,
        'rooms': rooms,       # ⬅️ ito ang gagamitin ng dashboard.html para sa images
        'room_data': room_data  # ⬅️ optional kung gagamitin mo pa sa JS
    }
    return render(request, 'booking/dashboard.html', context)




# -------------------- BOOKINGS --------------------

@login_required
def booking_create(request):
    room_id = request.GET.get('room_id')
    form = BookingForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        room = booking.room
        start = booking.start
        end = booking.end

        # Check kung may nag-overlap sa date/time
        overlap = Booking.objects.filter(
            room=room,
            start__lt=end,
            end__gt=start
        ).exists()

        if overlap:
            messages.error(request, "This room is already booked for the selected date and time!")
        else:
            booking.created_by = request.user
            booking.save()
            messages.success(request, "Booking created successfully!")
            return redirect('dashboard')

    if room_id:
        try:
            form.fields['room'].initial = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            pass

    rooms = Room.objects.all().order_by('id')
    return render(request, 'booking/booking_form.html', {'form': form, 'rooms': rooms})


@login_required
def booking_list(request):
    bookings = Booking.objects.select_related("room", "created_by").order_by("-start")
    return render(request, "booking/booking_list.html", {"bookings": bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking has been cancelled.")
    return redirect("dashboard")

@login_required
def api_bookings(request):
    events = [
        {
            'id': b.id,
            'title': b.title,
            'start': b.start.isoformat(),
            'end': b.end.isoformat(),
            'backgroundColor': b.display_color(),
            'borderColor': b.display_color(),
            'extendedProps': {
                'room_name': b.room.name,
                'created_by': b.created_by.username,
                'attendees': b.attendees,
                'room_image': b.room.image.url if b.room.image else '/static/img/placeholder.png'
            }
        }
        for b in Booking.objects.all().select_related('created_by', 'room').order_by('-start')
    ]
    return JsonResponse(events, safe=False)


@login_required
def choose_room(request):
    rooms = Room.objects.all().order_by('id')
    form = BookingForm()
    return render(request, 'booking/choose_room.html', {'rooms': rooms, 'form': form})


# -------------------- ADMIN DASHBOARD --------------------

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    bookings = Booking.objects.select_related("room", "created_by")
    staff_accounts = User.objects.filter(is_staff=True).order_by("username")
    password_requests = PasswordChangeRequest.objects.filter(approved=False).order_by("-requested_at")
    rooms = Room.objects.all().order_by("name")
    
    # New pending users
    pending_users = User.objects.filter(is_active=False)

    summary_cards = [
        {"label": "Total Bookings", "count": bookings.count(), "icon": "bi-journal-bookmark", "bg": "primary"},
        {"label": "Pending", "count": bookings.filter(status="Pending").count(), "icon": "bi-hourglass-split", "bg": "warning text-dark"},
        {"label": "Approved", "count": bookings.filter(status="Approved").count(), "icon": "bi-check-circle", "bg": "success"},
        {"label": "Staff Accounts", "count": staff_accounts.count(), "icon": "bi-people", "bg": "secondary"},
        {"label": "Rooms", "count": rooms.count(), "icon": "bi-building", "bg": "info text-dark"},
    ]
    return render(request, "booking/admin_dashboard.html", {
        "bookings": bookings,
        "staff_accounts": staff_accounts,
        "password_requests": password_requests,
        "summary_cards": summary_cards,
        "rooms": rooms,
        "pending_users": pending_users,  # ✅ Add this
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.info(request, f"{user.username} registration rejected.")
    return redirect("admin_dashboard")

# -------------------- PASSWORD MANAGEMENT --------------------

# -------------------- PASSWORD MANAGEMENT --------------------

def reset_password_view(request):
    context = {"username": ""}
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        context["username"] = username  # preserve input

        try:
            user = User.objects.get(username=username)
            # Check if there's already a pending request
            if PasswordChangeRequest.objects.filter(user=user, approved=False).exists():
                messages.warning(request, "You already have a pending password change request.")
            else:
                PasswordChangeRequest.objects.create(user=user, new_password=new_password)
                messages.success(request, "Password change request submitted. Wait for admin approval.")
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "Username not found.")

    return render(request, 'booking/resetpassword.html', context)



@login_required
def request_password_change(request):
    form = PasswordChangeRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Password change request submitted. Wait for admin approval.")
        return redirect("dashboard")
    return render(request, "booking/request_password_change.html", {"form": form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_password_change(request, request_id):
    req = get_object_or_404(PasswordChangeRequest, id=request_id)
    req.user.set_password(req.new_password)
    req.user.save()
    req.approved = True
    req.save()
    messages.success(request, f"Password for {req.user.username} approved and updated.")
    return redirect("admin_dashboard")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_user(request, user_id):
    u = get_object_or_404(User, id=user_id)
    u.is_active = True
    u.save()
    messages.success(request, f"{u.username} is now approved.")
    return redirect("admin_dashboard")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reject_password_change(request, request_id):
    req = get_object_or_404(PasswordChangeRequest, id=request_id)
    req.approved = False
    req.save()
    messages.info(request, f"Password change request for {req.user.username} rejected.")
    return redirect("admin_dashboard")

# notification 
@login_required
@user_passes_test(lambda u: u.is_superuser)
def pending_password_requests_api(request):
    pending_requests = PasswordChangeRequest.objects.filter(approved=False, notified=False)
    data = [{"id": r.id, "user": r.user.username, "requested_at": r.requested_at.strftime("%Y-%m-%d %H:%M:%S")} for r in pending_requests]
    
    # Mark as notified para hindi na lumabas ulit
    pending_requests.update(notified=True)
    
    return JsonResponse(data, safe=False)

def pending_user_registrations_api(request):
    # Example: return users who joined in the last 24 hours or are inactive
    recent_users = User.objects.filter(is_active=False)  # only pending/needs approval
    data = [
        {
            "id": u.id,
            "username": u.username,
            "date_joined": u.date_joined.strftime("%Y-%m-%d %H:%M"),
        }
        for u in recent_users
    ]
    return JsonResponse(data, safe=False)
# -------------------- ROOM MANAGEMENT --------------------

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_rooms(request):
    rooms = Room.objects.all().order_by("name")
    return render(request, "booking/admin_dashboard.html", {"rooms": rooms})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_room(request):
    if request.method == "POST":
        Room.objects.create(
            name=request.POST.get("name"),
            capacity=request.POST.get("capacity") or 0,
            projector=request.POST.get("projector", "No"),
            speaker=request.POST.get("speaker", "No"),
            tables=request.POST.get("tables") or 0,
            chairs=request.POST.get("chairs") or 0,
            description=request.POST.get("description", ""),
            image=request.FILES.get("image")
        )
        messages.success(request, f"{request.POST.get('name')} added successfully.")
        return redirect("manage_rooms")
    return render(request, "booking/add_room.html")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        room.name = request.POST.get("name")
        room.capacity = request.POST.get("capacity") or 0
        room.projector = request.POST.get("projector", "No")
        room.speaker = request.POST.get("speaker", "No")
        room.tables = request.POST.get("tables") or 0
        room.chairs = request.POST.get("chairs") or 0
        room.description = request.POST.get("description", "")
        if request.FILES.get("image"):
            room.image = request.FILES["image"]
        room.save()
        messages.success(request, f"{room.name} updated successfully.")
        return redirect("manage_rooms")
    return render(request, "booking/update_room.html", {"room": room})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    messages.success(request, f"{room.name} deleted successfully.")
    return redirect("manage_rooms")


# -------------------- TRIPS --------------------

@login_required
def trip_create(request):
    form = TripForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        trip = form.save(commit=False)
        trip.created_by = request.user
        trip.save()
        messages.success(request, "Trip created successfully.")
        return redirect("dashboard")
    return render(request, "booking/trip_form.html", {"form": form})


# -------------------- HOLIDAYS --------------------

@login_required
def holiday_create(request):
    form = HolidayForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Holiday added successfully.")
        return redirect("dashboard")
    return render(request, "booking/holiday_form.html", {"form": form})

@login_required
def ph_holidays(request):
    holidays = list(Holiday.objects.values("date", "description"))
    return JsonResponse(holidays, safe=False)


# -------------------- ADMIN EXCEL & STAFF MANAGEMENT --------------------

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_bookings_excel(request):
    bookings = Booking.objects.select_related("room", "created_by").order_by("-start")
    wb = Workbook()
    ws = wb.active
    ws.title = "Bookings"
    ws.append(["ID", "Title", "Room", "Start", "End", "Created By", "Attendees", "Status"])
    for b in bookings:
        ws.append([
            b.id, b.title, b.room.name, b.start.strftime("%Y-%m-%d %H:%M"),
            b.end.strftime("%Y-%m-%d %H:%M"), b.created_by.username, b.attendees, b.status
        ])
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="bookings.xlsx"'
    wb.save(response)
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def booking_history(request):
    bookings = Booking.objects.select_related("room", "created_by").order_by("-start")
    return render(request, "booking/booking_history.html", {"bookings": bookings})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def staff_accounts(request):
    staff_accounts = User.objects.filter(is_staff=True).order_by("username")
    return render(request, "booking/staff_accounts.html", {"staff_accounts": staff_accounts})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_staff(request, user_id):
    staff = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        staff.username = request.POST.get("username")
        staff.email = request.POST.get("email")
        staff.is_active = bool(request.POST.get("is_active"))
        staff.save()
        messages.success(request, f"{staff.username} updated successfully.")
        return redirect("staff_accounts")
    return render(request, "booking/edit_staff.html", {"staff": staff})

# models.py Booking method
def display_color(self):
    return self.created_by.profile.color if hasattr(self.created_by, 'profile') else "#F1F50B"
