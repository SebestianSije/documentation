#!/usr/bin/env python3
"""
Email Service for KenyaNet ISP
Handles email notifications for billing, alerts, and customer communications
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS', 'billing@kenyanet.co.ke')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your-app-password')
        self.company_name = "KenyaNet ISP"
        
    def send_email(self, to_email, subject, body, is_html=False, attachments=None):
        """
        Send email to a recipient
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): Whether body is HTML
            attachments (list): List of file paths to attach
            
        Returns:
            dict: Response indicating success or failure
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.company_name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return {'status': 'success', 'message': 'Email sent successfully'}
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Global email service instance
email_service = EmailService()

def send_email(to_email, subject, body, is_html=False, attachments=None):
    """Convenience function to send email"""
    return email_service.send_email(to_email, subject, body, is_html, attachments)

# Email templates
EMAIL_TEMPLATES = {
    'welcome': {
        'subject': 'Welcome to KenyaNet ISP - Registration Successful',
        'body': '''Dear {name},

Welcome to KenyaNet ISP! We're excited to have you as our customer.

Your registration has been successfully completed with the following details:
- Name: {name}
- Phone: {phone}
- Package: {package}
- Monthly Fee: KES {amount}

Next Steps:
1. Our technical team will contact you within 24 hours to schedule installation
2. Installation is completely FREE and includes a WiFi router
3. You'll receive your first bill after installation

Payment Information:
- M-PESA Paybill: 123456
- Account Number: {phone}
- You can also pay via bank transfer or cash at our offices

Need Help?
- Call: +254 700 000 000
- WhatsApp: +254 700 000 001
- Email: support@kenyanet.co.ke

Thank you for choosing KenyaNet ISP for your internet needs!

Best regards,
KenyaNet ISP Team'''
    },
    
    'bill_notification': {
        'subject': 'KenyaNet ISP Bill - {month}',
        'body': '''Dear {name},

Your internet bill for {month} is now ready.

Bill Details:
- Package: {package}
- Billing Period: {period}
- Amount Due: KES {amount}
- Due Date: {due_date}

Payment Options:
1. M-PESA Paybill: 123456 (Account: {phone})
2. Bank Transfer: Account details available on request
3. Cash payment at our offices

To avoid service interruption, please ensure payment is made by the due date.

You can view and download your bill by logging into your customer portal at:
https://billing.kenyanet.co.ke

Thank you for your continued trust in KenyaNet ISP.

Best regards,
KenyaNet ISP Billing Team'''
    },
    
    'payment_confirmation': {
        'subject': 'Payment Confirmation - KenyaNet ISP',
        'body': '''Dear {name},

We have successfully received your payment. Thank you!

Payment Details:
- Amount: KES {amount}
- Date: {date}
- Method: {method}
- Receipt/Reference: {receipt}

Your account is now up to date and your service will remain active.

Your next bill will be generated on {next_bill_date}.

Thank you for choosing KenyaNet ISP.

Best regards,
KenyaNet ISP Billing Team'''
    },
    
    'service_suspended': {
        'subject': 'Service Suspension Notice - KenyaNet ISP',
        'body': '''Dear {name},

This is to inform you that your internet service has been temporarily suspended due to overdue payment.

Overdue Details:
- Amount: KES {amount}
- Days Overdue: {days_overdue}
- Original Due Date: {due_date}

To restore your service immediately:
1. Pay via M-PESA Paybill 123456 (Account: {phone})
2. Your service will be restored automatically within 15 minutes of payment
3. For immediate assistance, call +254 700 000 000

We understand that circumstances can change, and we're here to help. If you're experiencing financial difficulties, please contact our customer service team to discuss payment arrangements.

We look forward to serving you again soon.

Best regards,
KenyaNet ISP Customer Service Team'''
    },
    
    'service_restored': {
        'subject': 'Service Restored - Welcome Back to KenyaNet ISP',
        'body': '''Dear {name},

Great news! Your internet service has been successfully restored.

Your connection should be active within the next few minutes. If you experience any technical issues, please don't hesitate to contact our support team.

Payment Received:
- Amount: KES {amount}
- Date: {date}

Thank you for your payment and for choosing KenyaNet ISP. We appreciate your business and look forward to continuing to serve you.

For any technical support:
- Call: +254 700 000 000
- WhatsApp: +254 700 000 001
- Email: support@kenyanet.co.ke

Welcome back!

Best regards,
KenyaNet ISP Team'''
    },
    
    'package_change': {
        'subject': 'Package Change Confirmation - KenyaNet ISP',
        'body': '''Dear {name},

Your internet package has been successfully changed.

Change Details:
- Previous Package: {old_package}
- New Package: {new_package}
- New Monthly Fee: KES {new_amount}
- Effective Date: {effective_date}

The new package will be reflected in your next billing cycle. You may notice improved speeds within the next few hours.

If you have any questions about your new package or need technical support, please contact us:
- Call: +254 700 000 000
- Email: support@kenyanet.co.ke

Thank you for choosing KenyaNet ISP.

Best regards,
KenyaNet ISP Customer Service Team'''
    }
}

