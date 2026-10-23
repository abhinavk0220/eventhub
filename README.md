## EventHub

EventHub is a Django REST Framework API for browsing events, reserving seats,
and cancelling reservations.

### Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Apply migrations:

   ```powershell
   python manage.py migrate
   ```

4. Start the development server:

   ```powershell
   python manage.py runserver
   ```

The API is available at `http://127.0.0.1:8000/api/`.

### Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/events/` | List all events |
| POST | `/api/events/` | Create an event |
| GET/PATCH/PUT/DELETE | `/api/events/<id>/` | Read or manage one event |
| GET | `/api/events/?status=upcoming` | Filter events by status |
| GET | `/api/events/?venue=bangalore` | Filter events by venue |
| GET | `/api/reservations/` | List reservations |
| POST | `/api/reservations/` | Reserve seats |
| GET/PATCH/PUT/DELETE | `/api/reservations/<id>/` | Read or manage one reservation |
| GET | `/api/reservations/?event_id=1` | Filter reservations by event |
| POST | `/api/reservations/<id>/cancel/` | Cancel a reservation and restore seats |

### Example requests

Create an event:

```json
{
  "title": "PyCon India 2025",
  "venue": "NIMHANS Convention Centre, Bangalore",
  "date": "2025-09-20",
  "total_seats": 500,
  "available_seats": 500,
  "status": "upcoming"
}
```

Reserve seats:

```json
{
  "event": 1,
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

### Design decision

Reservation creation and cancellation use `transaction.atomic()` and lock the
event row with `select_for_update()`. The seat count is checked again while
locked before the reservation is created. This keeps the event and reservation
updates consistent when requests arrive concurrently.

### Screenshots

Place the required Postman screenshots in
[`screenshots/`](screenshots/):

- `successful-reservation.png`
- `overbooking-failure.png`
- `successful-cancellation.png`

### Tests

Run the test suite with:

```powershell
python manage.py test
```