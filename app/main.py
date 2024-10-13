from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core import app_settings
from .utils import create_tables
from .api.v1.endpoints import auth_router, subscription_router, projects_router, tasks_router


# Lifespan function to handle startup and shutdown events:


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(debug=app_settings.DEBUG, title=app_settings.APP_NAME,
              description=app_settings.APP_DESCRIPTION, version=app_settings.APP_VERSION, lifespan=lifespan)
app.include_router(subscription_router,
                   prefix="/api/v1/subscription", tags=["Subscription"])
app.include_router(
    projects_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])


# Include/Register API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])


# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
