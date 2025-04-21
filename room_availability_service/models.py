from pydantic import BaseModel

class BookingRequest(BaseModel):
    hotel_id: int
    room_type: str
    days: int
