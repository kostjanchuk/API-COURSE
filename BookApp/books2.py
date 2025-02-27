from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    category: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, category, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.category = category
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="Not required field", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    category: str = Field(min_length=3, max_length=20)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=0, lt=9999)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Second Book",
                "author": "Second author",
                "category": "science",
                "rating": 5,
                "published_date": 2025
            }
        }
    }


BOOKS = [

    Book(1, "First Book", "First author", "science", 5,
         2025),
    Book(2, "Second Book", "Second author", "sport", 5,
         2025),
    Book(3, "Third Book", "Third author", "sport", 5,
         2025),
    Book(4, "Fourth Book", "Fourth author", "sport", 5,
         2025),
    Book(5, "Fifth Book", "Fifth author", "science", 5,
         2025),
    Book(6
         , "Sixth Book", "First author", "science", 5,
         2025)
]


@app.get('/books', status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.post('/create-book', status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.dict())
    BOOKS.append(generate_id_for_book(new_book))


@app.get('/books/{book_id}', status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.get('/books/', status_code=status.HTTP_200_OK)
async def get_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    book_query = []
    for book in BOOKS:
        if book.rating == book_rating:
            book_query.append(book)
    return book_query


@app.get('/books/publish/{published_date}', status_code=status.HTTP_200_OK)
async def get_book_by_publish_date(published_date: int = Path(gt=0, lt=9999)):
    book_query = []
    for book in BOOKS:
        if book.published_date == published_date:
            book_query.append(book)
    return book_query


@app.put('/books/update_book', status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    book_state = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = book_request
            book_state = True
            break
    if not book_state:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete('/books/delete_book/{book_id}', status_code=status.HTTP_200_OK)
async def delete_book(book_id: int = Path(gt=0)):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            return BOOKS.pop(i)
    raise HTTPException(status_code=404, detail="Item not found")


def generate_id_for_book(book: Book):
    book.id = 1 if len(BOOKS) == 0 else len(BOOKS) + 1
    return book
