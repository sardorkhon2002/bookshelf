from uuid import uuid4
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI()

# Define MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.bookshelf
collection = db.bookshelf


# Pydantic model to validate data
class Book(BaseModel):
    title: str
    description: str
    imageUrl: Optional[str] = None


os.makedirs("uploads", exist_ok=True)


# Route to get books with pagination
@app.get("/api/books", response_model=List[Book])
async def read_books(page: int = 1, limit: int = 2):
    skip = (page - 1) * limit
    books_cursor = collection.find().skip(skip).limit(limit)
    books = await books_cursor.to_list(length=limit)
    return books


# Route to add a new book
@app.post("/api/books", response_model=Book)
async def add_book(title: str = Form(...), description: str = Form(...), image: UploadFile = File(...)):
    file = image
    file_id = str(uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"

    # Save file to disk
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Save the book to the database
    book_data = {
        "title": title,
        "description": description,
        "imageUrl": f"http://localhost:8000/api/images/{file_id}_{file.filename}"
    }
    await collection.insert_one(book_data)
    return book_data


@app.get("/api/images/{filename}")
async def get_image(filename: str):
    return FileResponse(f"uploads/{filename}")


# Run the Uvicorn server to serve your application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
