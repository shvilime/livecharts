from sqlalchemy import text
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.engine import CursorResult

from application.core.config import settings


router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    responses={404: {"description": "Not found"}},
)


@router.get("/info")
async def info():
    return JSONResponse(content={"service": settings.application, "version": settings.version})


@router.get("/db")
async def db_test(r: Request):
    async with r.app.state.db.begin() as conn:
        query: str = "SELECT 1;"
        cursor: CursorResult = await conn.execute(text(query))
        result: list = cursor.fetchall()
    return JSONResponse({"status": len(result) == 1})
