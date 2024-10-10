from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routes import auth, user, token, settings as s, socket, friends
import time

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]
# whoiam
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(token.router, prefix="/token", tags=["token"])
app.mount("/avatars", StaticFiles(directory=settings.AVATAR_UPLOAD_DIR), name="avatars")
app.include_router(s.router, prefix="/settings", tags=["settings"])
app.include_router(socket.router, prefix="/socket", tags=["socket"])
app.include_router(friends.router, prefix="/friends", tags=["friends"])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
