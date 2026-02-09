"""HTTP API for parser_site."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .parser import parse_contacts

MAX_INPUT_CHARS = 100_000
PARSE_TIMEOUT_SECONDS = 1.0


class ParseRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text blob to parse for contacts",
        examples=[
            "Contact: dev@example.com, site: https://example.com, phone: +1 (202) 555-0182"
        ],
    )


class ParseResponse(BaseModel):
    emails: list[str] = Field(examples=[["dev@example.com"]])
    urls: list[str] = Field(examples=[["https://example.com"]])
    phones: list[str] = Field(examples=[["+12025550182"]])


class ErrorResponse(BaseModel):
    detail: str


app = FastAPI(
    title="Parser Site API",
    version="0.1.0",
    description="API for extracting emails, URLs and phone numbers from text.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/parse",
    response_model=ParseResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        408: {"model": ErrorResponse, "description": "Parsing timeout"},
        413: {"model": ErrorResponse, "description": "Input too large"},
    },
    tags=["parser"],
)
async def parse_endpoint(payload: ParseRequest) -> ParseResponse:
    text = payload.text

    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty")

    if len(text) > MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Input text exceeds maximum length of {MAX_INPUT_CHARS} characters",
        )

    try:
        result = await asyncio.wait_for(asyncio.to_thread(parse_contacts, text), PARSE_TIMEOUT_SECONDS)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=408,
            detail=f"Parsing exceeded timeout of {PARSE_TIMEOUT_SECONDS} seconds",
        ) from exc

    return ParseResponse(emails=result.emails, urls=result.urls, phones=result.phones)


@app.get("/", tags=["system"])
def root() -> dict[str, Any]:
    return {
        "service": "parser-site-api",
        "docs": "/docs",
        "parse_endpoint": "/parse",
        "limits": {
            "max_input_chars": MAX_INPUT_CHARS,
            "parse_timeout_seconds": PARSE_TIMEOUT_SECONDS,
        },
    }
