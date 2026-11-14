import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config.settings import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    MANAGER_EMAIL
)


class EmailService:
    def __init__(self):
        self.mail_server = MAIL_SERVER
        self.mail_port = MAIL_PORT
        self.mail_username = MAIL_USERNAME
        self.mail_password = MAIL_PASSWORD
        self.mail_from = MAIL_FROM
        self.manager_email = MANAGER_EMAIL

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

    def send_order_pending_approval_notice(self, order_number: str, total_amount, sales_rep_name: str, manager_email: str = None):
        recipient = manager_email or self.manager_email
        subject = f"Action Required: Order {order_number} Requires Approval"
        html = f"""
        <h3>Manager Order Approval Alert</h3>
        <p>A new high-value sales order has been created and requires your review.</p>
        <ul>
            <li><strong>Order Number:</strong> {order_number}</li>
            <li><strong>Total Amount:</strong> ${total_amount:,.2f}</li>
            <li><strong>Created By:</strong> {sales_rep_name}</li>
            <li><strong>Status:</strong> PENDING_APPROVAL</li>
        </ul>
        <p>Please log in to the management dashboard to approve or reject this order.</p>
        """
        self._send_email(recipient, subject, html)

    def send_order_decision_notice(self, sales_rep_email: str, order_number: str, decision: str, notes: str = None):
        subject = f"Order {order_number} Has Been {decision}"
        html = f"""
        <h3>Sales Order Status Update</h3>
        <p>Your sales order has been reviewed by management.</p>
        <ul>
            <li><strong>Order Number:</strong> {order_number}</li>
            <li><strong>Decision:</strong> {decision}</li>
            <li><strong>Manager Notes:</strong> {notes or 'No notes provided'}</li>
        </ul>
        """
        self._send_email(sales_rep_email, subject, html)


email_service = EmailService()
