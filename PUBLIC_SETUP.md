# Public Multi-Tenant Setup

## Azure App Registration (Public Use)

### App Details:
- **Application Type**: Public client (multi-tenant)
- **Supported Account Types**: Accounts in any organizational directory and personal Microsoft accounts
- **Authentication**: Device code flow enabled
- **Permissions**: Calendars.ReadWrite, User.Read (delegated)

### For Users:
1. **Client ID**: `c6b880d2-0990-4ee9-a7eb-c3bab3d27110` (shared for all users)
2. **Tenant ID**: `common` (works for all Microsoft accounts)
3. **User Email**: Your own Microsoft account email
4. **Google API Key**: Get your own from Google Cloud Console

### How it Works:
- **Shared Client ID**: All users use the same Azure app
- **Individual Authentication**: Each user signs in with their own Microsoft account
- **Private Calendar Access**: Each user only sees their own calendar
- **Secure**: No shared credentials, each user authenticates separately

### Setup Instructions:
1. Go to the deployed Streamlit app
2. Enter the shared Client ID: `c6b880d2-0990-4ee9-a7eb-c3bab3d27110`
3. Set Tenant ID to: `common`
4. Enter your Microsoft account email
5. Get your own Google API key from: https://console.cloud.google.com
6. Use the app with your own calendar!