import ssl
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
from starlette.responses import JSONResponse

from core.config import settings
from db.models.user import User


logger = logging.getLogger(__name__)


def read_html_file(file_path) -> str:
    with open(file_path, 'r') as file:
        return file.read()


async def send_email(subject: str, recipient_email: str, html_content: str) -> JSONResponse:
    """
    Generic email sending function.
    """
    email_sender = settings.EMAIL_SENDER
    # email_password = settings.EMAIL_PASSWORD
    email_port = int(settings.EMAIL_PORT)
    email_receiver = recipient_email

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    html_part = MIMEText(html_content, 'html')
    em.attach(html_part)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(settings.EMAIL_SERVER, email_port) as smtp:
            smtp.starttls(context=context)
            smtp.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
            smtp.sendmail(settings.EMAIL_SENDER, email_receiver, em.as_string())
            logger.info("Email sent successfully")
        return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
    except Exception as e:
        logger.error(f"Error occurred while sending email {e.__str__()}")
        raise Exception(f"An error occurred: {e}")


async def send_password_reset_email(email: str, reset_token: str, username: str, email_template):
    # subject = "Reset Password"
    rest_base_url = settings.BASE_URL
    if not settings.BASE_URL.startswith("http"):
        rest_base_url = f"https://{settings.BASE_URL}" if settings.PRODUCTION_ENV else f"http://{settings.BASE_URL}"
    reset_password_url = f"{rest_base_url}{settings.URL_PATH}?{urlencode({'token': reset_token})}"

    if email_template:
        html_content = email_template.html_content.format(username, reset_password_url)
        email_subject = email_template.subject
    else:
        try:
            html_content = read_html_file(
                'utils/templates/password-reset.html'
            ).replace("Hi {}", f"Hi {username},").replace("href={}", f"href={reset_password_url}")
        except FileNotFoundError:
            html_content = f"Hello {username}, please reset your password by clicking this link: {reset_password_url}"
        email_subject = "Learningbrix Password Reset"
    await send_email(email_subject, email, html_content)


async def send_password_reset_confirmation(email: str, username: str, user_role: str) -> None:
    """Send the password reset confirmation email"""
    try:
        html_content = read_html_file(
            "utils/templates/reset_confirmation.html"
        ).replace("Hi {}", f"Hi {username}, ({user_role})")
    except FileNotFoundError:
        html_content = f"Hi {username}, This is a confirmation of a successful password reset."
    email_subject = "Learningbrix Password Reset Confirmation"
    await send_email(email_subject, email, html_content)


async def welcome_new_user(email: str, username: str, reset_token: str) -> None:
    """Send a warm welcome message to the newly registered user"""
    try:
        reset_url = settings.BASE_URL
        if not settings.BASE_URL.startswith("http"):
            reset_url = f"https://{settings.BASE_URL}" if settings.PRODUCTION_ENV else f"http://{settings.BASE_URL}"
        reset_password_url = f"{reset_url}{settings.URL_PATH}?{urlencode({'token': reset_token})}"
        html_content = read_html_file(
            "utils/templates/welcome.html"
        ).replace(
            "Welcome to LearningBrix, {}!", f"Welcome to Learningbrix, {username}!)"
        ).replace("href={}", f"href={reset_password_url}")
    except FileNotFoundError:
        html_content = f"""
        Welcome to Learningbrix, {username}!, We are excited to have you join us.
        Click the link below to set your password {reset_password_url}"""
    email_subject = "Learningbrix Welcome Message"
    await send_email(email_subject, email, html_content)
