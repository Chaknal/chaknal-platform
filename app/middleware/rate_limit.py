from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
import asyncio
from config.settings import settings


class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def is_allowed(self, client_ip: str) -> bool:
        async with self.lock:
            now = time.time()
            # Clean old requests (older than 1 minute)
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < 60
            ]

            # Check if rate limit exceeded
            if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
                return False

            # Add current request
            self.requests[client_ip].append(now)
            return True

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host

    if not await rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "type": "rate_limit_exceeded"
            }
        )

    response = await call_next(request)
    return response
