from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api import users
from app.api import auth
from app.api import tasks
from app.db.base import Base
from app.db.session import engine
from app.error.register_handlers import register_all_error
from app.utlis.rate_limiter import TokenBucketLimiter

app = FastAPI()

# Resolve absolute static directory path (compatible with Vercel serverless)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def dispatch(request: Request, call_next):

    try:
        response = await call_next(request)
        return response

    except Exception as exc:
        handler = app.exception_handlers.get(Exception)
        return await handler(request, exc)


register_all_error(app)
app.add_middleware(TokenBucketLimiter, bucket_size=10, refill_rate=1.0)


# Serve root SPA frontend
@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>Frontend index.html not found! Path: {index_path}</h1>", status_code=404)


app.include_router(auth.router, prefix="/auth", tags=["Auth Endpoints"])

app.include_router(users.router, tags=["User Endpoints"])

app.include_router(tasks.router, tags=["Task Endpoints"])
