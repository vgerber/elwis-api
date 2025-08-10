from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.database import create_db_and_tables
from app.routes import ftm, cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # Cleanup code can go here


app = FastAPI(
    redoc_url=None, docs_url=None, openapi_url="/openapi.json", lifespan=lifespan
)

app.include_router(ftm.router)
app.include_router(cache.router)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def get_stoplight_docs():
    with open("static/docs.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
