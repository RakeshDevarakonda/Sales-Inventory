import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config.settings import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    FRONTEND_URL
)


class INotificationService(ABC):
    """
    Interface Segregation Principle & Dependency Inversion:
    Abstract notification contract allowing swapping SMTP for SES/SendGrid/Twilio.
    """

    @abstractmethod
    def send_order_pending_approval_notice(self, order_number: str, total_amount, sales_rep_name: str, manager_email: str = None):
        pass

    @abstractmethod
    def send_order_decision_notice(self, sales_rep_email: str, order_number: str, decision: str, notes: str = None):
        pass


class EmailService(INotificationService):
    def __init__(self):
        self.mail_server = MAIL_SERVER
        self.mail_port = MAIL_PORT
        self.mail_username = MAIL_USERNAME
        self.mail_password = MAIL_PASSWORD
        self.mail_from = MAIL_FROM

    def _send_email(self, recipient: str, subject: str, html_content: str):
        # If credentials are not configured in .env, log cleanly to console (mock mode for local dev)
        if not self.mail_username or not self.mail_password:
            print("\n" + "=" * 60)
            print(" [EMAIL SERVICE MOCK DISPATCH]")
            print(f" To: {recipient}")
            print(f" Subject: {subject}")
            print(" Body:")
            print(html_content)
            print("=" * 60 + "\n")
            return

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.mail_from
            message["To"] = recipient

            part = MIMEText(html_content, "html")
            message.attach(part)

            with smtplib.SMTP(self.mail_server, self.mail_port, timeout=10) as server:
                server.starttls()
                server.login(self.mail_username, self.mail_password)
                server.sendmail(self.mail_from, recipient, message.as_string())
            print(f"Email successfully sent to {recipient}")
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")

    def send_order_pending_approval_notice(self, order_number: str, total_amount, sales_rep_name: str, manager_email: str):
        if not manager_email:
            return
        recipient = manager_email
        orders_url = f"{FRONTEND_URL}/orders"
        subject = f"Action Required: Order {order_number} Requires Approval"
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;">
            <h2 style="color: #0f172a; margin-top: 0; font-size: 20px; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px;">Manager Order Approval Alert</h2>
            <p style="color: #475569; font-size: 14px; line-height: 1.5;">
                A new high-value sales order exceeding the approval threshold has been submitted by <strong>{sales_rep_name}</strong> and is currently <strong>PENDING APPROVAL</strong>.
            </p>
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 20px 0;">
                <table style="width: 100%; font-size: 13px; color: #334155; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; width: 140px;">Order Number:</td>
                        <td style="padding: 6px 0; font-family: monospace; font-size: 14px; color: #0f172a;">{order_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600;">Total Amount:</td>
                        <td style="padding: 6px 0; font-weight: bold; color: #0f172a;">₹{float(total_amount):,.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600;">Created By:</td>
                        <td style="padding: 6px 0;">{sales_rep_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600;">Status:</td>
                        <td style="padding: 6px 0;"><span style="background-color: #fef3c7; color: #b45309; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">PENDING APPROVAL</span></td>
                    </tr>
                </table>
            </div>
            <div style="margin: 28px 0; text-align: center;">
                <a href="{orders_url}" style="background-color: #0f172a; color: #ffffff; padding: 12px 24px; font-size: 14px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block;">
                    Review & Approve Order →
                </a>
            </div>
        </div>
        """
        self._send_email(recipient, subject, html)

    def send_order_decision_notice(self, sales_rep_email: str, order_number: str, decision: str, notes: str = None):
        orders_url = f"{FRONTEND_URL}/orders"
        is_approved = decision.upper() == "APPROVED"
        status_bg = "#ecfdf5" if is_approved else "#fff1f2"
        status_color = "#047857" if is_approved else "#be123c"
        subject = f"Order {order_number} Has Been {decision.upper()}"
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;">
            <h2 style="color: #0f172a; margin-top: 0; font-size: 20px; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px;">Sales Order Status Update</h2>
            <p style="color: #475569; font-size: 14px; line-height: 1.5;">
                Your pending sales order has been reviewed by management.
            </p>
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 20px 0;">
                <table style="width: 100%; font-size: 13px; color: #334155; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600; width: 140px;">Order Number:</td>
                        <td style="padding: 6px 0; font-family: monospace; font-size: 14px; color: #0f172a;">{order_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600;">Decision:</td>
                        <td style="padding: 6px 0;"><span style="background-color: {status_bg}; color: {status_color}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">{decision.upper()}</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 6px 0; font-weight: 600;">Manager Notes:</td>
                        <td style="padding: 6px 0; color: #334155; font-style: italic;">{notes or 'No additional review notes provided'}</td>
                    </tr>
                </table>
            </div>
            <div style="margin: 28px 0; text-align: center;">
                <a href="{orders_url}" style="background-color: #0f172a; color: #ffffff; padding: 12px 24px; font-size: 14px; font-weight: 600; text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Order Details →
                </a>
            </div>
        </div>
        """
        self._send_email(sales_rep_email, subject, html)


email_service = EmailService()
