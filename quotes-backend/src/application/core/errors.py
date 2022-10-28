from typing import Union
from pydantic import ValidationError
from fastapi import HTTPException, Request
from starlette.responses import JSONResponse
from fastapi.openapi.constants import REF_PREFIX
from fastapi.exceptions import RequestValidationError
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.openapi.utils import validation_error_response_definition
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED

from application.core.config import settings

validation_error_response_definition["properties"] = {
    "errors": {
        "title": "Errors",
        "type": "array",
        "items": {"$ref": "{0}ValidationError".format(REF_PREFIX)},
    },
}


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)


async def http422_error_handler(_: Request, exc: Union[RequestValidationError, ValidationError]) -> JSONResponse:
    settings.logger.error(exc)
    return JSONResponse(
        {"errors": [f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors()]},
        status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )


def unexpected_error_handler(_: Request, exc: Exception):
    settings.logger.exception(exc)
    return JSONResponse({"errors": ["Unexpected server error. Please call to support."]}, status_code=500)
