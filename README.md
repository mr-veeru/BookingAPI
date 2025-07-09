# Booking API

A simple Flask-based API for booking fitness classes (Yoga, Zumba, HIIT) at a fictional studio.

---

## Table of Contents
1. [Features](#features)
2. [Setup Instructions](#setup-instructions)
3. [Project Structure](#project-structure)
4. [API Endpoints](#api-endpoints)
5. [API Endpoint Details](#api-endpoint-details)
6. [Sample Requests](#sample-requests)
7. [Running Tests](#running-tests)

---

## Features
- View available classes
- Book a class
- View all bookings
- Timezone support (IST and conversion)

---

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```

---

## Project Structure

```
BookingAPI/
│
├── app.py                # Main Flask app, creates app and registers blueprints
├── db.py                 # Database connection and schema/seed logic
├── models.py             # Data models and validation
├── requirements.txt      # Dependencies
├── README.md             # Documentation
├── routes/               # Modular route blueprints
│   ├── classes.py        # Endpoints for class listings
│   ├── bookings.py       # Endpoints for bookings
│   └── timezone.py       # Endpoints for changing the timezone
└── tests/
    └── test_api.py       # All tests
```

- **Modular Routing:** All API endpoints are organized into separate modules using Flask, located in the `routes/` package for clarity and scalability.

---

## API Endpoints

- `GET /classes` — List all upcoming classes
- `POST /book` — Book a class
- `GET /bookings` — List all bookings in the system 
- `POST /change_timezone` - Changes the time zone of all classes

---

## API Endpoint Details

### GET `/classes`
**Description:** List all upcoming classes. Times are always returned in the current base timezone (IST by default, or as set by /change_timezone).

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Yoga",
    "datetime": "2024-06-01 10:00:00",
    "instructor": "Alice",
    "available_slots": 5
  }
]
```

---

### POST `/book`
**Description:** Book a class.

**Request Body:**
```json
{
  "class_id": 1,
  "client_name": "Veerendra",
  "client_email": "veeru@test.com"
}
```

**Success Response:**
- Status: `201 Created`
```json
{
  "message": "Booking successful"
}
```

**Error Responses:**
- Missing JSON body:
  - Status: `400 Bad Request`
  - `{ "error": "Missing JSON body" }`
- Validation errors (missing fields, invalid email, etc.):
  - Status: `400 Bad Request`
  - `{ "error": ["class_id is required", ...] }`
- Class not found:
  - Status: `404 Not Found`
  - `{ "error": "Class not found" }`
- No slots available:
  - Status: `409 Conflict`
  - `{ "error": "No slots available" }`

---

### GET `/bookings`
**Description:** List all bookings, or filter by email.

**Query Parameters:**
- `email` (optional, string): Filter bookings by client email.

**Response Example:**
```json
[
  {
    "booking_id": 1,
    "class_id": 1,
    "class_name": "Yoga",
    "client_name": "Veerendra",
    "client_email": "veeru@test.com",
    "booked_at": "2024-06-01 10:00 AM"
  }
]
```

---

### POST `/change_timezone`
**Description:** Change the base timezone for all classes.

**Request Body:**
```json
{
  "new_timezone": "UTC"
}
```

**Success Response:**
- Status: `200 OK`
```json
{
  "message": "All class times updated to new base timezone: UTC"
}
```

**Error Responses:**
- Missing field:
  - Status: `400 Bad Request`
  - `{ "error": "Missing new_timezone in request body" }`
- Invalid timezone:
  - Status: `400 Bad Request`
  - `{ "error": "Invalid timezone" }`

---

## Sample Requests

### 1. List all classes (default IST)
```bash
curl -X GET http://127.0.0.1:5000/classes
```

### 2. Book a class
```bash
curl -X POST http://127.0.0.1:5000/book \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "Veerendra",
    "client_email": "veeru@test.com"
  }'
```

### 3. Get all bookings
```bash
curl -X GET http://127.0.0.1:5000/bookings
```

### 4. Change Base Timezone
```bash
curl -X POST "http://127.0.0.1:5000/change_timezone" \
  -H "Content-Type: application/json" \
  -d '{
    "new_timezone": "UTC"
  }'
```

---

## Running Tests

This project includes a suite of unit tests using `pytest` to ensure the API works as expected and handles edge cases.

### To run the tests:

```bash
python -m pytest
```

### Test Coverage Highlights
- **Classes Endpoints:** Basic listing, timezone change reflected 
- **Booking Endpoints:** Success, overbooking, + parameterized validation 
- **Bookings Endpoints:** All bookings, empty state 
- **Timezone Endpoints:** Timezone change success and validation

The tests cover both standard usage and important edge cases to ensure robust API behavior.

