import os

from fastapi.templating import Jinja2Templates

PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "views"))