def send_templated_email(to_email, template_name, **kwargs):
    """
    Send email using predefined templates
    
    Args:
        to_email (str): Recipient email address
        template_name (str): Name of the template to use
        **kwargs: Variables to substitute in the template
    """
    if template_name not in EMAIL_TEMPLATES:
        logger.error(f"Email template '{template_name}' not found")
        return {'status': 'error', 'message': f'Template {template_name} not found'}
    
    try:
        template = EMAIL_TEMPLATES[template_name]
        subject = template['subject'].format(**kwargs)
        body = template['body'].format(**kwargs)
        
        return send_email(to_email, subject, body)
    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        return {'status': 'error', 'message': f'Missing template variable: {e}'}
    except Exception as e:
        logger.error(f"Error sending templated email: {e}")
        return {'status': 'error', 'message': str(e)}

def send_welcome_email(to_email, name, phone, package, amount):
    """Send welcome email to new customer"""
    return send_templated_email(
        to_email,
        'welcome',
        name=name,
        phone=phone,
        package=package,
        amount=amount
    )

def send_bill_email(to_email, name, phone, package, month, period, amount, due_date):
    """Send bill notification email"""
    return send_templated_email(
        to_email,
        'bill_notification',
        name=name,
        phone=phone,
        package=package,
        month=month,
        period=period,
        amount=amount,
        due_date=due_date
    )

def send_payment_confirmation_email(to_email, name, amount, date, method, receipt, next_bill_date):
    """Send payment confirmation email"""
    return send_templated_email(
        to_email,
        'payment_confirmation',
        name=name,
        amount=amount,
        date=date,
        method=method,
        receipt=receipt,
        next_bill_date=next_bill_date
    )

def send_suspension_email(to_email, name, phone, amount, days_overdue, due_date):
    """Send service suspension email"""
    return send_templated_email(
        to_email,
        'service_suspended',
        name=name,
        phone=phone,
        amount=amount,
        days_overdue=days_overdue,
        due_date=due_date
    )

def send_restoration_email(to_email, name, amount, date):
    """Send service restoration email"""
    return send_templated_email(
        to_email,
        'service_restored',
        name=name,
        amount=amount,
        date=date
    )

def send_package_change_email(to_email, name, old_package, new_package, new_amount, effective_date):
    """Send package change confirmation email"""
    return send_templated_email(
        to_email,
        'package_change',
        name=name,
        old_package=old_package,
        new_package=new_package,
        new_amount=new_amount,
        effective_date=effective_date
    )

def send_bulk_email(recipients, subject, body, is_html=False):
    """
    Send email to multiple recipients
    
    Args:
        recipients (list): List of email addresses
        subject (str): Email subject
        body (str): Email body
        is_html (bool): Whether body is HTML
    """
    results = []
    for email in recipients:
        result = send_email(email, subject, body, is_html)
        results.append({'email': email, 'result': result})
    
    return results