from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from instagram.routers import router as instagram_router


app = FastAPI(
    title="Facebook/Instagram APIS",
    description="Facebook/Instagram APIS"
)

app.include_router(instagram_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


@app.get("/", include_in_schema=False)
def get_home_page():
    return RedirectResponse("/docs")
