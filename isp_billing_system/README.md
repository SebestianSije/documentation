# KenyaNet ISP Billing System

A comprehensive billing and customer management system designed specifically for WiFi Internet Service Providers (ISPs) in Kenya. This system handles customer registration, automated billing, M-PESA payments, SMS notifications, and administrative management.

## 🌟 Features

### 📦 1. Customer Registration & Onboarding
- ✅ Complete customer registration with Kenya-specific fields
- ✅ National ID number validation
- ✅ Phone number formatting (+254 format)
- ✅ Physical address with estate/building details
- ✅ GPS coordinates support
- ✅ KRA PIN for business customers
- ✅ Referral code system

### 💳 2. M-PESA Integration
- ✅ Safaricom Daraja API integration
- ✅ STK Push for seamless payments
- ✅ Automatic payment callbacks
- ✅ Real-time payment processing
- ✅ Receipt generation and matching

### 📱 3. SMS Notifications
- ✅ Africa's Talking API integration
- ✅ Automated billing reminders
- ✅ Payment confirmations
- ✅ Service suspension/restoration alerts
- ✅ Welcome messages
- ✅ Custom SMS templates

### 📧 4. Email Notifications
- ✅ Professional email templates
- ✅ Bill notifications with PDF attachments
- ✅ Payment confirmations
- ✅ Service alerts
- ✅ Welcome emails

### 📊 5. Package Management
- ✅ Multiple internet packages (10Mbps, 20Mbps, 50Mbps, 100Mbps)
- ✅ Speed and pricing configuration
- ✅ Data cap options
- ✅ Fair usage policies
- ✅ Package upgrade/downgrade with pro-rated billing

### 🔄 6. Automated Billing
- ✅ Monthly recurring billing
- ✅ Automatic bill generation
- ✅ Payment reminder system (3 days, due date, overdue)
- ✅ Auto-suspension after 5 days overdue
- ✅ Auto-reconnection on payment

### 👨‍💼 7. Admin Dashboard
- ✅ Real-time statistics and analytics
- ✅ Customer management
- ✅ Payment tracking
- ✅ Overdue account monitoring
- ✅ Bulk SMS capabilities
- ✅ Financial reporting

### 🏠 8. Customer Self-Service Portal
- ✅ Mobile-friendly web interface
- ✅ View and pay bills online
- ✅ Package management
- ✅ Payment history
- ✅ Support ticket system
- ✅ Account information updates

### 🔐 9. Security & Compliance
- ✅ Kenya Data Protection Act compliance
- ✅ Secure payment processing
- ✅ Data encryption
- ✅ Admin access controls
- ✅ Session management

## 🛠️ Technology Stack

- **Backend:** Python Flask
- **Database:** SQLite (development), PostgreSQL/MySQL (production)
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Payment:** M-PESA Daraja API
- **SMS:** Africa's Talking API
- **Email:** SMTP (Gmail/custom)
- **Authentication:** Flask-Login
- **Automation:** APScheduler

## 📋 Requirements

- Python 3.8+
- Flask 2.3+
- SQLite/PostgreSQL/MySQL
- M-PESA Developer Account
- Africa's Talking Account
- Email Account (Gmail/custom SMTP)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/kenyanet-isp-billing.git
cd kenyanet-isp-billing/isp_billing_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///isp_billing.db

# M-PESA Configuration
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_BUSINESS_SHORTCODE=your-business-shortcode
MPESA_PASSKEY=your-mpesa-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback

# SMS Configuration (Africa's Talking)
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=billing@kenyanet.co.ke
EMAIL_PASSWORD=your-app-password
```

### 3. Database Setup

```bash
# Initialize the database
python app.py
```

This will create the SQLite database and populate it with:
- Default admin user (Phone: +254700000000)
- Sample internet packages
- Initial configuration

### 4. Run the Application

```bash
# Development server
python app.py

# Production server (with Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Visit `http://localhost:5000` to access the application.

## 👤 Default Login Credentials

### Admin Access
- **Phone:** +254700000000
- **Password:** Not required (phone-based login)

### Test Customer
After registration, customers log in using their registered phone numbers.

## 🔧 Configuration Guide

### M-PESA Setup

1. Register for M-PESA Developer Account at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create a new app and get your credentials
3. Configure your callback URL
4. Update the `.env` file with your credentials

### SMS Setup

