# 🤖 AI-Powered Outlook Calendar Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-outlook-calendar-agent.streamlit.app)

Transform your calendar management with natural language! This AI agent connects to your Microsoft Outlook calendar and lets you create, find, update, and delete events using simple conversational commands.

## ✨ Features

- 📅 **Natural Language Calendar Management**: "Create a birthday party for my nephew on September 1st, 2025 from 2 PM to 4 PM with friend@email.com"
- 🔍 **Smart Event Search**: "Find my meetings this week"
- ✏️ **Easy Updates**: "Move the team meeting to 4 PM"
- ❌ **Quick Deletion**: "Cancel the client call"
- 🧠 **AI-Powered Understanding**: Automatically extracts dates, times, and attendees from natural language
- 👥 **Multi-User Support**: Each user manages their own calendar securely
- 🌐 **Cloud Deployed**: Access from anywhere via web browser
- 🔒 **Secure Authentication**: Microsoft OAuth 2.0 with device code flow

## 🚀 Live Demo

**Try it now:** [https://ai-outlook-calendar-agent.streamlit.app](https://ai-outlook-calendar-agent.streamlit.app)

## 💻 Quick Start (Local Setup)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
**Windows**: Double-click `run.bat`
**Mac/Linux**: Run `./run.sh`
**Manual**: `streamlit run streamlit_app.py`

### Step 3: Configure Credentials
**Option A: Use .env file (Recommended)**
1. Copy `.env.example` to `.env`
2. Fill in your credentials

**Option B: Enter in the sidebar**
- **Tenant ID**: Your Azure tenant (or "common")
- **Client ID**: Your Azure app ID
- **Client Secret**: Your Azure app secret
- **Google API Key**: Your Google AI key

## 🔧 Getting Your Credentials

### 🏢 For Organizations (Recommended)
**IT Admin sets up once, everyone uses:**

#### Azure Setup (5 minutes)
1. Go to [Azure Portal](https://portal.azure.com)
2. **Azure Active Directory** → **App registrations** → **New registration**
3. Name: "Calendar Agent", Account type: "Accounts in this organizational directory only"
4. **Authentication** → **Add platform** → **Mobile and desktop applications**
5. Add redirect URI: `https://login.microsoftonline.com/common/oauth2/nativeclient`
6. Set **Allow public client flows** = **Yes**
7. **Certificates & secrets** → **New client secret** → Add description → **Add**
8. **Copy the client secret value** (you won't see it again!)
9. **API permissions** → Add **Microsoft Graph**:
   - Calendars.ReadWrite (Delegated)
   - User.Read (Delegated)
10. **Grant admin consent for [Your Organization]**
11. Copy **Application (client) ID**, **Directory (tenant) ID**, and **Client Secret**

#### Google API Key (2 minutes)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable **Generative Language API**
3. **APIs & Services** → **Credentials** → **Create API Key**
4. Copy the key

#### Share with Team
- Give everyone the **CLIENT_ID** and **GOOGLE_API_KEY**
- Each person uses their own Microsoft account to sign in
- Everyone's calendar data stays private

### 👤 For Personal Use
**Each person creates their own:**

1. Follow the same Azure setup steps above
2. Use "Accounts in any organizational directory and personal Microsoft accounts"
3. Get your own Google API key
4. Use your personal Microsoft account

### 🔄 Multiple Users Setup

#### Option 1: Shared App (Corporate)
```env
# Same for everyone in organization
TENANT_ID="your-company-tenant-id"
CLIENT_ID="shared-app-client-id"
CLIENT_SECRET="shared-app-client-secret"
GOOGLE_API_KEY="shared-google-api-key"

# Each user signs in with their own Microsoft account
# Calendar data remains private to each user
```

#### Option 2: Individual Apps (Personal)
```env
# Each person has their own
TENANT_ID="common"
CLIENT_ID="personal-app-client-id"
CLIENT_SECRET="personal-app-client-secret"
GOOGLE_API_KEY="personal-google-api-key"
USER_EMAIL="your-email@domain.com"
```

## 💬 Example Commands

### Creating Events
```
"Schedule a team standup tomorrow at 9 AM with sarah@company.com and mike@company.com"
"Book a client meeting on Friday 2-3 PM with john@company.com about project discussion"
"Create a project review next Monday 10 AM to 11 AM with the dev team at dev-team@company.com"
"Set up a quarterly planning meeting next Tuesday 2-4 PM with all managers"
```

### Finding Events
```
"What meetings do I have today?"
"Find all meetings with 'standup' this week"
"Show me my calendar for tomorrow"
"List meetings with John this month"
```

### Updating Events
```
"Move the team meeting from 2 PM to 3 PM"
"Reschedule the client call to next Tuesday same time"
"Change the standup time to 9:30 AM"
"Update the project review to 4 PM"
```

### Deleting Events
```
"Cancel the meeting with John"
"Delete the standup meeting tomorrow"
"Remove the client presentation"
"Cancel all meetings on Friday"
```

## 🛠️ Troubleshooting

### "Authentication Required" Browser Opens
- This is normal! Sign in with your Microsoft account
- The app will remember you for future use

### "Failed to create event"
- Check your Azure app permissions
- Ensure admin consent is granted
- Verify your credentials are correct

### "Google API Error"
- Confirm your API key is valid
- Check if Generative Language API is enabled
- Verify you haven't exceeded quota

### App Won't Start
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Try running manually: `streamlit run streamlit_app.py`

## 🔒 Security & Privacy

- **Secure Authentication**: Uses Microsoft's OAuth 2.0
- **No Data Storage**: No calendar data stored locally
- **Token Caching**: Secure local token storage
- **Enterprise Ready**: Meets corporate security standards
- **Multi-User Safe**: Each user's calendar data stays completely private
- **Shared Apps**: Safe to share CLIENT_ID (it's just an app identifier)
- **Never Share**: Personal Microsoft account passwords or tokens

## 📱 System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **Internet**: Required for API access
- **Browser**: For initial authentication

## 🎯 Advanced Usage

### API Mode
Start the FastAPI server for programmatic access:
```bash
uvicorn main:app --reload
```
Access at: http://localhost:8000

### Custom Commands
The AI understands natural language variations:
- "Set up a call" = "Schedule a meeting"
- "Next week" = Specific dates
- "Morning" = 9 AM default
- "Afternoon" = 2 PM default

## 📞 Support

### Common Issues
1. **Credentials not working**: Double-check Azure app configuration
2. **Browser not opening**: Try running as administrator
3. **API errors**: Verify internet connection and API quotas
4. **Multi-user setup**: Ensure each user has calendar permissions

### Getting Help
- Check the troubleshooting section above
- Verify all setup steps were completed
- Ensure your Microsoft account has calendar access
- For organizations: Contact your IT administrator

### Multi-User Troubleshooting
- **User can't sign in**: Check if they have Microsoft 365 access
- **No calendar access**: Verify user has Outlook/Exchange mailbox
- **Permissions error**: Ensure admin consent was granted
- **Different tenant**: Each user must be in the same organization (for corporate setup)

## 👥 Multi-User Deployment

### For IT Administrators
1. **Set up Azure app once** (5 minutes)
2. **Share CLIENT_ID** with all users
3. **Each user signs in** with their Microsoft account
4. **Everyone gets private** calendar access

### For Team Leaders
1. **Get credentials** from IT or set up personal
2. **Share the app** with team members
3. **Each person configures** their own credentials
4. **Start managing calendars** with natural language

### Security Benefits
- ✅ **Corporate Control**: IT manages app permissions
- ✅ **User Privacy**: Each person's calendar stays private
- ✅ **Easy Scaling**: Add unlimited users with same app
- ✅ **Audit Trail**: All actions logged to individual accounts

## 🎉 You're Ready!

Your AI calendar agent is now ready to transform how you manage your schedule. Start with simple commands like "What meetings do I have today?" and explore the natural language capabilities.

**Perfect for individuals, teams, and entire organizations!** 🚀