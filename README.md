![image](static/logo.png) 
# StackMart

## Setting up Mail Credentials

### Step 1: Configure Your Google Account for an App Password

Regular Google account passwords no longer work for SMTP access. You must enable 2-Step Verification and generate a specific "App Password" to use in your Django settings.

- Go to your Google Account security page.
- Enable 2-Step Verification if it's not already on.
- Navigate to the App passwords section (you may need to re-enter your password).
- Under "Select app," choose Mail, and under "Select device," choose Other (custom name).
- Click Generate. Google will display a unique, 16-character password (e.g., smbumqjiurmqrywn).
- Copy this password immediately; it will not be shown again. This is the password you will use in your Django settings.

### Step 2: Configure Django .env

In your Django project's .env file, add the following configuration. for better safety and security we are implmeneting Env File.

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True # Use port 587 for TLS
EMAIL_HOST_USER = 'your-email@gmail.com' # Replace with your full Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password' # Replace with the generated App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com' # Optional: default sender email
```

Note: For SSL, you would use EMAIL_PORT = 465 and EMAIL_USE_SSL = True with EMAIL_USE_TLS = False

## Running the Server.

Before Running the server make sure you have configured Mail credentials in .env file as mentioned [here](#setting-up-mail-credentials-mail-header).

1. Clone The repo
2. Create a Virtual Environment in current Directory
   `python -m venv .venv`
3. Install Project's Requirements
   `pip install -r requirements.txt`
4. Run the Server.

   For Windows
   `yu.bat`

   For Linux/MacOS
   `python manage.py runserver 0.0.0.0:9060`
