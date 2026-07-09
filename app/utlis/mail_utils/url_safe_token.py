from fastapi import status
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings
from fastapi import HTTPException


serializer = URLSafeTimedSerializer(
    secret_key=settings.ACCESS_SECRET_KEY, salt="email-configuration"
)


def create_url_safe_token(data: dict):

    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)

        return token_data

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e)
