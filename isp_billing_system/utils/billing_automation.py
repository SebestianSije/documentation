#!/usr/bin/env python3
"""
ISP Billing Automation Script
Handles automated billing cycles, reminders, and service suspension for KenyaNet ISP
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Package, Subscription, Bill, Payment
from utils.sms_service import send_sms
from utils.email_service import send_email

def generate_monthly_bills():
    """Generate bills for all active subscriptions"""
    print(f"[{datetime.now()}] Starting monthly bill generation...")
    
    with app.app_context():
        # Get all active subscriptions
        active_subscriptions = Subscription.query.filter_by(is_active=True).all()
        
        current_month = datetime.now().replace(day=1)
        next_month = (current_month + timedelta(days=32)).replace(day=1)
        
        bills_created = 0
        
        for subscription in active_subscriptions:
            # Check if bill already exists for this month
            existing_bill = Bill.query.filter(
                Bill.subscription_id == subscription.id,
                Bill.bill_period_start == current_month
            ).first()
            
            if existing_bill:
                continue
            
            # Create new bill
            bill = Bill(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=subscription.package.price_monthly,
                due_date=current_month + timedelta(days=15),  # Due 15th of month
                bill_period_start=current_month,
                bill_period_end=next_month - timedelta(days=1),
                status='pending'
            )
            
            db.session.add(bill)
            bills_created += 1
            
            # Send bill notification
            user = subscription.user
            message = f"KenyaNet ISP: Your {subscription.package.name} bill for {current_month.strftime('%B %Y')} is KES {bill.amount}. Due: {bill.due_date.strftime('%d %b')}. Pay via M-PESA Paybill 123456, Account: {user.phone_number}"
            
            send_sms(user.phone_number, message)
            
            if user.email:
                send_email(
                    user.email,
                    f"KenyaNet ISP Bill - {current_month.strftime('%B %Y')}",
                    f"Dear {user.name},\n\nYour internet bill for {current_month.strftime('%B %Y')} is ready.\n\nPackage: {subscription.package.name}\nAmount: KES {bill.amount}\nDue Date: {bill.due_date.strftime('%d %B %Y')}\n\nPay via M-PESA Paybill 123456 using your phone number as account number.\n\nThank you,\nKenyaNet ISP Team"
                )
        
        db.session.commit()
        print(f"[{datetime.now()}] Generated {bills_created} bills")

def send_payment_reminders():
    """Send payment reminders for upcoming and overdue bills"""
    print(f"[{datetime.now()}] Sending payment reminders...")
    
    with app.app_context():
        today = datetime.now().date()
        
        # Get bills due in 3 days
        upcoming_bills = Bill.query.filter(
            Bill.status == 'pending',
            Bill.due_date.cast(db.Date) == today + timedelta(days=3)
        ).all()
        
        # Get bills due today
        due_today_bills = Bill.query.filter(
            Bill.status == 'pending',
            Bill.due_date.cast(db.Date) == today
        ).all()
        
        # Get overdue bills (2 days past due)
        overdue_bills = Bill.query.filter(
            Bill.status == 'pending',
            Bill.due_date.cast(db.Date) == today - timedelta(days=2)
        ).all()
        
        reminders_sent = 0
        
        # Send upcoming payment reminders
        for bill in upcoming_bills:
            user = bill.user
            message = f"KenyaNet ISP Reminder: Your internet bill of KES {bill.amount} is due in 3 days ({bill.due_date.strftime('%d %b')}). Pay via M-PESA Paybill 123456, Account: {user.phone_number}"
            send_sms(user.phone_number, message)
            reminders_sent += 1
        
        # Send due today reminders
        for bill in due_today_bills:
            user = bill.user
            message = f"KenyaNet ISP: Your internet bill of KES {bill.amount} is due TODAY. Pay now via M-PESA Paybill 123456, Account: {user.phone_number} to avoid service interruption."
            send_sms(user.phone_number, message)
            reminders_sent += 1
        
        # Send overdue reminders
        for bill in overdue_bills:
            user = bill.user
            days_overdue = (today - bill.due_date.date()).days
            message = f"KenyaNet ISP URGENT: Your bill of KES {bill.amount} is {days_overdue} days overdue. Pay immediately to avoid suspension. M-PESA Paybill 123456, Account: {user.phone_number}"
            send_sms(user.phone_number, message)
            reminders_sent += 1
        
        print(f"[{datetime.now()}] Sent {reminders_sent} payment reminders")

def auto_suspend_overdue_accounts():
    """Automatically suspend accounts with bills overdue by more than 5 days"""
    print(f"[{datetime.now()}] Checking for accounts to suspend...")
    
    with app.app_context():
        today = datetime.now().date()
        suspension_date = today - timedelta(days=5)
        
        # Get bills overdue by more than 5 days
        overdue_bills = Bill.query.filter(
            Bill.status == 'pending',
            Bill.due_date.cast(db.Date) <= suspension_date
        ).all()
        
        suspended_count = 0
        
        for bill in overdue_bills:
            user = bill.user
            
            # Skip if already suspended
            if not user.is_active:
                continue
            
            # Suspend the user
            user.is_active = False
            db.session.add(user)
            
            # Send suspension notification
            days_overdue = (today - bill.due_date.date()).days
            message = f"KenyaNet ISP: Your service has been suspended due to {days_overdue} days overdue payment of KES {bill.amount}. Pay immediately to restore service. M-PESA Paybill 123456, Account: {user.phone_number}"
            send_sms(user.phone_number, message)
            
            if user.email:
                send_email(
                    user.email,
                    "KenyaNet ISP - Service Suspended",
                    f"Dear {user.name},\n\nYour internet service has been suspended due to overdue payment.\n\nOverdue Amount: KES {bill.amount}\nDays Overdue: {days_overdue}\n\nTo restore your service immediately, please pay via M-PESA Paybill 123456 using your phone number as account number.\n\nFor assistance, call +254 700 000 000\n\nKenyaNet ISP Team"
                )
            
            suspended_count += 1
        
        db.session.commit()
        print(f"[{datetime.now()}] Suspended {suspended_count} accounts")

def auto_reactivate_paid_accounts():
    """Automatically reactivate accounts that have made recent payments"""
    print(f"[{datetime.now()}] Checking for accounts to reactivate...")
    
    with app.app_context():
        # Get users who are suspended but have recent payments
        suspended_users = User.query.filter_by(is_active=False, is_admin=False).all()
        
        reactivated_count = 0
        
        for user in suspended_users:
            # Check for recent payments (last 24 hours)
            recent_payment = Payment.query.filter(
                Payment.user_id == user.id,
                Payment.payment_date >= datetime.now() - timedelta(hours=24)
            ).first()
            
            if recent_payment:
                # Check if all bills are now paid or within grace period
                pending_bills = Bill.query.filter_by(
                    user_id=user.id,
                    status='pending'
                ).all()
                
                # Simple logic: reactivate if there are no severely overdue bills
                should_reactivate = True
                for bill in pending_bills:
                    days_overdue = (datetime.now().date() - bill.due_date.date()).days
                    if days_overdue > 10:  # Still severely overdue
                        should_reactivate = False
                        break
                
                if should_reactivate:
                    user.is_active = True
                    db.session.add(user)
                    
                    message = f"KenyaNet ISP: Welcome back! Your service has been restored. Thank you for your payment. Contact us at +254 700 000 000 for any issues."
                    send_sms(user.phone_number, message)
                    
                    if user.email:
                        send_email(
                            user.email,
                            "KenyaNet ISP - Service Restored",
                            f"Dear {user.name},\n\nGreat news! Your internet service has been restored.\n\nThank you for your payment. Your connection should be active within the next few minutes.\n\nFor any technical issues, please contact our support team at +254 700 000 000.\n\nWelcome back!\nKenyaNet ISP Team"
                        )
                    
                    reactivated_count += 1
        
        db.session.commit()
        print(f"[{datetime.now()}] Reactivated {reactivated_count} accounts")

def process_bill_payments():
    """Process and match payments to bills"""
    print(f"[{datetime.now()}] Processing bill payments...")
    
    with app.app_context():
        # This would typically integrate with M-PESA API to fetch recent transactions
        # For now, we'll just mark bills as paid if there are corresponding payments
        
        payments_processed = 0
        
        # Get all unprocessed payments (simplified logic)
        unprocessed_payments = Payment.query.filter_by(status='completed').all()
        
        for payment in unprocessed_payments:
            # Find matching pending bill
            pending_bill = Bill.query.filter_by(
                user_id=payment.user_id,
                status='pending'
            ).order_by(Bill.due_date.asc()).first()
            
            if pending_bill and payment.amount >= pending_bill.amount:
                pending_bill.status = 'paid'
                db.session.add(pending_bill)
                payments_processed += 1
        
        db.session.commit()
        print(f"[{datetime.now()}] Processed {payments_processed} bill payments")

def generate_reports():
    """Generate daily operational reports"""
    print(f"[{datetime.now()}] Generating daily reports...")
    
    with app.app_context():
        today = datetime.now().date()
        
        # Basic statistics
        total_customers = User.query.filter_by(is_admin=False).count()
        active_customers = User.query.filter_by(is_admin=False, is_active=True).count()
        suspended_customers = User.query.filter_by(is_admin=False, is_active=False).count()
        
        pending_bills = Bill.query.filter_by(status='pending').count()
        overdue_bills = Bill.query.filter(
            Bill.status == 'pending',
            Bill.due_date.cast(db.Date) < today
        ).count()
        
        total_revenue_today = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.payment_date.cast(db.Date) == today
        ).scalar() or 0
        
        # Create report
        report = f"""
KenyaNet ISP Daily Report - {today.strftime('%d %B %Y')}
========================================================

Customer Statistics:
- Total Customers: {total_customers}
- Active Customers: {active_customers}
- Suspended Customers: {suspended_customers}
- Active Rate: {(active_customers/total_customers*100) if total_customers > 0 else 0:.1f}%

Billing Statistics:
- Pending Bills: {pending_bills}
- Overdue Bills: {overdue_bills}
- Revenue Today: KES {total_revenue_today:,.2f}

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Save report to file
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_file = os.path.join(reports_dir, f'daily_report_{today.strftime("%Y%m%d")}.txt')
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"[{datetime.now()}] Report saved to {report_file}")

def main():
    """Main automation function"""
    print(f"[{datetime.now()}] Starting ISP billing automation...")
    
    try:
        # Run all automation tasks
        generate_monthly_bills()
        send_payment_reminders()
        auto_suspend_overdue_accounts()
        auto_reactivate_paid_accounts()
        process_bill_payments()
        generate_reports()
        
        print(f"[{datetime.now()}] Billing automation completed successfully")
        
    except Exception as e:
        print(f"[{datetime.now()}] Error in billing automation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()