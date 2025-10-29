import os

# Email Configuration
# These will read from environment variables in production (Render)
# Or use the default values when running locally

SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'mooduvenkatesh.nielit@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'lcypqqkyxtcjuxbq')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'venkatchouhan24@gmail.com')

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587