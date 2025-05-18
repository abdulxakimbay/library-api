# Third party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local
from .auth import router as auth_router
from .books import router as books_router
from .readers import router as readers_router
from .borrowed_books import router as borrowed_books_router

####################################################################################################
# SETTINGS
####################################################################################################

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

####################################################################################################
# ROUTERS
####################################################################################################

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(readers_router)
app.include_router(borrowed_books_router)