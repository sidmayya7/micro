from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from typing import List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Replace with your DB credentials or import from a config
def get_connection():
    return mysql.connector.connect(
        host="mysql-hotel",  # name of the MySQL service in Docker
        user="root",
        password="root",
        database="hotel_db"
    )

@app.get("/check-availability")
def check_availability(
    hotel_id: int = Query(...),
    room_type: str = Query(...),
    check_in: str = Query(...),
    check_out: str = Query(...),
):
    try:
        check_in_date = datetime.strptime(check_in.strip(), "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out.strip(), "%Y-%m-%d")
    except ValueError as e:
        return {"available": False, "message": f"Invalid date format: {e}"}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Count overlapping bookings
        query = """
            SELECT COUNT(*) FROM bookings
            WHERE hotel_id = %s
            AND room_type = %s
            AND NOT (%s <= check_in_date OR %s >= check_out_date)
        """
        cursor.execute(query, (hotel_id, room_type, check_out_date, check_in_date))
        (overlapping_bookings,) = cursor.fetchone()

        # Get availability from rooms table
        cursor.execute(
            "SELECT availability FROM rooms WHERE hotel_id = %s AND room_type = %s",
            (hotel_id, room_type),
        )
        room_result = cursor.fetchone()

        if room_result is None:
            return {"available": False, "message": "Room type not found for hotel"}

        available_rooms = room_result[0]
        available = overlapping_bookings < available_rooms

        return {"available": available}

    except Error as err:
        return {"available": False, "message": f"Database error: {err}"}

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/room-availability/{hotel_id}/{room_type}")
def get_room_availability_range(hotel_id: int, room_type: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Calculate date range
        today = datetime.now().date()
        thirty_days = today + timedelta(days=30)

        # Get room details first
        cursor.execute(
            "SELECT availability FROM rooms WHERE hotel_id = %s AND room_type = %s",
            (hotel_id, room_type)
        )
        room_result = cursor.fetchone()
        if not room_result:
            return {"error": "Room type not found"}

        total_rooms = room_result['availability']

        # Get all bookings for next 30 days
        query = """
            SELECT check_in_date, check_out_date, COUNT(*) as booked_rooms
            FROM bookings 
            WHERE hotel_id = %s 
            AND room_type = %s 
            AND check_in_date <= %s 
            AND check_out_date >= %s
            GROUP BY check_in_date, check_out_date
        """
        cursor.execute(query, (hotel_id, room_type, thirty_days, today))
        bookings = cursor.fetchall()

        # Create availability map for each day
        availability_map = {}
        booked_dates = []
        current_date = today
        
        while current_date <= thirty_days:
            rooms_booked = 0
            for booking in bookings:
                if booking['check_in_date'] <= current_date and booking['check_out_date'] >= current_date:
                    rooms_booked += booking['booked_rooms']
            
            date_str = current_date.isoformat()
            rooms_available = total_rooms - rooms_booked
            
            availability_map[date_str] = {
                "date": date_str,
                "available": rooms_available,
                "total_rooms": total_rooms,
                "booked_rooms": rooms_booked
            }
            
            if rooms_booked > 0:
                booked_dates.append({
                    "date": date_str,
                    "booked_rooms": rooms_booked,
                    "remaining_rooms": rooms_available
                })
            
            current_date += timedelta(days=1)

        cursor.close()
        conn.close()

        return {
            "room_type": room_type,
            "total_rooms": total_rooms,
            "availability": availability_map,
            "booked_dates": booked_dates
        }

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}