from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Book, BookUpdate

router = APIRouter()

# POST /book
# The first endpoint we'll implement is the POST /books endpoint for creating a new book. 

# The route is / because we'll prefix all the books endpoints with /books. 
# The response_description will be displayed in the API documentation. 
# The status_code is the HTTP status code returned when the request is successful. 
# We use the Book model to validate both the data passed in the request body and the response we sent back. 
# FastAPI handles the validation for us. 
# In the body of the function, we're using PyMongo's insert_one() method to add the new book to the books collection. 
# We're using the find_one() method to retrieve the newly created book from the database. 
# You can read more about the insert_one() and find_one() methods in the PyMongo documentation article for collection level operations.
@router.post("/", response_description="Create a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    new_book = request.app.database["books"].insert_one(book)
    created_book = request.app.database["books"].find_one(
        {"_id": new_book.inserted_id}
    )

    return created_book

# GET /book
# Next, we'll implement the GET /book endpoint for returning a list with all documents in the books collection. 
# Append the following to the end of the routes.py file:

# For the response model, we're using the List[Book] type. This means that the response will be a list of Book objects. 
# We're also using the find() method to retrieve no more than 100 books from the database. 
# To learn more about limit and the other parameters of the find() method, check out the dedicated PyMongo documentation page.
@router.get("/", response_description="List all books", response_model=List[Book])
def list_books(request: Request):
    books = list(request.app.database["books"].find(limit=100))
    return books

# Here, we're using the find_one() method to retrieve a single book from the database. 
# If the book is found, we're returning it. 
# If the book is not found, we're raising an HTTPException with a 404 Not Found status code and an appropriate message.
@router.get("/{id}", response_description="Get a single book by id", response_model=Book)
def find_book(id: str, request: Request):
    if (book := request.app.database["books"].find_one({"_id": id})) is not None:
        return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

# First, we're building an object that we'll use to update the book.
# Then, if there are any fields in the book object, we're using the update_one() method to update the book in the database. 
# It's important to note that we're using the $set update operator to ensure that only the specified fields are updated instead of rewriting the whole document.

# Then, we check the modified_count attribute of the update_result to verify that the book was updated. 
# If that's the case, we're using the find_one() method to retrieve the updated book from the database and return it.

#If there are no fields in the book object, we're just returning the existing book. 
# However, if the book is not found, we're raising an HTTPException with a 404 Not Found status code.
@router.put("/{id}", response_description="Update a book", response_model=Book)
def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    book = {k: v for k, v in book.dict().items() if v is not None}
    if len(book) >= 1:
        update_result = request.app.database["books"].update_one(
            {"_id": id}, {"$set": book}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

    if (
        existing_book := request.app.database["books"].find_one({"_id": id})
    ) is not None:
        return existing_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")

# If the book was deleted, we're returning a 204 No Content status code. 
# This is a success status code indicating that the request has succeeded and there's no content to send in the response payload body.
@router.delete("/{id}", response_description="Delete a book")
def delete_book(id: str, request: Request, response: Response):
    delete_result = request.app.database["books"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with ID {id} not found")



# Register the /book endpoints
# Finally, we need to register the /book endpoints. 
# Open the main.py file, import the routes module, and register the book router. 