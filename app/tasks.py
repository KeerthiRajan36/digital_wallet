# app/tasks.py
from celery import Celery
from app.config import settings
import smtplib
from email.message import EmailMessage

celery = Celery(
    __name__,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery.task
def send_transfer_email(sender_email: str, receiver_email: str, amount: float):
    """Send email notification for transfer"""
    try:
        msg = EmailMessage()
        msg.set_content(f"""
        Transfer Notification:
        Amount: ₹{amount}
        From: {sender_email}
        To: {receiver_email}
        """)
        
        msg['Subject'] = 'Money Transfer Notification'
        msg['From'] = settings.SMTP_USER
        msg['To'] = receiver_email
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return {"status": "success", "message": "Email sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery.task
def generate_daily_summary():
    """Generate daily transaction summary"""
    # Implementation for daily summary generation
    pass