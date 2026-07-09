from sqlalchemy.orm import Session
from app.core.config import settings
from app.error.custom_execption import UserNotFound
from app.utlis.mail_utils.mail import mail, create_message
from app.utlis.mail_utils.url_safe_token import (
    create_url_safe_token,
    decode_url_safe_token,
)
from app.repositories.user_repository import UserRepository


class EmailService:
    def send_mail(self, email, bg_tasks):

        token = create_url_safe_token({"email": email})

        link = f"http://{settings.DOMAIN}/auth/verify/{token}"
        html_message = f"""
                <h1>Verify your Email</h1>
                <p>Please click this <a href="{link}">link</a> to very your email</p>
            """

        message = create_message(
            recipients=[email], subject="Verify your email", body=html_message
        )

        bg_tasks.add_task(mail.send_message, message)


class VerifyMail:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def verify(self, token):
        token_data = decode_url_safe_token(token)
        user_email = token_data["email"]

        with self.db.begin():
            user = self.repo.get_by_email(user_email)

            if not user:
                raise UserNotFound()

            setattr(user, "is_verified", True)

            return {"message": "Account verified successfully."}
