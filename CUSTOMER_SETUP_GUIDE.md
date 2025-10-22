# Customer Setup Guide - AI Outlook Calendar Agent

## 🎯 For Your Customer's IT Team

### Prerequisites
- Windows 10/11 or macOS/Linux
- Python 3.9 or higher
- Microsoft 365 account with Outlook
- Internet connection

## 📦 Installation Steps

### 1. Extract Files
Extract the provided ZIP file to desired location:
```
C:\OutlookCalendarAgent\
```

### 2. Install Python Dependencies
Open Command Prompt/Terminal in the project folder:
```bash
pip install -r requirements.txt
```

### 3. Azure App Registration (One-time setup)

#### A. Create Azure App
1. Go to: https://portal.azure.com/
2. Navigate: **Azure Active Directory** → **App registrations** → **New registration**
3. Fill details:
   - **Name**: "Outlook Calendar Agent"
   - **Account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank for now
4. Click **Register**
5. **Copy and save**: Application (client) ID and Directory (tenant) ID

#### B. Configure Authentication
1. Go to **Authentication** in left menu
2. Click **Add a platform** → **Mobile and desktop applications**
3. Check these redirect URIs:
   - ✅ `https://login.microsoftonline.com/common/oauth2/nativeclient`
   - ✅ `http://localhost`
4. Scroll to **Advanced settings**
5. Set **Allow public client flows** to **Yes**
6. Click **Save**

#### C. Set API Permissions
1. Go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:
   - ✅ `Calendars.ReadWrite`
   - ✅ `User.Read`
4. Click **Grant admin consent for [Your Organization]**

### 4. Get Google API Key

#### A. Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Create new project or select existing
3. Enable **Generative Language API**

#### B. Create API Key
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **API Key**
3. **Copy and save** the API key
4. (Optional) Restrict the key to Generative Language API

### 5. Configure Environment Variables

Create `.env` file in project root:
```env
TENANT_ID="your_tenant_id_from_step_3"
CLIENT_ID="your_client_id_from_step_3"
GOOGLE_API_KEY="your_google_api_key_from_step_4"
```

### 6. Test Installation

Run the test script:
```bash
python test_outlook_integration.py
```

Expected output:
```
============================================================
TESTING OUTLOOK CALENDAR INTEGRATION
============================================================

1. Authenticating with Microsoft Graph API...
[SUCCESS] Authentication successful!

2. Fetching calendar events for the next 7 days...
[SUCCESS] Found X events

3. Your Upcoming Calendar Events:
============================================================
[Lists your calendar events]

[SUCCESS] INTEGRATION TEST COMPLETE
============================================================
```

## 🚀 Running the Agent

### Option 1: Streamlit Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```
- Opens in browser at: http://localhost:8501
- User-friendly chat interface
- Example commands provided

### Option 2: FastAPI + Web Interface
```bash
uvicorn main:app --reload
```
- Opens in browser at: http://localhost:8000
- REST API + web interface
- Suitable for integration

## 👥 User Training

### Basic Commands
```
"Book a meeting with John tomorrow at 3 PM"
"Find my meetings this week"
"Reschedule the team meeting to 4 PM"
"Cancel the client call"
```

### Advanced Examples
```
"Create a meeting titled 'Project Review' on January 25th from 2-3 PM with john@company.com and sarah@company.com"
"Find all meetings with 'standup' in the title for next week"
"Move the budget meeting from Tuesday to Wednesday same time"
```

## 🔧 Troubleshooting

### Common Issues

#### Authentication Fails
**Problem**: "Failed to create device flow" or redirect URI error
**Solution**: 
1. Verify Azure app configuration (Step 3)
2. Ensure redirect URIs are added correctly
3. Check "Allow public client flows" is enabled

#### No Calendar Access
**Problem**: "Insufficient privileges" error
**Solution**:
1. Verify API permissions are granted (Step 3C)
2. Ensure admin consent is provided
3. Check user has calendar access in Outlook

#### Google API Errors
**Problem**: "API key invalid" or quota exceeded
**Solution**:
1. Verify API key is correct in .env file
2. Check Generative Language API is enabled
3. Monitor quota usage in Google Cloud Console

#### Import Errors
**Problem**: "Module not found" errors
**Solution**:
```bash
pip install --upgrade -r requirements.txt
```

### Getting Help

1. **Check logs**: Look for error messages in terminal
2. **Run tests**: `pytest tests/ -v` to verify installation
3. **Verify config**: Ensure .env file has correct values
4. **Contact support**: [Your support contact]

## 🔒 Security Notes

### Data Privacy
- No calendar data is stored locally
- Authentication tokens cached securely
- All communications encrypted (HTTPS)

### Access Control
- Users must authenticate with their Microsoft account
- Admin can revoke app access anytime in Azure portal
- Minimal permissions requested (only calendar access)

### Network Requirements
- Outbound HTTPS (443) to:
  - login.microsoftonline.com
  - graph.microsoft.com
  - generativelanguage.googleapis.com

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Test authentication
python test_outlook_integration.py

# Run full test suite
pytest tests/ -v

# Check dependencies
pip check
```

### Regular Maintenance
- Update dependencies monthly: `pip install --upgrade -r requirements.txt`
- Monitor Google API usage in Cloud Console
- Review Azure app permissions quarterly
- Backup .env configuration file

### Performance Monitoring
- Response times should be < 3 seconds
- Monitor Google API quota usage
- Check for authentication token expiry

## 📞 Support Information

### Technical Support
- **Documentation**: See included files
- **Test Suite**: 23 automated tests (100% pass rate)
- **Logs**: Available in terminal output
- **Contact**: [Your support email/phone]

### Business Hours Support
- **Availability**: [Your support hours]
- **Response Time**: [Your SLA]
- **Escalation**: [Your escalation process]

---

## ✅ Installation Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Azure app registered and configured
- [ ] Google API key obtained
- [ ] .env file created with correct values
- [ ] Test script runs successfully
- [ ] Streamlit app launches without errors
- [ ] User can authenticate and see calendar events
- [ ] Sample commands work correctly

**Installation Complete!** 🎉

Your AI-powered Outlook Calendar Agent is ready for use.