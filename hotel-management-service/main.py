from fastapi import FastAPI, HTTPException
from app.db import get_connection
from typing import List, Optional
from pydantic import BaseModel


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
#this service is supposed to help store and retrieve details about hotels
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

# Define data models
class HotelBase(BaseModel):
    name: str
    location: str
    amenities: str = ""
    contact_info: Optional[str] = ""
    photos: List[str] = []

    @property
    def amenities_list(self) -> List[str]:
        """Convert CSV amenities string to list of amenities"""
        return [a.strip().lower() for a in self.amenities.split(",")] if self.amenities else []

class Hotel(HotelBase):
    hotel_id: int

@app.post("/hotels", response_model=Hotel)
async def add_hotel(hotel: HotelBase):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO hotels (name, location, amenities, contact_info) VALUES (%s, %s, %s, %s)",
        (hotel.name, hotel.location, hotel.amenities, hotel.contact_info)
    )
    hotel_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return {**hotel.dict(), "hotel_id": hotel_id}

@app.get("/hotels/search")
async def search_hotels(
    name: Optional[str] = None,
    location: Optional[str] = None,
    amenities: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build the query dynamically
        query = "SELECT * FROM hotels WHERE 1=1"
        params = []

        if name:
            query += " AND LOWER(name) LIKE %s"
            params.append(f"%{name}%")

        if location:
            query += " AND LOWER(location) LIKE %s"
            params.append(f"%{location}%")

     
        if amenities:
            requested_amenities = [a.strip().lower() for a in amenities.split(",")]
            for amenity in requested_amenities:
                query += " AND LOWER(amenities) LIKE %s"
                params.append(f"%{amenity}%")

        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while searching hotels: {str(e)}"
        )

@app.put("/hotels/{hotel_id}/photos")
async def upload_hotel_photos(hotel_id: int, photo_urls: List[str]):
    # ... implement photo upload logic ...
    pass

@app.get("/hotels/{hotel_id}")
def get_hotel(hotel_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hotels WHERE hotel_id = %s", (hotel_id,))
    hotel = cursor.fetchone()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {
        "hotel_id": hotel[0],
        "name": hotel[1],
        "location": hotel[2],
        "amenities": hotel[3],
        "contact_info": hotel[4]
    }


@app.delete("/hotels/{hotel_id}")
async def delete_hotel(hotel_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotels WHERE hotel_id = %s", (hotel_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Hotel deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting hotel: {str(e)}"
        )
    

@app.put("/hotels/{hotel_id}")
def update_hotel(hotel_id: int, hotel: HotelBase):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE hotels 
               SET name = %s, location = %s, amenities = %s, contact_info = %s 
               WHERE hotel_id = %s""",
            (hotel.name, hotel.location, hotel.amenities, hotel.contact_info, hotel_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Hotel not found")
        conn.commit()
        cursor.close()
        conn.close()
        return {**hotel.dict(), "hotel_id": hotel_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating hotel: {str(e)}"
        )
    
@app.get("/hotels/{hotel_id}/rooms")
def get_hotel_rooms(hotel_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM rooms WHERE hotel_id = %s",
            (hotel_id,)
        )
        rooms = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rooms:
            raise HTTPException(status_code=404, detail="No rooms found for this hotel")
            
        return rooms
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching rooms: {str(e)}"
        )
