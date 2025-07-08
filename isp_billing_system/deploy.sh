#!/bin/bash

# KenyaNet ISP Billing System Deployment Script
# For Ubuntu 20.04+ VPS deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="isp_billing"
APP_USER="isp"
APP_DIR="/opt/isp_billing"
DOMAIN=""
EMAIL=""

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    KenyaNet ISP Billing System Deployment"
    echo "=================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Collect deployment information
collect_info() {
    print_step "Collecting deployment information..."
    
    echo -n "Enter your domain name (e.g., billing.yourisp.co.ke): "
    read DOMAIN
    
    echo -n "Enter your email for SSL certificate: "
    read EMAIL
    
    echo -n "Enter M-PESA Consumer Key: "
    read MPESA_KEY
    
    echo -n "Enter M-PESA Consumer Secret: "
    read -s MPESA_SECRET
    echo
    
    echo -n "Enter M-PESA Business Shortcode: "
    read MPESA_SHORTCODE
    
    echo -n "Enter M-PESA Passkey: "
    read -s MPESA_PASSKEY
    echo
    
    echo -n "Enter Africa's Talking API Key: "
    read -s AT_API_KEY
    echo
    
    echo -n "Enter Africa's Talking Username: "
    read AT_USERNAME
    
    print_warning "Please verify the information above is correct before continuing."
    echo -n "Continue? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
}

# Update system
update_system() {
    print_step "Updating system packages..."
    apt update && apt upgrade -y
    apt install -y software-properties-common curl wget git
}

# Install Python
install_python() {
    print_step "Installing Python 3.9+..."
    apt install -y python3 python3-pip python3-venv python3-dev
    
    # Install additional packages
    apt install -y build-essential libssl-dev libffi-dev
}

# Install and configure PostgreSQL
install_database() {
    print_step "Installing PostgreSQL..."
    apt install -y postgresql postgresql-contrib
    
    # Start and enable PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    print_step "Setting up database..."
    sudo -u postgres psql -c "CREATE DATABASE isp_billing;"
    sudo -u postgres psql -c "CREATE USER isp_user WITH PASSWORD 'isp_secure_password_2024';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE isp_billing TO isp_user;"
    sudo -u postgres psql -c "ALTER DATABASE isp_billing OWNER TO isp_user;"
}

# Install Nginx
install_nginx() {
    print_step "Installing Nginx..."
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Configure firewall
    ufw allow 'Nginx Full'
    ufw allow ssh
    ufw --force enable
}

# Create application user
create_app_user() {
    print_step "Creating application user..."
    if ! id "$APP_USER" &>/dev/null; then
        useradd --system --shell /bin/bash --home-dir $APP_DIR --create-home $APP_USER
    fi
}

# Deploy application
deploy_app() {
    print_step "Deploying application..."
    
    # Create application directory
    mkdir -p $APP_DIR
    
    # Copy application files (assuming they're in current directory)
    if [ -f "app.py" ]; then
        cp -r . $APP_DIR/
    else
        print_error "Application files not found. Please run this script from the isp_billing_system directory."
        exit 1
    fi
    
    # Set ownership
    chown -R $APP_USER:$APP_USER $APP_DIR
    
    # Create virtual environment
    sudo -u $APP_USER python3 -m venv $APP_DIR/venv
    
    # Install Python packages
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install gunicorn psycopg2-binary
}

# Create environment file
create_env_file() {
    print_step "Creating environment configuration..."
    
    cat > $APP_DIR/.env << EOF
# Flask Configuration
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production

# Database Configuration
DATABASE_URL=postgresql://isp_user:isp_secure_password_2024@localhost/isp_billing

# M-PESA Configuration
MPESA_CONSUMER_KEY=$MPESA_KEY
MPESA_CONSUMER_SECRET=$MPESA_SECRET
MPESA_BUSINESS_SHORTCODE=$MPESA_SHORTCODE
MPESA_PASSKEY=$MPESA_PASSKEY
MPESA_CALLBACK_URL=https://$DOMAIN/api/mpesa/callback

# SMS Configuration
AFRICASTALKING_USERNAME=$AT_USERNAME
AFRICASTALKING_API_KEY=$AT_API_KEY

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=billing@$DOMAIN
EMAIL_PASSWORD=your-gmail-app-password
EOF
    
    chown $APP_USER:$APP_USER $APP_DIR/.env
    chmod 600 $APP_DIR/.env
}

