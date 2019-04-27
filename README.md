# Project:Item-Catalog
We are building a online BOOK STORE where users get to view different boooks placed according to their categories and can create add, edit, and delete books. It also provides JSON endpoints for these. Used postgresql server and sqlalchemy. Google signin is made to ensure safe authentication and verification of users. This site may not look most appealing but the server configuration is of high standards to ensure data security, maintainability and efficiency.

## Key Functionality
  - Google Authentication
  - Local Premission System
  - Easy to add, update, create, delete information.
  - Easily accessible data with JSON Endpoints

## What does Local Permission System do ?
This website gives each user full control over books created by them but only viewing rights over the books created by other users !!!
Only the user who created a book or category can edit or delete it no one else can do that.

### Prerequisites
  - Python 3.5
  - Vagrant
  - VirtualBox

### How to Run
- Clone this repository.
- Open your vagrant machine and change directory into this folder
- Run the python code catalog.py using the following command
` python3 catalog.py`
- Open your browser and go to this url http://localhost:8000

## JSON endpoints
#### Returns JSON of all Categories
`/bookstore/JSON/`
#### Returns JSON of all books in specific category
`/bookstore/<int:c_id>/JSON/`
#### Returns JSON of a given book
`/bookstore/<int:c_id>/vbook/<int:b_id>/JSON/`
