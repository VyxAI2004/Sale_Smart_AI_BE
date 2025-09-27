import time

import alembic.config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app_environment import AppEnvironment
from controllers import api_router
from env import env

# Migrate the database to its latest version
# Not thread safe, so it should be update once we are running multiple instances
alembic.config.main(argv=["--raiseerr", "upgrade", "head"])

app = FastAPI(debug=env.APP_DEBUG)

# Add a simple request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Get client IP
        client_host = request.client.host if request.client else "unknown"

        # Log the request details
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
        print(
            f"[REQUEST] {client_host} - {start_time} - {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}ms"
        )

        return response


# Add the middleware
app.add_middleware(RequestLoggingMiddleware)

if AppEnvironment.is_local_env(env.APP_ENV):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

elif AppEnvironment.is_remote_env(env.APP_ENV):
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=env.ALLOWED_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "TO DO APP API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}