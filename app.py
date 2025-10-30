from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re
import os

# Import DNS library for email validation
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    print("⚠️ WARNING: dnspython not installed. Email validation disabled!")
    print("   Install with: pip install dnspython")

app = Flask(__name__)

# ========================================
# EMAIL CONFIGURATION
# ========================================

# Import configuration from config.py
try:
    from config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SMTP_SERVER, SMTP_PORT
except ImportError:
    # Fallback to environment variables if config.py doesn't exist
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

# Validation settings
ENABLE_STRICT_EMAIL_VALIDATION = True  # Must be True to block invalid emails
REQUIRE_MINIMUM_MESSAGE_LENGTH = False  # Set to True if you want minimum 10 chars

# ========================================
# ENHANCED EMAIL VALIDATION
# ========================================

def validate_email_format(email):
    """Check if email format is valid (user@domain.com)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None
    
    if is_valid:
        print(f"   ✅ Format valid: {email}")
    else:
        print(f"   ❌ Format invalid: {email}")
    
    return is_valid

def check_email_exists(email):
    """
    CRITICAL FUNCTION: Verify email domain and mailbox actually exist.
    This blocks typo emails like venkatchouhna24@gmail.com (missing 'a')
    """
    if not DNS_AVAILABLE:
        print("   ⚠️ DNS library not available - CANNOT validate email!")
        return False
    
    try:
        # Extract domain from email
        domain = email.split('@')[1].lower()
        print(f"   🔍 Checking domain: {domain}")
        
        # Step 1: Check if domain has MX (Mail Exchange) records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                print(f"   ❌ Domain '{domain}' has NO mail servers")
                return False
            
            print(f"   ✅ Domain '{domain}' has {len(mx_records)} mail server(s)")
            
            # Step 2: Additional verification - Check if domain resolves to IP
            try:
                dns.resolver.resolve(domain, 'A')
                print(f"   ✅ Domain '{domain}' resolves to IP address")
            except:
                pass  # MX record is enough
            
            return True
            
        except dns.resolver.NXDOMAIN:
            print(f"   ❌ Domain '{domain}' DOES NOT EXIST")
            return False
        except dns.resolver.NoAnswer:
            print(f"   ❌ Domain '{domain}' has NO mail servers (MX records)")
            return False
        except dns.resolver.Timeout:
            print(f"   ⚠️ DNS timeout for '{domain}' - rejecting to be safe")
            return False
            
    except Exception as e:
        print(f"   ❌ Email validation error: {e}")
        return False

def validate_email_complete(email):
    """
    Complete email validation with detailed logging.
    Returns: (is_valid, error_message)
    """
    print(f"\n🔍 VALIDATING EMAIL: {email}")
    
    # Step 1: Check format
    if not validate_email_format(email):
        print(f"   ❌ REJECTED: Invalid email format\n")
        return False, "Invalid email format. Please enter a valid email address."
    
    # Step 2: Check if email actually exists
    if not DNS_AVAILABLE:
        print(f"   ⚠️ WARNING: DNS library not available - accepting anyway\n")
        return True, "Email accepted (validation unavailable)"
    
    if not ENABLE_STRICT_EMAIL_VALIDATION:
        print(f"   ⚠️ WARNING: Strict validation disabled - accepting without verification\n")
        return True, "Email accepted (validation disabled)"
    
    if not check_email_exists(email):
        print(f"   ❌ REJECTED: Email does not exist or cannot receive mail\n")
        return False, "This email address does not exist or cannot receive emails. Please check for typos and try again."
    
    print(f"   ✅ ACCEPTED: Email is valid and can receive mail\n")
    return True, "Email validated successfully"

def validate_form_data(data):
    """Validate all form fields with detailed error messages"""
    errors = []
    
    # Validate Name
    if not data.get('name'):
        errors.append('Name is required')
    elif len(data['name'].strip()) < 2:
        errors.append('Name must be at least 2 characters long')
    elif len(data['name']) > 100:
        errors.append('Name is too long (maximum 100 characters)')
    
    # Validate Email (STRICT)
    if not data.get('email'):
        errors.append('Email address is required')
    else:
        email = data['email'].strip()
        is_valid, message = validate_email_complete(email)
        if not is_valid:
            errors.append(message)
    
    # Validate Message (NO MINIMUM LENGTH REQUIREMENT)
    if not data.get('message'):
        errors.append('Message is required')
    elif len(data['message'].strip()) == 0:
        errors.append('Message cannot be empty')
    elif REQUIRE_MINIMUM_MESSAGE_LENGTH and len(data['message'].strip()) < 10:
        errors.append('Message must be at least 10 characters long')
    elif len(data['message']) > 2000:
        errors.append('Message is too long (maximum 2000 characters)')
    
    return errors

# ========================================
# EMAIL SENDING FUNCTION
# ========================================

def send_email_notification(data):
    """Send email notification with anti-spam headers"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔔 Portfolio Contact: {data['name']}"
        msg['From'] = f"{data['name']} <{SENDER_EMAIL}>"
        msg['To'] = RECIPIENT_EMAIL
        msg['Reply-To'] = data['email']
        msg['X-Mailer'] = 'Portfolio Contact Form'
        msg['X-Priority'] = '3'
        msg['Importance'] = 'Normal'
        
        # HTML Email
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 30px;
                }}
                .info-row {{
                    margin: 15px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    border-radius: 4px;
                }}
                .info-row strong {{
                    color: #667eea;
                    display: inline-block;
                    min-width: 120px;
                }}
                .message-box {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 25px 0;
                    border: 1px solid #e0e0e0;
                }}
                .message-box h3 {{
                    color: #667eea;
                    margin-top: 0;
                }}
                .reply-btn {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>📧 New Contact Form Submission</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">From your Portfolio Website</p>
                </div>
                
                <div class="content">
                    <div class="info-row">
                        <strong>👤 Name:</strong> {data['name']}
                    </div>
                    <div class="info-row">
                        <strong>📧 Email:</strong> <a href="mailto:{data['email']}" style="color: #667eea;">{data['email']}</a>
                    </div>
                    <div class="info-row">
                        <strong>🕐 Received:</strong> {data['timestamp']}
                    </div>
                    <div class="info-row">
                        <strong>🌐 IP Address:</strong> {data.get('ip_address', 'Unknown')}
                    </div>
                    
                    <div class="message-box">
                        <h3>💬 Message:</h3>
                        <div style="white-space: pre-wrap;">{data['message']}</div>
                    </div>
                    
                    <center>
                        <a href="mailto:{data['email']}?subject=Re: Your message from my portfolio" class="reply-btn">
                            📨 Reply to {data['name'].split()[0]}
                        </a>
                    </center>
                </div>
                
                <div class="footer">
                    <p><strong>Portfolio Contact System</strong></p>
                    <p>Timestamp: {data['timestamp']} | IP: {data.get('ip_address', 'Unknown')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text = f"""
NEW CONTACT FORM SUBMISSION
===========================

Name:     {data['name']}
Email:    {data['email']}
Time:     {data['timestamp']}
IP:       {data.get('ip_address', 'Unknown')}

MESSAGE:
--------
{data['message']}

---
Reply directly to this email to respond.
        """
        
        msg.attach(MIMEText(text, 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

# ========================================
# ROUTES
# ========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submission with STRICT validation"""
    
    if not request.is_json:
        return jsonify({
            'success': False,
            'message': 'Invalid request format.'
        }), 400
    
    data = request.get_json()
    
    print("\n" + "="*70)
    print("📨 NEW FORM SUBMISSION RECEIVED")
    print("="*70)
    print(f"Name:    {data.get('name', 'N/A')}")
    print(f"Email:   {data.get('email', 'N/A')}")
    print(f"Message: {data.get('message', 'N/A')[:50]}...")
    
    # VALIDATE FORM DATA (This will block invalid emails!)
    errors = validate_form_data(data)
    
    if errors:
        print(f"\n❌ VALIDATION FAILED - SUBMISSION REJECTED")
        print(f"Errors:")
        for error in errors:
            print(f"   • {error}")
        print("="*70 + "\n")
        
        return jsonify({
            'success': False,
            'message': ' | '.join(errors)
        }), 400
    
    # If we reach here, ALL validations passed
    print(f"\n✅ VALIDATION PASSED - Preparing to send email...")
    
    submission = {
        'name': data['name'].strip(),
        'email': data['email'].strip().lower(),
        'message': data['message'].strip(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip_address': request.remote_addr
    }
    
    # Send email
    email_sent = send_email_notification(submission)
    
    if email_sent:
        print("="*70 + "\n")
        return jsonify({
            'success': True,
            'message': 'Thank you for reaching out! Your message has been sent successfully. I will get back to you soon! 🚀'
        }), 200
    else:
        print("="*70 + "\n")
        return jsonify({
            'success': False,
            'message': 'Failed to send email. Please try again or contact me directly at mooduvenkatesh.nielit@gmail.com'
        }), 500

@app.route('/test-email')
def test_email():
    """Test endpoint - Use real email for testing"""
    test_data = {
        'name': 'Test User',
        'email': 'venkatchouhan24@gmail.com',
        'message': 'This is a test message. If you receive this, the system is working!',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ip_address': '127.0.0.1'
    }
    
    print("\n🧪 Sending test email...")
    success = send_email_notification(test_data)
    
    return jsonify({
        'success': success,
        'message': f'Test email sent to {RECIPIENT_EMAIL}!' if success else 'Failed to send test email'
    })

# ========================================
# STARTUP - FIXED FOR RENDER DEPLOYMENT
# ========================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 PORTFOLIO SERVER STARTING")
    print("="*70)
    print(f"📧 Email Notifications: ENABLED")
    print(f"📬 Recipient Email: {RECIPIENT_EMAIL}")
    print(f"🔒 Email Validation: {'STRICT (Blocks Invalid Emails)' if ENABLE_STRICT_EMAIL_VALIDATION else 'DISABLED'}")
    print(f"📝 Message Min Length: {'None (accepts any length)' if not REQUIRE_MINIMUM_MESSAGE_LENGTH else '10 characters'}")
    print(f"🌐 Server: http://localhost:5000")
    print(f"🧪 Test Endpoint: http://localhost:5000/test-email")
    print("="*70)
    
    if not DNS_AVAILABLE:
        print("\n⚠️  CRITICAL WARNING: dnspython NOT installed!")
        print("   Email validation will NOT work properly!")
        print("   Install now: pip install dnspython\n")
    else:
        print("\n✅ All systems ready! DNS validation is ACTIVE.\n")
    
    # Get port from environment variable (Render sets this) or use 5000 for local
    port = int(os.environ.get('PORT', 8000))
    
    # Run the app
    # debug=False for production, host='0.0.0.0' to accept external connections
    app.run(host='0.0.0.0', port=port, debug=False)
