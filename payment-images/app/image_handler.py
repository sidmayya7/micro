from motor.motor_asyncio import AsyncIOMotorClient
from bson.binary import Binary
from bson.objectid import ObjectId
import magic
import os

async def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/hotel_images")
    client = AsyncIOMotorClient(mongo_uri)
    return client.hotel_images

async def save_image(hotel_id: int, image_data: bytes, filename: str):
    db = await get_db()
    mime_type = magic.from_buffer(image_data, mime=True)
    
    document = {
        "hotel_id": hotel_id,
        "filename": filename,
        "mime_type": mime_type,
        "image_data": Binary(image_data)
    }
    
    result = await db.images.insert_one(document)
    return str(result.inserted_id)

async def get_hotel_images(hotel_id: int):
    db = await get_db()
    cursor = db.images.find({"hotel_id": hotel_id})
    images = []
    async for doc in cursor:
        images.append({
            "id": str(doc["_id"]),
            "filename": doc["filename"],
            "mime_type": doc["mime_type"]
        })
    return images

async def get_image(image_id: str):
    db = await get_db()
    doc = await db.images.find_one({"_id": ObjectId(image_id)})
    if doc:
        return doc["image_data"], doc["mime_type"]
    return None, None

async def delete_image(image_id: str):
    db = await get_db()
    result = await db.images.delete_one({"_id": ObjectId(image_id)})
    return result.deleted_count > 0