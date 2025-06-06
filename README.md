# Fitness Studio Booking API

This is a basic API built with FastAPI and SQLite for booking fitness classes like Yoga, Zumba, and HIIT.

## Features

- Get a list of available classes
- Book a class for a user
- Get all bookings made by an email


## Setup Instructions

### Requirements

- Python 3.9+
- `pip` for installing packages

### Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic pytz pytest


API Endpoints
GET /classes
Get all available classes.

Request:
curl http://127.0.0.1:8000/classes


Response:
[{"id":1,"name":"Yoga","datetime":"2025-06-10T07:00:00","instructor":"Aarti","available_slots":5},{"id":2,"name":"Zumba","datetime":"2025-06-10T08:00:00","instructor":"Rohit","available_slots":10},{"id":3,"name":"HIIT","datetime":"2025-06-10T09:00:00","instructor":"Meera","available_slots":8}]

POST /book

Request:
curl -X POST http://127.0.0.1:8000/book \
-H "Content-Type: application/json" \
-d '{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}'


Response:
{
  "id": 1,
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}


GET /bookings?email=<email>

Request:
curl "http://127.0.0.1:8000/bookings?email=john@example.com"

Response:
[
  {
    "id": 1,
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
  }
]


Notes:
Email format is validated using regex

Empty client names are not allowed

You can't book a class that has 0 available slots