1. Register at [africastalking.com](https://africastalking.com)
2. Get your API key and username
3. For production, verify your sender ID
4. Update the `.env` file

### Email Setup

1. For Gmail: Enable 2FA and create an App Password
2. For custom SMTP: Get your server details
3. Update the `.env` file with credentials

## 🤖 Automation Setup

### Billing Automation

The system includes automated billing scripts that should be run regularly:

```bash
# Run billing automation (daily)
python utils/billing_automation.py

# Set up cron job (Linux/Mac)
crontab -e
# Add: 0 6 * * * /path/to/python /path/to/utils/billing_automation.py

# Windows Task Scheduler
# Create a daily task to run the billing script
```

### Automation Features

- **Daily:** Payment reminders, account suspensions, reactivations
- **Monthly:** Bill generation for all active customers
- **Real-time:** Payment processing and receipt matching

## 📱 API Endpoints

### Customer APIs
- `POST /register` - Customer registration
- `POST /login` - Customer login
- `GET /customer/portal` - Customer dashboard
- `GET /customer/packages` - View packages
- `POST /customer/subscribe/<package_id>` - Subscribe to package
- `GET /customer/pay/<bill_id>` - Initiate M-PESA payment

### Admin APIs
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/customers` - Customer management
- `POST /admin/suspend/<user_id>` - Suspend customer
- `POST /admin/activate/<user_id>` - Activate customer

### Payment APIs
- `POST /api/mpesa/callback` - M-PESA payment callback
- `POST /api/payment/manual` - Manual payment entry

## 🏢 Business Logic

### Billing Cycle
1. **Day 1:** Bills generated for all active customers
2. **Day 12:** First reminder (3 days before due)
3. **Day 15:** Due date reminder
4. **Day 17:** Overdue reminder (2 days past due)
5. **Day 20:** Service suspension (5 days past due)

### Payment Processing
1. Customer initiates M-PESA payment
2. STK Push sent to customer's phone
3. Customer enters M-PESA PIN
4. Payment callback received
5. Bill marked as paid
6. Service restored (if suspended)

### Package Management
- Customers can upgrade/downgrade anytime
- Pro-rated billing for mid-cycle changes
- Immediate speed changes after package change

## 📊 Reports & Analytics

### Available Reports
- Daily revenue reports
- Customer statistics
- Overdue accounts
- Package popularity
- Payment method breakdown

### Export Options
- CSV export for customer data
- PDF invoices and receipts
- Excel reports for accounting

## 🔒 Security Features

### Data Protection
- Password hashing for admin accounts
- Session management
- CSRF protection
- SQL injection prevention
- XSS protection

### Kenya Data Protection Act Compliance
- Customer consent management
- Data access/correction rights
- Secure data storage
- Privacy policy implementation

## 🚀 Deployment

### Production Deployment

1. **Server Setup (Ubuntu 20.04+)**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Clone and setup application
git clone your-repo
cd isp_billing_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Database Setup (PostgreSQL)**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql
CREATE DATABASE isp_billing;
CREATE USER isp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE isp_billing TO isp_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://isp_user:your_password@localhost/isp_billing
```

3. **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Supervisor Configuration**
```ini
[program:isp_billing]
command=/path/to/venv/bin/gunicorn -w 4 -b localhost:5000 app:app
directory=/path/to/isp_billing_system
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/isp_billing.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](docs/api.md)
- [User Manual](docs/user_manual.md)
- [Admin Guide](docs/admin_guide.md)

### Contact
- **Email:** support@kenyanet.co.ke
- **Phone:** +254 700 000 000
- **WhatsApp:** +254 700 000 001

### Common Issues

**Q: M-PESA payments not working?**
A: Check your Daraja API credentials and callback URL configuration.

**Q: SMS not sending?**
A: Verify your Africa's Talking API key and sender ID approval.

**Q: Database connection errors?**
A: Check your DATABASE_URL configuration and database server status.

**Q: Bills not generating automatically?**
A: Ensure the billing automation script is running via cron job.

## 🔮 Roadmap

### Version 2.0 (Planned)
- [ ] Mobile app (Android/iOS)
- [ ] Router integration (MikroTik/Ubiquiti)
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Advanced reporting

### Version 2.1 (Planned)
- [ ] WhatsApp API integration
- [ ] Voice call reminders
- [ ] Customer loyalty program
- [ ] Reseller management
- [ ] Advanced fraud detection

## 🏆 Acknowledgments

- [Safaricom](https://developer.safaricom.co.ke) for M-PESA API
- [Africa's Talking](https://africastalking.com) for SMS services
- [Bootstrap](https://getbootstrap.com) for UI framework
- [Flask](https://flask.palletsprojects.com) for web framework

---

**Built with ❤️ for Kenyan ISPs**

For more information, visit our [website](https://kenyanet.co.ke) or contact our support team.