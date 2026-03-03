from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.app.api import router as api_router
from src.app.core import settings, setup_logging, http_exception_handler, general_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Setup logging
    setup_logging()
    yield
    # Shutdown logic if needed


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME, 
        openapi_url=f"{settings.API_V1_STR}/openapi.json", 
        lifespan=lifespan
    )

    # Set all CORS enabled origins
    import time
    import structlog
    from fastapi import Request
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        logger = structlog.get_logger("api.access")
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            "request_processed",
            http_method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration=process_time,
        )
        return response

    # Register Exception Handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Include Router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
