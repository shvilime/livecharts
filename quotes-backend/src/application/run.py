import uvicorn
from application.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_config=settings.uvicorn_logging
    )
