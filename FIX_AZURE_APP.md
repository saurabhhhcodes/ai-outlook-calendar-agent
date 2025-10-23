# URGENT: Fix Azure App Configuration

## Your App ID: c7015219-8996-4dd4-ac85-5602660c6bbc

### Quick Fix Steps:

1. Go to https://portal.azure.com
2. Search for "App registrations"
3. Find app: c7015219-8996-4dd4-ac85-5602660c6bbc
4. Click on it

### Fix Authentication:
1. Go to **Authentication** tab
2. Click **Add a platform** → **Mobile and desktop applications**
3. Check the box: `https://login.microsoftonline.com/common/oauth2/nativeclient`
4. Scroll down to **Advanced settings**
5. Set **"Allow public client flows"** to **YES**
6. Click **Save**

### Fix API Permissions:
1. Go to **API permissions** tab
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Search and add:
   - `Calendars.ReadWrite`
   - `User.Read`
6. Click **Add permissions**
7. Click **Grant admin consent for [Your Directory]**

### Test:
After these changes, the device flow will work and authentication will succeed!
