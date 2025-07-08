#!/usr/bin/env python3
"""
SMS Service for KenyaNet ISP
Handles SMS notifications using Africa's Talking API
"""

import africastalking
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        # Initialize Africa's Talking
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY', 'your-api-key')
        
        africastalking.initialize(username, api_key)
        self.sms = africastalking.SMS
        
    def send_sms(self, phone_number, message, sender_id="KENYANET"):
        """
        Send SMS to a phone number
        
        Args:
            phone_number (str): Phone number in format +254XXXXXXXXX
            message (str): SMS message content
            sender_id (str): Sender ID for the SMS
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            # Ensure phone number is in correct format
            if not phone_number.startswith('+'):
                if phone_number.startswith('0'):
                    phone_number = '+254' + phone_number[1:]
                elif phone_number.startswith('254'):
                    phone_number = '+' + phone_number
                else:
                    phone_number = '+254' + phone_number
            
            # Send SMS
            response = self.sms.send(message, [phone_number], sender_id)
            
            logger.info(f"SMS sent to {phone_number}: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return {'error': str(e)}
    
    def send_bulk_sms(self, recipients, message, sender_id="KENYANET"):
        """
        Send SMS to multiple recipients
        
        Args:
            recipients (list): List of phone numbers
            message (str): SMS message content
            sender_id (str): Sender ID for the SMS
            
        Returns:
            dict: Response from Africa's Talking API
        """
        try:
            # Format all phone numbers
            formatted_recipients = []
            for phone in recipients:
                if not phone.startswith('+'):
                    if phone.startswith('0'):
                        phone = '+254' + phone[1:]
                    elif phone.startswith('254'):
                        phone = '+' + phone
                    else:
                        phone = '+254' + phone
                formatted_recipients.append(phone)
            
            # Send bulk SMS
            response = self.sms.send(message, formatted_recipients, sender_id)
            
            logger.info(f"Bulk SMS sent to {len(formatted_recipients)} recipients: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to send bulk SMS: {str(e)}")
            return {'error': str(e)}

# Global SMS service instance
sms_service = SMSService()

def send_sms(phone_number, message):
    """Convenience function to send SMS"""
    return sms_service.send_sms(phone_number, message)

def send_bulk_sms(recipients, message):
    """Convenience function to send bulk SMS"""
    return sms_service.send_bulk_sms(recipients, message)

# Pre-defined message templates for common scenarios
SMS_TEMPLATES = {
    'welcome': "Welcome to KenyaNet ISP! Your registration is successful. Our technician will contact you within 24hrs for installation. Call +254700000000 for queries.",
    
    'bill_generated': "KenyaNet ISP: Your {package} bill for {month} is KES {amount}. Due: {due_date}. Pay via M-PESA Paybill 123456, Account: {phone}",
    
    'payment_reminder_3days': "KenyaNet ISP Reminder: Your internet bill of KES {amount} is due in 3 days ({due_date}). Pay via M-PESA Paybill 123456, Account: {phone}",
    
    'payment_reminder_today': "KenyaNet ISP: Your internet bill of KES {amount} is due TODAY. Pay now via M-PESA Paybill 123456, Account: {phone} to avoid service interruption.",
    
    'payment_overdue': "KenyaNet ISP URGENT: Your bill of KES {amount} is {days} days overdue. Pay immediately to avoid suspension. M-PESA Paybill 123456, Account: {phone}",
    
    'service_suspended': "KenyaNet ISP: Your service has been suspended due to {days} days overdue payment of KES {amount}. Pay immediately to restore service. M-PESA Paybill 123456, Account: {phone}",
    
    'service_restored': "KenyaNet ISP: Welcome back! Your service has been restored. Thank you for your payment. Contact us at +254700000000 for any issues.",
    
    'payment_received': "KenyaNet ISP: Payment of KES {amount} received. Receipt: {receipt}. Thank you! Your service remains active.",
    
    'installation_scheduled': "KenyaNet ISP: Your installation is scheduled for {date} between {time}. Our technician will call before arrival. Ensure someone is available.",
    
    'package_changed': "KenyaNet ISP: Your package has been changed to {package} effective {date}. New monthly fee: KES {amount}. Thank you!",
    
    'support_ticket': "KenyaNet ISP: Your support ticket #{ticket_id} has been received. We'll resolve it within 24hrs. Call +254700000000 for urgent issues."
}

def send_templated_sms(phone_number, template_name, **kwargs):
    """
    Send SMS using predefined templates
    
    Args:
        phone_number (str): Phone number to send to
        template_name (str): Name of the template to use
        **kwargs: Variables to substitute in the template
    """
    if template_name not in SMS_TEMPLATES:
        logger.error(f"Template '{template_name}' not found")
        return {'error': f'Template {template_name} not found'}
    
    try:
        message = SMS_TEMPLATES[template_name].format(**kwargs)
        return send_sms(phone_number, message)
    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        return {'error': f'Missing template variable: {e}'}
    except Exception as e:
        logger.error(f"Error sending templated SMS: {e}")
        return {'error': str(e)}

def send_welcome_sms(phone_number, name):
    """Send welcome SMS to new customer"""
    message = f"Welcome to KenyaNet ISP, {name}! Your registration is successful. Our technician will contact you within 24hrs for installation. Call +254700000000 for queries."
    return send_sms(phone_number, message)

def send_bill_notification(phone_number, package_name, month, amount, due_date):
    """Send bill notification SMS"""
    return send_templated_sms(
        phone_number, 
        'bill_generated',
        package=package_name,
        month=month,
        amount=amount,
        due_date=due_date,
        phone=phone_number
    )

def send_payment_reminder(phone_number, amount, due_date, days_until_due=None):
    """Send payment reminder SMS"""
    if days_until_due == 3:
        template = 'payment_reminder_3days'
    elif days_until_due == 0:
        template = 'payment_reminder_today'
    else:
        template = 'payment_overdue'
        
    return send_templated_sms(
        phone_number,
        template,
        amount=amount,
        due_date=due_date,
        phone=phone_number,
        days=abs(days_until_due) if days_until_due is not None else 0
    )

def send_suspension_notice(phone_number, amount, days_overdue):
    """Send service suspension notice"""
    return send_templated_sms(
        phone_number,
        'service_suspended',
        amount=amount,
        days=days_overdue,
        phone=phone_number
    )

def send_restoration_notice(phone_number):
    """Send service restoration notice"""
    return send_templated_sms(phone_number, 'service_restored')

def send_payment_confirmation(phone_number, amount, receipt_number):
    """Send payment confirmation SMS"""
    return send_templated_sms(
        phone_number,
        'payment_received',
        amount=amount,
        receipt=receipt_number
    )

# Emergency broadcast function
def send_emergency_broadcast(message, customer_filter=None):
    """
    Send emergency broadcast to all or filtered customers
    
    Args:
        message (str): Emergency message to send
        customer_filter (dict): Optional filter criteria for customers
    """
    try:
        # This would integrate with the main app to get customer list
        # For now, it's a placeholder
        logger.info(f"Emergency broadcast initiated: {message}")
        
        # In a real implementation, you would:
        # 1. Query database for customers matching filter
        # 2. Extract phone numbers
        # 3. Send bulk SMS
        
        return {'status': 'success', 'message': 'Emergency broadcast initiated'}
        
    except Exception as e:
        logger.error(f"Failed to send emergency broadcast: {e}")
        return {'error': str(e)}