# Initialize database
init_database() {
    print_step "Initializing database..."
    cd $APP_DIR
    sudo -u $APP_USER $APP_DIR/venv/bin/python run.py --init-db --no-run
}

# Create systemd service
create_systemd_service() {
    print_step "Creating systemd service..."
    
    cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=KenyaNet ISP Billing System
After=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
RuntimeDirectory=$APP_NAME
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/$APP_NAME.sock -m 007 --access-logfile - --error-logfile - app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    systemctl daemon-reload
    systemctl enable $APP_NAME
    systemctl start $APP_NAME
}

# Configure Nginx
configure_nginx() {
    print_step "Configuring Nginx..."
    
    cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/$APP_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t && systemctl reload nginx
}

# Install SSL certificate
install_ssl() {
    print_step "Installing SSL certificate..."
    
    # Install Certbot
    apt install -y certbot python3-certbot-nginx
    
    # Get certificate
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect
    
    # Set up auto-renewal
    systemctl enable certbot.timer
}

# Create cron jobs for automation
setup_automation() {
    print_step "Setting up billing automation..."
    
    # Create cron job for billing automation
    cat > /tmp/isp_cron << EOF
# ISP Billing Automation
0 6 * * * $APP_USER cd $APP_DIR && $APP_DIR/venv/bin/python utils/billing_automation.py >> /var/log/isp_billing_cron.log 2>&1
EOF
    
    crontab -u $APP_USER /tmp/isp_cron
    rm /tmp/isp_cron
    
    # Create log file
    touch /var/log/isp_billing_cron.log
    chown $APP_USER:$APP_USER /var/log/isp_billing_cron.log
}

# Setup log rotation
setup_logging() {
    print_step "Setting up log rotation..."
    
    cat > /etc/logrotate.d/isp_billing << EOF
/var/log/isp_billing_cron.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
}
EOF
}

# Create backup script
create_backup_script() {
    print_step "Creating backup script..."
    
    cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
# ISP Billing System Backup Script

BACKUP_DIR="/opt/backups/isp_billing"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U isp_user isp_billing > $BACKUP_DIR/database_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_files_$DATE.tar.gz -C /opt/isp_billing .

# Keep only last 30 backups
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x $APP_DIR/backup.sh
    chown $APP_USER:$APP_USER $APP_DIR/backup.sh
    
    # Add backup to cron (weekly)
    (crontab -u $APP_USER -l ; echo "0 2 * * 0 $APP_DIR/backup.sh") | crontab -u $APP_USER -
}

# Print final instructions
print_final_info() {
    print_step "Deployment completed successfully!"
    
    echo -e "${GREEN}"
    echo "=================================================="
    echo "           DEPLOYMENT SUCCESSFUL!"
    echo "=================================================="
    echo -e "${NC}"
    
    echo "🌐 Your ISP billing system is now available at:"
    echo "   https://$DOMAIN"
    echo
    echo "🔐 Default admin login:"
    echo "   Phone: +254700000000"
    echo
    echo "📁 Application directory: $APP_DIR"
    echo "📊 Service status: systemctl status $APP_NAME"
    echo "📋 Logs: journalctl -u $APP_NAME -f"
    echo
    echo "🔧 Next steps:"
    echo "1. Update your DNS to point $DOMAIN to this server"
    echo "2. Test the M-PESA integration with sandbox"
    echo "3. Configure your email SMTP settings in $APP_DIR/.env"
    echo "4. Set up monitoring and alerts"
    echo
    echo "📞 Support: https://github.com/your-repo/issues"
    echo
}

# Main deployment function
main() {
    print_header
    
    check_root
    collect_info
    update_system
    install_python
    install_database
    install_nginx
    create_app_user
    deploy_app
    create_env_file
    init_database
    create_systemd_service
    configure_nginx
    install_ssl
    setup_automation
    setup_logging
    create_backup_script
    print_final_info
}

# Run main function
main "$@"