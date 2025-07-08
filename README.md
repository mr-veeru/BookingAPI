# Fitness Studio Booking API

A simple Flask-based API for booking fitness classes (Yoga, Zumba, HIIT) at a fictional studio.

## Features
- View available classes
- Book a class
- View bookings by email
- Timezone support (IST and conversion)

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```

## API Endpoints

- `GET /classes` — List all upcoming classes
- `POST /book` — Book a class
- `GET /bookings?email=...` — List bookings by email

## Advanced: Change Base Timezone for All Classes (Admin)

- `POST /admin/change_timezone` — Change the base timezone for all stored class datetimes.
  - Body: `{ "new_timezone": "<timezone string, e.g. UTC or America/New_York>" }`

### Example: Change all class times to UTC
```bash
curl -X POST http://127.0.0.1:5000/admin/change_timezone \
  -H "Content-Type: application/json" \
  -d '{"new_timezone": "UTC"}'
```

## Running Tests

This project includes a suite of unit tests using `pytest` to ensure the API works as expected and handles edge cases.

### To run the tests:

```bash
pytest
```

### Test Coverage Highlights
- Listing available classes
- Booking a class (success, overbooking, missing fields)
- Viewing bookings by email (including when there are no bookings)
- Admin changing the base timezone for all classes
- Handling invalid timezone inputs (for both class listing and admin timezone change)

The tests cover both standard usage and important edge cases to ensure robust API behavior.

## Sample Requests

### 1. List all classes (default IST)
```bash
curl -X GET http://127.0.0.1:5000/classes
```

### 2. List all classes in a different timezone (e.g., UTC)
```bash
curl -X GET "http://127.0.0.1:5000/classes?timezone=UTC"
```

### 3. Book a class
```bash
curl -X POST http://127.0.0.1:5000/book \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "Veerendra",
    "client_email": "veeru@test.com"
  }'
```

### 4. Get bookings by email
```bash
curl -X GET "http://127.0.0.1:5000/bookings?email=veeru@test.com"
``` 