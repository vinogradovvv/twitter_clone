from contextlib import asynccontextmanager

from db import db_models
from db.database import async_session, engine
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from init_db import init_db
from routers import media, tweets, users
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(db_models.Base.metadata.drop_all)
        await conn.run_sync(db_models.Base.metadata.create_all)
    async with async_session() as session:
        await init_db(session=session)
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Twitter_API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception):
    print(exception.errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": exception.errors()[0]["type"],
                "error_message": exception.errors()[0]["msg"],
            }
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exception):
    if "result" in exception.__dict__:
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                {
                    "result": exception.result,
                    "error_type": exception.error_type,
                    "error_message": exception.error_message,
                }
            ),
        )
    return JSONResponse(
        status_code=exception.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": exception.detail,
                "error_message": exception.detail,
            }
        ),
    )


app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(media.router)
