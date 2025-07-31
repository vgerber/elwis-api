from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.routes import ftm, cache

app = FastAPI(redoc_url=None, docs_url=None, openapi_url="/openapi.json")

app.include_router(ftm.router)
app.include_router(cache.router)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def get_stoplight_docs():
    with open("static/docs.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
