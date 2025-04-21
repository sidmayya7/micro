from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from app.image_handler import save_image, get_hotel_images, get_image, delete_image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class PaymentRequest(BaseModel):
    booking_details: dict
    amount: float

@app.get("/")
async def root():
    return {"message": "Image service is running"}

# Payment endpoints
@app.get("/payment")
async def payment_page():
    # Read the payment.html file and return it
    with open("static/payment.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/process-payment")
async def process_payment(payment: PaymentRequest):
    logger.info(f"Processing payment for amount: {payment.amount}")
    # This is a placeholder that always returns success
    return {
        "status": "success",
        "message": "Payment processed successfully",
        "booking_details": payment.booking_details
    }

@app.post("/hotels/{hotel_id}/images")
async def upload_hotel_image(hotel_id: int, file: UploadFile = File(...)):
    logger.info(f"Receiving upload request for hotel {hotel_id}")
    try:
        contents = await file.read()
        image_id = await save_image(hotel_id, contents, file.filename)
        logger.info(f"Successfully saved image {image_id} for hotel {hotel_id}")
        return {"image_id": image_id}
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hotels/{hotel_id}/images")
async def list_hotel_images(hotel_id: int):
    logger.info(f"Fetching images for hotel {hotel_id}")
    try:
        images = await get_hotel_images(hotel_id)
        logger.info(f"Found {len(images)} images for hotel {hotel_id}")
        return images
    except Exception as e:
        logger.error(f"Error fetching images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images/{image_id}")
async def serve_image(image_id: str):
    logger.info(f"Serving image {image_id}")
    try:
        image_data, mime_type = await get_image(image_id)
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found")
        return Response(content=image_data, media_type=mime_type)
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/images/{image_id}")
async def remove_image(image_id: str):
    logger.info(f"Deleting image {image_id}")
    try:
        success = await delete_image(image_id)
        if not success:
            raise HTTPException(status_code=404, detail="Image not found")
        logger.info(f"Successfully deleted image {image_id}")
        return {"message": "Image deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))