from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from app.db import get_connection
import os
import requests

app = FastAPI()

# Update CORS middleware with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8003"],  # Allow both hotel service and payment service
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

@app.get("/")
def root():
    return {"message": "Booking Service is up and running!"}

class Booking(BaseModel):
    hotel_id: int
    name: str
    price: float
    people: int
    room_type: str
    check_in_date: date
    check_out_date: date

@app.post("/bookings")
def create_booking(booking: Booking):
    try:
        # 🔎 Validate hotel exists from hotel-management-service
        response = requests.get(f"http://hotel-service:8000/hotels/{booking.hotel_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Hotel not found")

        # ✅ Check room availability from room-availability-service
        availability_response = requests.get(
            f"http://room-availability-service:8001/check-availability",
            params={
                "hotel_id": booking.hotel_id,
                "room_type": booking.room_type,
                "check_in": booking.check_in_date.isoformat(),
                "check_out": booking.check_out_date.isoformat()
            }
        )

        if availability_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to check room availability")
            
        availability_data = availability_response.json()
        if not availability_data.get("available", False):
            raise HTTPException(status_code=409, detail="Requested room is not available for selected dates")

        # 🔐 Insert booking into MySQL
        conn = get_connection()
        cursor = conn.cursor()
        
        # Calculate days from check_in and check_out dates
        days = (booking.check_out_date - booking.check_in_date).days

        cursor.execute(
            """INSERT INTO bookings 
               (hotel_id, name, price, days, people, room_type, check_in_date, check_out_date) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                booking.hotel_id, 
                booking.name, 
                booking.price, 
                days,
                booking.people, 
                booking.room_type,
                booking.check_in_date,
                booking.check_out_date
            )
        )
        booking_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "message": "Booking successful!",
            "booking_id": booking_id,
            "check_in_date": booking.check_in_date,
            "check_out_date": booking.check_out_date,
            "days": days
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM bookings WHERE id = %s",
            (booking_id,)
        )
        booking = cursor.fetchone()
        cursor.close()
        conn.close()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        return booking

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if booking exists
        cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        # Delete the booking
        cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Booking cancelled successfully"}
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings")
def get_all_bookings():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, h.name as hotel_name 
            FROM bookings b 
            JOIN hotels h ON b.hotel_id = h.hotel_id 
            ORDER BY b.check_in_date DESC
        """)
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
