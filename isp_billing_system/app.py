from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import requests
import base64
import json
from decimal import Decimal
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///isp_billing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for Kenya-specific settings
app.config['CURRENCY'] = 'KES'
app.config['COUNTRY_CODE'] = '+254'
app.config['TIMEZONE'] = 'Africa/Nairobi'

# M-PESA Daraja API Configuration
app.config['MPESA_CONSUMER_KEY'] = 'your-consumer-key'
app.config['MPESA_CONSUMER_SECRET'] = 'your-consumer-secret'
app.config['MPESA_BUSINESS_SHORTCODE'] = 'your-shortcode'
app.config['MPESA_PASSKEY'] = 'your-passkey'
app.config['MPESA_CALLBACK_URL'] = 'https://yourdomain.com/mpesa/callback'

# SMS Configuration (Africa's Talking)
app.config['AFRICASTALKING_USERNAME'] = 'sandbox'  # Use 'sandbox' for testing
app.config['AFRICASTALKING_API_KEY'] = 'your-api-key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(20), unique=True, nullable=False)
    kra_pin = db.Column(db.String(20), nullable=True)
    physical_address = db.Column(db.Text, nullable=False)
    installation_location = db.Column(db.Text, nullable=False)
    gps_coordinates = db.Column(db.String(100), nullable=True)
    referral_code = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    speed_mbps = db.Column(db.Integer, nullable=False)
    price_monthly = db.Column(db.Numeric(10, 2), nullable=False)
    data_cap_gb = db.Column(db.Integer, nullable=True)  # None for unlimited
    fair_usage_policy = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='subscriptions')
    package = db.relationship('Package', backref='subscriptions')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    bill_period_start = db.Column(db.DateTime, nullable=False)
    bill_period_end = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='bills')
    subscription = db.relationship('Subscription', backref='bills')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # mpesa, cash, bank_transfer
    transaction_id = db.Column(db.String(100), nullable=True)
    mpesa_receipt_number = db.Column(db.String(50), nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')
    
    bill = db.relationship('Bill', backref='payments')
    user = db.relationship('User', backref='payments')

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # slow_internet, no_connection, billing, other
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    assigned_to = db.Column(db.String(100), nullable=True)
    resolution = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='support_tickets')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility Functions
def format_kenyan_phone(phone):
    """Format phone number to Kenyan standard"""
    phone = phone.replace(' ', '').replace('-', '')
    if phone.startswith('0'):
        phone = '+254' + phone[1:]
    elif phone.startswith('254'):
        phone = '+' + phone
    elif not phone.startswith('+254'):
        phone = '+254' + phone
    return phone

