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

## Postman test sequence

Keep the server running at `http://127.0.0.1:8000`. Use
`Content-Type: application/json` for POST requests. Run these requests in
order; the IDs in later requests come from earlier responses.

### 1. Create an event

```text
POST http://127.0.0.1:8000/api/events/
```

Request body:

```json
{
  "title": "DjangoCon India",
  "venue": "NIMHANS Convention Centre, Bangalore",
  "date": "2027-09-20",
  "total_seats": 5,
  "available_seats": 5,
  "status": "upcoming"
}
```

Save the returned event `id` as `EVENT_ID`.

### 2. List events

```text
GET http://127.0.0.1:8000/api/events/
```

Optional filters:

```text
GET http://127.0.0.1:8000/api/events/?status=upcoming
GET http://127.0.0.1:8000/api/events/?venue=bangalore
```

### 3. Create a successful reservation

```text
POST http://127.0.0.1:8000/api/reservations/
```

Request body:

```json
{
  "event": "EVENT_ID",
  "attendee_name": "Priya Sharma",
  "attendee_email": "priya@example.com",
  "seats_reserved": 2
}
```

Replace `"EVENT_ID"` with the numeric ID from step 1. The response should be
`201 Created`, and the event should now have 3 available seats. Save the
returned reservation `id` as `RESERVATION_ID`.

Screenshot filename: `01-successful-reservation-201.png`

### 4. Test overbooking

```text
POST http://127.0.0.1:8000/api/reservations/
```

Request body:

```json
{
  "event": "EVENT_ID",
  "attendee_name": "Arjun Mehta",
  "attendee_email": "arjun@example.com",
  "seats_reserved": 4
}
```

At this point only 3 seats are available. The response should be
`400 Bad Request` with an availability error.

Screenshot filename: `02-overbooking-failure-400.png`

### 5. List reservations for an event

```text
GET http://127.0.0.1:8000/api/reservations/?event_id=EVENT_ID
```

Replace `EVENT_ID` with the numeric event ID.

### 6. Cancel the reservation

```text
POST http://127.0.0.1:8000/api/reservations/RESERVATION_ID/cancel/
```

No request body is needed. Replace `RESERVATION_ID` with the numeric
reservation ID from step 3. The response should be `200 OK`, show
`"status": "cancelled"`, and restore the 2 seats to the event.

Screenshot filename: `03-successful-cancellation-200.png`

### Endpoint reference

| Method | URL | Purpose |
| --- | --- | --- |
| POST | `http://127.0.0.1:8000/api/events/` | Create an event |
| GET | `http://127.0.0.1:8000/api/events/` | List events |
| GET | `http://127.0.0.1:8000/api/events/?status=upcoming` | Filter by status |
| GET | `http://127.0.0.1:8000/api/events/?venue=bangalore` | Filter by venue |
| POST | `http://127.0.0.1:8000/api/reservations/` | Reserve seats |
| GET | `http://127.0.0.1:8000/api/reservations/?event_id=EVENT_ID` | Filter by event |
| POST | `http://127.0.0.1:8000/api/reservations/RESERVATION_ID/cancel/` | Cancel and restore seats |

### Design decision

Reservation creation and cancellation use `transaction.atomic()` and lock the
event row with `select_for_update()`. The seat count is checked again while
locked before the reservation is created. This keeps the event and reservation
updates consistent when requests arrive concurrently.

## Submission screenshots

Place the three Postman screenshots in [`screenshots/`](screenshots/):

| Screenshot | Capture |
| --- | --- |
| `01-successful-reservation-201.png` | Step 3 response showing `201 Created` |
| `02-overbooking-failure-400.png` | Step 4 response showing `400 Bad Request` |
| `03-successful-cancellation-200.png` | Step 6 response showing cancelled status |

### Tests

Run the test suite with:

```powershell
python manage.py test
```