# Training Room Booking (Django)

## Quick Start
```bash
cd trainroom
python -m venv venv
venv\Scripts\activate   # on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata booking/fixtures/initial_rooms.json
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000

- Register a staff account (choosing your color) or login with superuser.
- Create bookings (color-coded by user color).
- Add Trips (e.g., Baguio) — visible on the dashboard and as all-day events on the calendar.
- The dashboard template uses Tailwind and FullCalendar plus a table of today's bookings.
- A copy of your provided HTML design is in `templates/booking/user_dashboard_reference.html`.

## Notes
- Timezone: Asia/Manila (set in settings.py).
- Colors: stored per user (Profile). Booking uses user's color unless overridden.
- Rooms: 5 rooms are preloaded via fixtures.
