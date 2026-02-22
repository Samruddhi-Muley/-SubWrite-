import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
SENDER_NAME = "SubWrite"


def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Send an email using Gmail SMTP
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        message["To"] = to_email

        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)

        part2 = MIMEText(html_content, "html")
        message.attach(part2)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


def send_welcome_email(to_email: str, username: str):
    """
    Send welcome email to new users
    """
    subject = "Welcome to SubWrite! 🎉"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to SubWrite!</h1>
            </div>
            <div class="content">
                <h2>Hello {username}! 👋</h2>
                <p>Thank you for joining SubWrite, the platform where writers share their stories and ideas.</p>

                <p><strong>What's next?</strong></p>
                <ul>
                    <li>Complete your profile and add a bio</li>
                    <li>Start writing your first article</li>
                    <li>Explore articles from other writers</li>
                    <li>Use markdown to format your posts beautifully</li>
                </ul>

                <a href="http://localhost:8000/dashboard" class="button">Go to Dashboard</a>

                <p style="margin-top: 30px;">Happy writing! ✍️</p>
                <p>The SubWrite Team</p>
            </div>
            <div class="footer">
                <p>This email was sent to {to_email}</p>
                <p>© 2024 SubWrite. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Welcome to SubWrite!

    Hello {username}!

    Thank you for joining SubWrite, the platform where writers share their stories and ideas.

    What's next?
    - Complete your profile and add a bio
    - Start writing your first article
    - Explore articles from other writers
    - Use markdown to format your posts beautifully

    Visit: http://localhost:8000/dashboard

    Happy writing!
    The SubWrite Team
    """

    return send_email(to_email, subject, html_content, text_content)


def send_verification_email(to_email: str, username: str, verification_token: str):
    """
    Send email verification link
    """
    subject = "Verify Your Email - SubWrite"

    verification_link = f"http://localhost:8000/verify-email?token={verification_token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📧 Verify Your Email</h1>
            </div>
            <div class="content">
                <h2>Hello {username}!</h2>
                <p>Thanks for signing up for SubWrite. Please verify your email address to complete your registration.</p>

                <a href="{verification_link}" class="button">Verify Email Address</a>

                <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                    Or copy and paste this link in your browser:<br>
                    <code>{verification_link}</code>
                </p>

                <p style="margin-top: 30px; font-size: 14px; color: #ef4444;">
                    <strong>Note:</strong> This link will expire in 24 hours.
                </p>

                <p style="margin-top: 20px;">
                    If you didn't create this account, you can safely ignore this email.
                </p>
            </div>
            <div class="footer">
                <p>This email was sent to {to_email}</p>
                <p>© 2024 SubWrite. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Verify Your Email - SubWrite

    Hello {username}!

    Thanks for signing up for SubWrite. Please verify your email address to complete your registration.

    Click here to verify: {verification_link}

    This link will expire in 24 hours.

    If you didn't create this account, you can safely ignore this email.

    The SubWrite Team
    """

    return send_email(to_email, subject, html_content, text_content)


def send_password_reset_email(to_email: str, username: str, reset_token: str):
    """
    Send password reset link
    """
    subject = "Reset Your Password - SubWrite"

    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Reset Your Password</h1>
            </div>
            <div class="content">
                <h2>Hello {username}!</h2>
                <p>We received a request to reset your password for your SubWrite account.</p>

                <a href="{reset_link}" class="button">Reset Password</a>

                <p style="margin-top: 30px; font-size: 14px; color: #6b7280;">
                    Or copy and paste this link in your browser:<br>
                    <code>{reset_link}</code>
                </p>

                <p style="margin-top: 30px; font-size: 14px; color: #ef4444;">
                    <strong>Note:</strong> This link will expire in 1 hour for security reasons.
                </p>

                <p style="margin-top: 20px;">
                    If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
                </p>
            </div>
            <div class="footer">
                <p>This email was sent to {to_email}</p>
                <p>© 2024 SubWrite. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Reset Your Password - SubWrite

    Hello {username}!

    We received a request to reset your password for your SubWrite account.

    Click here to reset: {reset_link}

    This link will expire in 1 hour for security reasons.

    If you didn't request a password reset, please ignore this email.

    The SubWrite Team
    """

    return send_email(to_email, subject, html_content, text_content)