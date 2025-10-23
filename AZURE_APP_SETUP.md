# Azure App Setup for Public Use

## Create Multi-Tenant Azure App

### Step 1: Azure Portal Setup
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**

### Step 2: App Configuration
- **Name**: `AI Calendar Agent Public`
- **Supported account types**: `Accounts in any organizational directory and personal Microsoft accounts (e.g. Skype, Xbox)`
- **Redirect URI**: Leave blank for now

### Step 3: Authentication Setup
1. Go to **Authentication** tab
2. Click **Add a platform** → **Mobile and desktop applications**
3. Add redirect URI: `https://login.microsoftonline.com/common/oauth2/nativeclient`
4. Under **Advanced settings**:
   - Set **Allow public client flows** = **Yes**
   - Set **Enable the following mobile and desktop flows** = **Yes**

### Step 4: API Permissions
1. Go to **API permissions** tab
2. Click **Add a permission** → **Microsoft Graph**
3. Select **Delegated permissions**
4. Add these permissions:
   - `Calendars.ReadWrite`
   - `User.Read`
5. Click **Grant admin consent** (if you're admin)

### Step 5: Get Credentials
- Copy **Application (client) ID**
- Go to **Certificates & secrets** → **New client secret**
- Copy the **secret value** (save immediately!)

### Step 6: Update Streamlit Secrets
Add to Streamlit Cloud secrets:
```toml
CLIENT_SECRET = "your_actual_client_secret_value"
```

This will enable device code flow for all users!