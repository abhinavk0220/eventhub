from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Event, Reservation


class EventHubApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.event = Event.objects.create(
            title="DjangoCon",
            venue="City Hall",
            date=date(2026, 11, 20),
            total_seats=5,
            available_seats=5,
        )

    def reservation_data(self, seats=1):
        return {
            "event": self.event.pk,
            "attendee_name": "Priya Sharma",
            "attendee_email": "priya@example.com",
            "seats_reserved": seats,
        }

    def test_event_list_and_filters(self):
        response = self.client.get("/api/events/?status=upcoming&venue=city")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.event.pk)

    def test_reservation_deducts_seats(self):
        response = self.client.post(
            "/api/reservations/", self.reservation_data(2), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 3)
        self.assertEqual(response.data["status"], "confirmed")

    def test_overbooking_is_rejected(self):
        response = self.client.post(
            "/api/reservations/", self.reservation_data(6), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only 5 seat(s) available.", str(response.data))
        self.assertEqual(Reservation.objects.count(), 0)

    def test_cancel_restores_seats_and_is_idempotency_protected(self):
        reservation = Reservation.objects.create(
            event=self.event,
            attendee_name="Priya Sharma",
            attendee_email="priya@example.com",
            seats_reserved=2,
        )
        self.event.available_seats = 3
        self.event.save(update_fields=["available_seats"])

        response = self.client.post(
            f"/api/reservations/{reservation.pk}/cancel/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)
        self.assertEqual(response.data["status"], "cancelled")

        response = self.client.post(
            f"/api/reservations/{reservation.pk}/cancel/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.event.refresh_from_db()
        self.assertEqual(self.event.available_seats, 5)

    def test_reservation_filter_by_event(self):
        response = self.client.get(
            f"/api/reservations/?event_id={self.event.pk}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
