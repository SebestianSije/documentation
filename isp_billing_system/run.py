#!/usr/bin/env python3
"""
KenyaNet ISP Billing System Startup Script
Initializes database and starts the Flask application
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Package, Subscription, Bill

def create_sample_data():
    """Create sample data for testing and demonstration"""
    print("Creating sample data...")
    
    # Create sample customers
    sample_customers = [
        {
            'name': 'John Kamau',
            'phone_number': '+254712345678',
            'email': 'john.kamau@email.com',
            'id_number': '12345678',
            'physical_address': 'Kileleshwa Estate, House No. 45, Near Shell Petrol Station',
            'installation_location': 'Ground floor living room',
            'gps_coordinates': '-1.2921, 36.8219'
        },
        {
            'name': 'Mary Wanjiku',
            'phone_number': '+254723456789',
            'email': 'mary.wanjiku@email.com',
            'id_number': '23456789',
            'physical_address': 'Westlands, ABC Apartments, Flat 204',
            'installation_location': 'Master bedroom',
            'gps_coordinates': '-1.2634, 36.8047'
        },
        {
            'name': 'Peter Ochieng',
            'phone_number': '+254734567890',
            'email': 'peter.ochieng@email.com',
            'id_number': '34567890',
            'physical_address': 'Karen Estate, Villa 12, Off Karen Road',
            'installation_location': 'Study room upstairs',
            'gps_coordinates': '-1.3197, 36.7084'
        }
    ]
    
    for customer_data in sample_customers:
        existing_customer = User.query.filter_by(phone_number=customer_data['phone_number']).first()
        if not existing_customer:
            customer = User(**customer_data)
            db.session.add(customer)
    
    db.session.commit()
    
    # Create sample subscriptions
    print("Creating sample subscriptions...")
    customers = User.query.filter_by(is_admin=False).all()
    packages = Package.query.all()
    
    for i, customer in enumerate(customers[:3]):  # First 3 customers
        if not customer.subscriptions:
            package = packages[i % len(packages)]  # Distribute packages
            subscription = Subscription(
                user_id=customer.id,
                package_id=package.id,
                start_date=datetime.utcnow() - timedelta(days=30),
                is_active=True
            )
            db.session.add(subscription)
    
    db.session.commit()
    
    # Create sample bills
    print("Creating sample bills...")
    active_subscriptions = Subscription.query.filter_by(is_active=True).all()
    
    for subscription in active_subscriptions:
        # Current month bill
        current_month = datetime.now().replace(day=1)
        next_month = (current_month + timedelta(days=32)).replace(day=1)
        
        existing_bill = Bill.query.filter(
            Bill.subscription_id == subscription.id,
            Bill.bill_period_start == current_month
        ).first()
        
        if not existing_bill:
            bill = Bill(
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                amount=subscription.package.price_monthly,
                due_date=current_month + timedelta(days=15),
                bill_period_start=current_month,
                bill_period_end=next_month - timedelta(days=1),
                status='pending'
            )
            db.session.add(bill)
    
    db.session.commit()
    print("Sample data created successfully!")

def initialize_database():
    """Initialize database with default data"""
    print("Initializing database...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created.")
        
        # Create default admin user if not exists
        admin = User.query.filter_by(phone_number='+254700000000').first()
        if not admin:
            print("Creating default admin user...")
            admin = User(
                phone_number='+254700000000',
                email='admin@kenyanet.co.ke',
                name='System Administrator',
                id_number='00000000',
                physical_address='KenyaNet ISP Office, Nairobi',
                installation_location='Main Office',
                is_admin=True,
                is_active=True
            )
            db.session.add(admin)
            print("Admin user created: +254700000000")
        
        # Create default packages if not exist
        if Package.query.count() == 0:
            print("Creating default internet packages...")
            packages = [
                Package(
                    name='Basic 10Mbps',
                    speed_mbps=10,
                    price_monthly=Decimal('2500.00'),
                    data_cap_gb=None,
                    fair_usage_policy='Fair usage applies during peak hours (6PM-12AM)',
                    is_active=True
                ),
                Package(
                    name='Standard 20Mbps',
                    speed_mbps=20,
                    price_monthly=Decimal('4000.00'),
                    data_cap_gb=None,
                    fair_usage_policy='Fair usage applies during peak hours (6PM-12AM)',
                    is_active=True
                ),
                Package(
                    name='Premium 50Mbps',
                    speed_mbps=50,
                    price_monthly=Decimal('7500.00'),
                    data_cap_gb=None,
                    fair_usage_policy='No fair usage policy - unlimited speeds',
                    is_active=True
                ),
                Package(
                    name='Business 100Mbps',
                    speed_mbps=100,
                    price_monthly=Decimal('12000.00'),
                    data_cap_gb=None,
                    fair_usage_policy='No fair usage policy - unlimited speeds with priority support',
                    is_active=True
                )
            ]
            
            for package in packages:
                db.session.add(package)
            
            print("Default packages created:")
            for package in packages:
                print(f"  - {package.name}: {package.speed_mbps}Mbps - KES {package.price_monthly}/month")
        
        db.session.commit()
        
        # Create sample data for demonstration
        create_sample_data()
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print("\nDEFAULT LOGIN CREDENTIALS:")
        print("Admin Phone: +254700000000")
        print("\nSAMPLE CUSTOMER ACCOUNTS:")
        customers = User.query.filter_by(is_admin=False).all()
        for customer in customers:
            print(f"- {customer.name}: {customer.phone_number}")
        
        print("\nAVAILABLE PACKAGES:")
        packages = Package.query.all()
        for package in packages:
            print(f"- {package.name}: {package.speed_mbps}Mbps - KES {package.price_monthly}/month")
        print("="*60)

def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment configuration...")
    
    required_vars = [
        'MPESA_CONSUMER_KEY',
        'MPESA_CONSUMER_SECRET',
        'AFRICASTALKING_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == 'your-api-key':
            missing_vars.append(var)
    
    if missing_vars:
        print("\n⚠️  WARNING: Missing or default configuration detected!")
        print("The following environment variables need to be configured:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nCreate a .env file with your actual API credentials for full functionality.")
        print("For testing, you can continue with demo mode.\n")
    else:
        print("✅ Environment configuration looks good!")

def print_startup_info():
    """Print startup information and instructions"""
    print("\n" + "="*60)
    print("🚀 KENYANET ISP BILLING SYSTEM")
    print("="*60)
    print("\n📋 SYSTEM FEATURES:")
    print("✅ Customer Registration & Management")
    print("✅ Automated Billing & Invoicing")
    print("✅ M-PESA Payment Integration")
    print("✅ SMS & Email Notifications")
    print("✅ Admin Dashboard & Reports")
    print("✅ Customer Self-Service Portal")
    print("✅ Package Management")
    print("✅ Auto Suspension & Reconnection")
    
    print("\n🌐 ACCESS URLS:")
    print("- Main Website: http://localhost:5000")
    print("- Customer Login: http://localhost:5000/login")
    print("- Admin Dashboard: http://localhost:5000/admin/dashboard")
    print("- Customer Registration: http://localhost:5000/register")
    
    print("\n📱 PAYMENT INTEGRATION:")
    print("- M-PESA Paybill: 123456 (Demo)")
    print("- Account Number: Customer phone number")
    print("- SMS Gateway: Africa's Talking")
    
    print("\n🔧 FOR PRODUCTION:")
    print("1. Configure .env file with real API credentials")
    print("2. Set up proper database (PostgreSQL/MySQL)")
    print("3. Configure web server (Nginx + Gunicorn)")
    print("4. Set up SSL certificate")
    print("5. Configure automated billing cron jobs")
    
    print("\n📞 SUPPORT:")
    print("- Documentation: README.md")
    print("- Issues: GitHub Issues")
    print("- Email: support@kenyanet.co.ke")
    print("="*60)

def main():
    """Main startup function"""
    print("Starting KenyaNet ISP Billing System...")
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Check environment
    check_environment()
    
    # Initialize database
    if not os.path.exists('isp_billing.db') or '--init-db' in sys.argv:
        initialize_database()
    else:
        print("Database exists. Use --init-db to reinitialize.")
    
    # Print startup information
    print_startup_info()
    
    # Start the application
    if '--no-run' not in sys.argv:
        print(f"\n🚀 Starting server on http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("-" * 60)
        
        try:
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n\nServer stopped. Thank you for using KenyaNet ISP Billing System!")
    else:
        print("\nDatabase initialized. Use 'python app.py' to start the server.")

if __name__ == "__main__":
    main()