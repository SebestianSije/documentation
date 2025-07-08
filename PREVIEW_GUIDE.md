# 🚀 **ISP Billing System Preview Guide**

**KenyaNet ISP Billing System** - A comprehensive billing and customer management solution for Internet Service Providers.

---

## **📋 Quick Start (3 Steps)**

### **Step 1: Install Dependencies**
```bash
cd isp_billing_system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Step 2: Start the System**
```bash
source venv/bin/activate  # Make sure virtual environment is active
python run.py
```

### **Step 3: Open Your Browser**
Navigate to: **http://localhost:5000**

---

## **🔑 Default Login Credentials**

### **Admin Account**
- **Phone:** `+254700000000`
- **Access:** Admin Dashboard with full system control

### **Sample Customer Accounts**
- **John Kamau:** `+254712345678`
- **Mary Wanjiku:** `+254723456789`  
- **Peter Ochieng:** `+254734567890`

---

## **🌐 System URLs**

| Page | URL | Description |
|------|-----|-------------|
| **Homepage** | `http://localhost:5000` | Main landing page |
| **Customer Login** | `http://localhost:5000/login` | Customer portal login |
| **Admin Dashboard** | `http://localhost:5000/admin/dashboard` | Admin control panel |
| **Register** | `http://localhost:5000/register` | New customer registration |
| **Packages** | `http://localhost:5000/packages` | View available internet packages |

---

## **💡 What You Can Test**

### **Customer Features**
✅ **Account Registration** - Sign up new customers  
✅ **Login & Dashboard** - Customer self-service portal  
✅ **View Bills** - Current and past billing statements  
✅ **Payment Processing** - M-PESA integration demo  
✅ **Package Selection** - Choose internet plans  
✅ **Profile Management** - Update customer information  

### **Admin Features**
✅ **Customer Management** - Add, edit, view customers  
✅ **Billing System** - Generate and manage bills  
✅ **Package Management** - Create internet packages  
✅ **Payment Tracking** - Monitor payment status  
✅ **Reports & Analytics** - Financial and usage reports  
✅ **System Configuration** - Manage system settings  

---

## **📦 Sample Internet Packages**

| Package | Speed | Price (KES) | Features |
|---------|-------|-------------|----------|
| **Basic** | 10 Mbps | 2,500/month | Fair usage during peak hours |
| **Standard** | 20 Mbps | 4,000/month | Fair usage during peak hours |
| **Premium** | 50 Mbps | 7,500/month | Unlimited speeds |
| **Business** | 100 Mbps | 12,000/month | Priority support + unlimited |

---

## **🔧 System Features Preview**

### **Automated Billing**
- Monthly bill generation
- Automatic due date calculations  
- Overdue payment tracking
- Service suspension/reconnection

### **Payment Integration**
- **M-PESA Paybill:** 123456 (Demo)
- **Account Number:** Customer phone number
- Real-time payment verification
- Automated receipt generation

### **Communication**
- SMS notifications via Africa's Talking
- Email alerts and invoices
- Payment confirmations
- Service status updates

### **Customer Management**
- Detailed customer profiles
- Installation tracking with GPS
- Service history logs
- Support ticket system

---

## **📱 Mobile-Friendly Interface**

The system is fully responsive and works great on:
- 📱 Mobile phones
- 📱 Tablets  
- 💻 Desktop computers
- 🖥️ Large displays

---

## **🚨 Troubleshooting**

### **Application Won't Start?**
```bash
# Check if virtual environment is active
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Initialize database
python run.py --init-db
```

### **Port 5000 Already in Use?**
```bash
# Kill processes using port 5000
sudo lsof -ti:5000 | xargs kill -9

# Or change port in run.py (line 294)
app.run(debug=True, host='0.0.0.0', port=8000)
```

### **Database Issues?**
```bash
# Reset database
rm isp_billing.db
python run.py --init-db
```

---

## **🔒 Security Features**

- ✅ User authentication and authorization
- ✅ Admin role separation
- ✅ Secure payment processing
- ✅ Input validation and sanitization
- ✅ Session management
- ✅ CSRF protection

---

## **📊 Reports & Analytics**

### **Available Reports**
- Monthly revenue reports
- Customer growth analytics
- Package popularity metrics  
- Payment success rates
- Overdue accounts summary
- Service usage statistics

---

## **🌍 Production Deployment**

### **For Live Deployment:**

1. **Environment Configuration**
   ```bash
   # Create .env file with real credentials
   MPESA_CONSUMER_KEY=your_mpesa_key
   MPESA_CONSUMER_SECRET=your_mpesa_secret
   AFRICASTALKING_API_KEY=your_sms_key
   ```

2. **Database Setup**
   - Use PostgreSQL or MySQL for production
   - Configure backup strategies
   - Set up replication if needed

3. **Web Server**
   - Deploy with Gunicorn + Nginx
   - Configure SSL certificate
   - Set up load balancing

4. **Monitoring**
   - Application performance monitoring
   - Error tracking and logging
   - Automated backup verification

---

## **📞 Support & Documentation**

- **Email:** support@kenyanet.co.ke
- **Documentation:** Comprehensive guides included
- **API Documentation:** Available for integrations
- **Video Tutorials:** Setup and usage guides

---

## **🎯 Next Steps**

1. **Start the system** using the Quick Start guide above
2. **Explore the admin dashboard** with the default admin account
3. **Test customer registration** by creating a new account
4. **Process a demo payment** to see the payment flow
5. **Generate reports** to see the analytics capabilities

**Ready to preview? Run `python run.py` and visit http://localhost:5000!**

---

*💡 **Tip:** This system is production-ready and includes all the features a real ISP would need for customer and billing management.*