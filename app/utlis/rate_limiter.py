# token_bucket.py
import time
from collections import defaultdict
from dataclasses import dataclass
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi.responses import JSONResponse


@dataclass
class Bucket:
    tokens: float
    last_update: float


class TokenBucketLimiter(BaseHTTPMiddleware):
    """Token bucket rate limiter - allows controlled bursts"""

    def __init__(self, app: ASGIApp, bucket_size: int, refill_rate: float):
        super().__init__(app)
        self.bucket_size = bucket_size
        self.refill_rate = refill_rate
        self.buckets: dict = {}

    def _get_bucket(self, ip_address: str) -> Bucket:
        """Get or create bucket for key"""

        if ip_address not in self.buckets:
            self.buckets[ip_address] = Bucket(
                tokens=self.bucket_size, last_update=time.time()
            )
        return self.buckets[ip_address]

    def _refill(self, bucket: Bucket) -> None:
        """Refill tokens based on delta time"""
        now = time.time()
        delta = now - bucket.last_update

        # Add tokens based on elapsed time
        bucket.tokens = min(
            self.bucket_size, bucket.tokens + (delta * self.refill_rate)
        )
        bucket.last_update = now

    # BaseHTTPMiddleware expects a method named dispatch to handle the request/response cycle.
    # If it's named allow_request, it will simply be ignored.
    async def dispatch(self, request: Request, call_next):
        """Get time to wait for tokens"""
        client_ip = request.client.host

        bucket = self._get_bucket(client_ip)
        self._refill(bucket)

        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return await call_next(request)

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"msg": "Please try again later"},
        )
