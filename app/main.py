import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.api.v1.endpoints.public_menu import router as public_menu_router
from app.api.v1.endpoints.web import router as web_router
from app.api.v1.endpoints.admin_categories import router as admin_categories_router
from app.api.v1.endpoints.admin_items import router as admin_items_router
from app.core.deps import ADMIN_LOGIN_PATH, HTMLAuthRequired
from app.core.uploads import ensure_upload_dir

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "template")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_upload_dir()
    yield


app = FastAPI(
    title="Hikaya",
    version="1.0.0",
    description="Hikaya restaurant menu and admin backend.",
    lifespan=lifespan,
)


@app.exception_handler(HTMLAuthRequired)
async def html_auth_required_handler(request: Request, exc: HTMLAuthRequired):
    return RedirectResponse(url=ADMIN_LOGIN_PATH, status_code=302)

# Serve template assets at /assets and /sass
app.mount("/assets", StaticFiles(directory=os.path.join(TEMPLATE_DIR, "assets")), name="assets")
app.mount("/sass", StaticFiles(directory=os.path.join(TEMPLATE_DIR, "sass")), name="sass")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# API routes
app.include_router(router)

# Web (HTML) routes — must come after static mounts
app.include_router(public_menu_router)
app.include_router(web_router)
app.include_router(admin_categories_router)
app.include_router(admin_items_router)
