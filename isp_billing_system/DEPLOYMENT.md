# 🚀 ISP Billing System Deployment Guide

## 📋 Deployment Options

### 🎯 **Recommended: VPS Deployment (Automated)**
**Best for:** Small to medium ISPs (100-5000 customers)
**Cost:** $10-50/month
**Time:** 15-30 minutes

### 🌩️ **Cloud Deployment**
**Best for:** Large ISPs (5000+ customers)
**Cost:** $50-200/month
**Time:** 30-60 minutes

### 🏠 **Shared Hosting**
**Best for:** Testing only (not recommended for production)
**Cost:** $5-15/month
**Time:** Variable

---

## 🎯 **Option 1: Automated VPS Deployment (RECOMMENDED)**

### **Prerequisites:**
- Ubuntu 20.04+ VPS (2GB RAM minimum, 4GB recommended)
- Root/sudo access
- Domain name pointing to your server
- M-PESA Developer Account ([developer.safaricom.co.ke](https://developer.safaricom.co.ke))
- Africa's Talking Account ([africastalking.com](https://africastalking.com))

### **Step 1: Server Setup**
```bash
# Connect to your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y
```

### **Step 2: Download and Run Deployment Script**
```bash
# Download the ISP billing system
git clone https://github.com/your-repo/isp-billing-system.git
cd isp-billing-system/isp_billing_system

# Make deployment script executable
chmod +x deploy.sh

# Run deployment (will ask for configuration)
sudo ./deploy.sh
```

### **Step 3: Follow the Prompts**
The script will ask for:
- Domain name (e.g., `billing.yourisp.co.ke`)
- Email for SSL certificate
- M-PESA credentials
- Africa's Talking credentials

### **Step 4: DNS Configuration**
Point your domain to your server IP:
```
A record: billing.yourisp.co.ke → YOUR_SERVER_IP
```

### **That's it!** 🎉
Your system will be available at `https://billing.yourisp.co.ke`

---

## 🌩️ **Option 2: Cloud Deployment (AWS/DigitalOcean)**

### **DigitalOcean Deployment**

1. **Create Droplet:**
   - Ubuntu 20.04
   - 2GB RAM minimum
   - Enable monitoring

2. **Configure DNS:**
   ```bash
   # Add A record in DigitalOcean DNS
   billing.yourdomain.com → DROPLET_IP
   ```

3. **Deploy:**
   ```bash
   ssh root@DROPLET_IP
   wget https://raw.githubusercontent.com/your-repo/deploy.sh
   chmod +x deploy.sh
   ./deploy.sh
   ```

### **AWS EC2 Deployment**

1. **Launch EC2 Instance:**
   - Ubuntu 20.04 LTS
   - t3.small (2 vCPU, 2GB RAM)
   - Security group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Connect and Deploy:**
   ```bash
   ssh -i your-key.pem ubuntu@ec2-ip
   sudo apt update
   curl -O https://raw.githubusercontent.com/your-repo/deploy.sh
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

---

## 🔧 **Manual Deployment (Advanced)**

### **System Requirements:**
- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- PostgreSQL 12+
- Nginx
- 2GB RAM minimum

### **Step-by-Step Manual Installation:**

1. **Install Dependencies:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib nginx git

# Install build tools
sudo apt install -y build-essential libssl-dev libffi-dev
```

2. **Setup Database:**
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE isp_billing;
CREATE USER isp_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE isp_billing TO isp_user;
ALTER DATABASE isp_billing OWNER TO isp_user;
\q
EOF
```

3. **Deploy Application:**
```bash
# Create application user
sudo useradd --system --shell /bin/bash --home /opt/isp_billing --create-home isp

# Clone repository
sudo git clone https://github.com/your-repo/isp-billing.git /opt/isp_billing
sudo chown -R isp:isp /opt/isp_billing

# Create virtual environment
sudo -u isp python3 -m venv /opt/isp_billing/venv
sudo -u isp /opt/isp_billing/venv/bin/pip install -r /opt/isp_billing/requirements.txt
sudo -u isp /opt/isp_billing/venv/bin/pip install gunicorn psycopg2-binary
```

4. **Configure Environment:**
```bash
# Create .env file
sudo -u isp tee /opt/isp_billing/.env << EOF
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
DATABASE_URL=postgresql://isp_user:secure_password@localhost/isp_billing
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_BUSINESS_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key
EOF

sudo chmod 600 /opt/isp_billing/.env
```

5. **Initialize Database:**
```bash
cd /opt/isp_billing
sudo -u isp ./venv/bin/python run.py --init-db --no-run
```

6. **Create Systemd Service:**
```bash
sudo tee /etc/systemd/system/isp_billing.service << EOF
[Unit]
Description=ISP Billing System
After=network.target

[Service]
Type=notify
User=isp
Group=isp
WorkingDirectory=/opt/isp_billing
Environment=PATH=/opt/isp_billing/venv/bin
EnvironmentFile=/opt/isp_billing/.env
ExecStart=/opt/isp_billing/venv/bin/gunicorn --workers 3 --bind unix:/opt/isp_billing/isp_billing.sock app:app
ExecReload=/bin/kill -s HUP $MAINPID

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable isp_billing
sudo systemctl start isp_billing
```

7. **Configure Nginx:**
```bash
sudo tee /etc/nginx/sites-available/isp_billing << EOF
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/isp_billing/isp_billing.sock;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/isp_billing /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

8. **Install SSL Certificate:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 📱 **API Keys Setup**

### **M-PESA Developer Account:**
1. Visit [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Register and create an app
3. Get your credentials:
   - Consumer Key
   - Consumer Secret
   - Business Shortcode
   - Passkey

### **Africa's Talking Account:**
1. Visit [africastalking.com](https://africastalking.com)
2. Sign up and verify your account
3. Get your API key from dashboard
4. For production, request sender ID approval

### **Email Configuration:**
For Gmail SMTP:
1. Enable 2-Factor Authentication
2. Generate App Password
3. Use app password in configuration

---

## 🔍 **Post-Deployment Checklist**

### **Verify Installation:**
```bash
# Check service status
sudo systemctl status isp_billing

# Check logs
sudo journalctl -u isp_billing -f

# Test database connection
sudo -u isp /opt/isp_billing/venv/bin/python -c "
from app import app, db
with app.app_context():
    print('Database connection:', db.engine.url)
"
```

### **Test Functionality:**
1. ✅ Access website: `https://yourdomain.com`
2. ✅ Admin login: `+254700000000`
3. ✅ Customer registration
4. ✅ Package selection
5. ✅ M-PESA payment (sandbox)
6. ✅ SMS notifications
7. ✅ Email notifications

### **Security Setup:**
```bash
# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Disable root login (optional)
sudo passwd -l root

# Setup fail2ban (optional)
sudo apt install fail2ban
```

---

## 🔄 **Maintenance & Updates**

### **Update Application:**
```bash
cd /opt/isp_billing
sudo -u isp git pull origin main
sudo -u isp ./venv/bin/pip install -r requirements.txt
sudo systemctl restart isp_billing
```

### **Database Backup:**
```bash
# Manual backup
pg_dump -h localhost -U isp_user isp_billing > backup_$(date +%Y%m%d).sql

# Automated backup (already setup by deploy script)
/opt/isp_billing/backup.sh
```

### **View Logs:**
```bash
# Application logs
sudo journalctl -u isp_billing -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Billing automation logs
sudo tail -f /var/log/isp_billing_cron.log
```

---

## 📊 **Monitoring**

### **Basic Monitoring:**
```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Service status
systemctl status isp_billing nginx postgresql
```

### **Advanced Monitoring (Optional):**
- **Uptime Robot** - Website monitoring
- **Grafana + Prometheus** - System metrics
- **Logwatch** - Log analysis
- **Netdata** - Real-time monitoring

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**Service won't start:**
```bash
sudo journalctl -u isp_billing --no-pager
sudo systemctl restart isp_billing
```

**Database connection errors:**
```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"
```

**Nginx errors:**
```bash
sudo nginx -t
sudo systemctl restart nginx
```

**M-PESA payments not working:**
1. Check callback URL is accessible
2. Verify credentials in `.env` file
3. Check M-PESA logs in application

**SMS not sending:**
1. Verify Africa's Talking API key
2. Check account balance
3. Ensure sender ID is approved

---

## 💰 **Cost Estimates**

### **VPS Hosting (Monthly):**
- **Basic:** DigitalOcean Droplet (2GB) - $12/month
- **Standard:** Linode VPS (4GB) - $24/month
- **Premium:** AWS EC2 t3.medium - $30/month

### **Additional Costs:**
- Domain name: $10-15/year
- SSL certificate: Free (Let's Encrypt)
- M-PESA integration: Transaction fees only
- SMS: $0.005-0.01 per SMS
- Email: Free (Gmail) or $6/month (G Suite)

### **Total Monthly Cost:** $15-50/month

---

## 📞 **Support**

- **Documentation:** [GitHub Wiki](https://github.com/your-repo/wiki)
- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Email:** support@kenyanet.co.ke
- **WhatsApp:** +254 700 000 001

---

**🎉 Congratulations! Your ISP billing system is now deployed and ready to serve your customers!**