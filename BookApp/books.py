from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [

    {"title": "First Book", "author": "First author", "category": "science"},
    {"title": "Second Book", "author": "Second author", "category": "science"},
    {"title": "Third Book", "author": "Third author", "category": "sport"},
    {"title": "Fourth Book", "author": "Fourth author", "category": "science"},
    {"title": "Fifth Book", "author": "Fifth author", "category": "sport"},
    {"title": "Sixth Book", "author": "Second author", "category": "sport"},
    {"title": "Seventh Book", "author": "Second author", "category": "sport"},

]


@app.get("/books")
async def get_all_books():
    return BOOKS


@app.get("/books/last_book")
async def get_last_book():
    return BOOKS[-1]


@app.get('/books/{book_tite}')
async def get_book_by_title(book_tite: str):
    print('title')
    for book in BOOKS:
        if book.get('title').casefold() == book_tite.casefold():
            return book


@app.get('/books/')
async def get_books_by_category(category: str):
    print('category')
    books_query = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_query.append(book)

    return books_query


@app.get('/books/{book_author}/')
async def get_books_by_category_and_author(author: str, category: str):
    print('category and author')
    books_query = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_query.append(book)

    return books_query


@app.post('/books/create_book')
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put('/books/update_book')
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
            break


@app.delete('/books/delete_book/{book_title}')
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