def send_sms(phone_number, message):
    """Send SMS using Africa's Talking API"""
    try:
        # This would integrate with Africa's Talking API
        # For now, we'll just log the message
        print(f"SMS to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"SMS Error: {e}")
        return False

def generate_mpesa_access_token():
    """Generate M-PESA access token"""
    try:
        consumer_key = app.config['MPESA_CONSUMER_KEY']
        consumer_secret = app.config['MPESA_CONSUMER_SECRET']
        
        api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        r = requests.get(api_url, auth=(consumer_key, consumer_secret))
        json_response = r.json()
        access_token = json_response['access_token']
        return access_token
    except Exception as e:
        print(f"M-PESA Token Error: {e}")
        return None

def initiate_mpesa_payment(phone_number, amount, account_reference, transaction_desc):
    """Initiate M-PESA STK push"""
    try:
        access_token = generate_mpesa_access_token()
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        business_shortcode = app.config['MPESA_BUSINESS_SHORTCODE']
        passkey = app.config['MPESA_PASSKEY']
        
        password = base64.b64encode(f"{business_shortcode}{passkey}{timestamp}".encode()).decode('utf-8')
        
        request_data = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": app.config['MPESA_CALLBACK_URL'],
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        response = requests.post(api_url, json=request_data, headers=headers)
        return response.json()
    except Exception as e:
        print(f"M-PESA Payment Error: {e}")
        return {'error': str(e)}

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_portal'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        # Format phone number
        phone_number = format_kenyan_phone(data['phone_number'])
        
        # Check if user already exists
        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            flash('Phone number already registered!')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            phone_number=phone_number,
            email=data.get('email'),
            name=data['name'],
            id_number=data['id_number'],
            kra_pin=data.get('kra_pin'),
            physical_address=data['physical_address'],
            installation_location=data['installation_location'],
            gps_coordinates=data.get('gps_coordinates'),
            referral_code=data.get('referral_code')
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = format_kenyan_phone(request.form['phone_number'])
        
        user = User.query.filter_by(phone_number=phone_number).first()
        if user and user.is_active:
            # In a real system, you'd send OTP here
            # For demo purposes, we'll just log them in
            login_user(user)
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer_portal'))
        else:
            flash('Invalid phone number or account inactive!')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/customer/portal')
@login_required
def customer_portal():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Get current subscription
    current_subscription = Subscription.query.filter_by(
        user_id=current_user.id, is_active=True
    ).first()
    
    # Get pending bills
    pending_bills = Bill.query.filter_by(
        user_id=current_user.id, status='pending'
    ).order_by(Bill.due_date.asc()).all()
    
    # Get recent payments
    recent_payments = Payment.query.filter_by(
        user_id=current_user.id
    ).order_by(Payment.payment_date.desc()).limit(5).all()
    
    return render_template('customer_portal.html', 
                         subscription=current_subscription,
                         pending_bills=pending_bills,
                         recent_payments=recent_payments)

@app.route('/customer/packages')
@login_required
def view_packages():
    packages = Package.query.filter_by(is_active=True).all()
    current_subscription = Subscription.query.filter_by(
        user_id=current_user.id, is_active=True
    ).first()
    
    return render_template('packages.html', 
                         packages=packages,
                         current_subscription=current_subscription)

@app.route('/customer/subscribe/<int:package_id>')
@login_required
def subscribe_package(package_id):
    package = Package.query.get_or_404(package_id)
    
    # Deactivate current subscription
    current_subscription = Subscription.query.filter_by(
        user_id=current_user.id, is_active=True
    ).first()
    
    if current_subscription:
        current_subscription.is_active = False
        current_subscription.end_date = datetime.utcnow()
    
    # Create new subscription
    new_subscription = Subscription(
        user_id=current_user.id,
        package_id=package_id,
        start_date=datetime.utcnow(),
        is_active=True
    )
    
    db.session.add(new_subscription)
    db.session.commit()
    
    flash(f'Successfully subscribed to {package.name}!')
    return redirect(url_for('customer_portal'))

@app.route('/customer/pay/<int:bill_id>')
@login_required
def pay_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    
    if bill.user_id != current_user.id:
        flash('Unauthorized access!')
        return redirect(url_for('customer_portal'))
    
    # Initiate M-PESA payment
    result = initiate_mpesa_payment(
        phone_number=current_user.phone_number,
        amount=bill.amount,
        account_reference=f"BILL-{bill.id}",
        transaction_desc=f"Internet Bill Payment"
    )
    
    if 'error' in result:
        flash(f'Payment initiation failed: {result["error"]}')
    else:
        flash('Payment request sent to your phone. Please enter your M-PESA PIN.')
    
    return redirect(url_for('customer_portal'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('customer_portal'))
    
    # Dashboard statistics
    total_customers = User.query.filter_by(is_admin=False).count()
    active_customers = User.query.filter_by(is_admin=False, is_active=True).count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    pending_bills = Bill.query.filter_by(status='pending').count()
    
    # Recent activity
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(10).all()
    overdue_bills = Bill.query.filter(
        Bill.status == 'pending',
        Bill.due_date < datetime.utcnow()
    ).all()
    
    return render_template('admin_dashboard.html',
                         total_customers=total_customers,
                         active_customers=active_customers,
                         total_revenue=total_revenue,
                         pending_bills=pending_bills,
                         recent_payments=recent_payments,
                         overdue_bills=overdue_bills)

@app.route('/admin/customers')
@login_required
def admin_customers():
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('customer_portal'))
    
    customers = User.query.filter_by(is_admin=False).all()
    return render_template('admin_customers.html', customers=customers)

@app.route('/admin/suspend/<int:user_id>')
@login_required
def suspend_customer(user_id):
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('customer_portal'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    
    # Send SMS notification
    send_sms(user.phone_number, 
            "Your internet service has been suspended due to overdue payment. Please contact us to reactivate.")
    
    flash(f'Customer {user.name} suspended successfully!')
    return redirect(url_for('admin_customers'))

@app.route('/admin/activate/<int:user_id>')
@login_required
def activate_customer(user_id):
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('customer_portal'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    
    # Send SMS notification
    send_sms(user.phone_number, 
            "Your internet service has been reactivated. Welcome back!")
    
    flash(f'Customer {user.name} activated successfully!')
    return redirect(url_for('admin_customers'))

# API Endpoints
@app.route('/api/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-PESA payment callbacks"""
    try:
        data = request.get_json()
        
        # Process the callback data
        if data.get('Body', {}).get('stkCallback', {}).get('ResultCode') == 0:
            # Payment successful
            callback_metadata = data['Body']['stkCallback']['CallbackMetadata']['Item']
            
            amount = None
            receipt_number = None
            transaction_id = None
            
            for item in callback_metadata:
                if item['Name'] == 'Amount':
                    amount = item['Value']
                elif item['Name'] == 'MpesaReceiptNumber':
                    receipt_number = item['Value']
                elif item['Name'] == 'TransactionDate':
                    transaction_id = item['Value']
            
            # Find the bill and create payment record
            # This would require parsing the account reference from the callback
            # For now, we'll just log the successful payment
            print(f"Payment successful: Amount={amount}, Receipt={receipt_number}")
            
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Callback Error: {e}")
        return jsonify({'status': 'error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(phone_number='+254700000000').first()
        if not admin:
            admin = User(
                phone_number='+254700000000',
                email='admin@isp.co.ke',
                name='System Administrator',
                id_number='00000000',
                physical_address='ISP Office',
                installation_location='ISP Office',
                is_admin=True
            )
            db.session.add(admin)
        
        # Create default packages if not exist
        if Package.query.count() == 0:
            packages = [
                Package(name='Basic 10Mbps', speed_mbps=10, price_monthly=Decimal('2500')),
                Package(name='Standard 20Mbps', speed_mbps=20, price_monthly=Decimal('4000')),
                Package(name='Premium 50Mbps', speed_mbps=50, price_monthly=Decimal('7500')),
                Package(name='Business 100Mbps', speed_mbps=100, price_monthly=Decimal('12000'))
            ]
            for package in packages:
                db.session.add(package)
        
        db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)