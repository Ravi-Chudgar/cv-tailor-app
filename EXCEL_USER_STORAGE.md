# Excel-Based User Storage System

## Overview
The CV Tailor application now uses a persistent Excel-based user storage system instead of in-memory storage. This means:
- ✅ **User data persists** even after the app restarts
- ✅ **Easy to manage** - Users can view/edit the Excel file directly
- ✅ **Secure passwords** - Passwords are hashed using bcrypt
- ✅ **Admin controls** - Only admin can delete users

## File Location
- **File**: `server/data/users.xlsx`
- **Auto-created**: Yes (created automatically on first run)
- **Backup**: Recommended to backup this file regularly

## User Data Structure
Each user record contains:
| Column | Description |
|--------|-------------|
| User ID | Unique identifier (auto-generated) |
| Username | Login username (unique) |
| Password Hash | Encrypted password (bcrypt) |
| Email | User email address |
| Is Active | Active/inactive status (True/False) |
| Created At | Account creation timestamp |
| Updated At | Last update timestamp |
| Role | User role (admin/user) |

## Default Admin Account
The system is initialized with one admin account:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

⚠️ **Important**: Change the default admin password after first login!

## How It Works

### User Registration
1. User clicks "Register" and enters credentials
2. System validates:
   - Username doesn't already exist
   - Password is at least 6 characters
3. Password is **hashed** using bcrypt (never stored plaintext)
4. User record is added to `users.xlsx`
5. User can login immediately

### User Login
1. User enters username and password
2. System:
   - Finds user by username in Excel
   - Verifies password against stored hash
   - Checks if user account is active
3. Returns auth tokens if credentials are valid

### Admin User Management
Admins can:
- **View all users**: `/api/admin/users`
- **View specific user**: `/api/admin/users/{user_id}`
- **Delete user**: `/api/admin/users/{user_id}` (DELETE)
- **Toggle active/inactive**: `/api/admin/users/{user_id}/status` (PUT)
- **Cannot delete**: Own account or admin user directly

## Security Features
✅ **Password Hashing**: bcrypt with salt
✅ **No Plaintext Storage**: Original passwords never stored
✅ **Admin Protection**: Cannot delete admin account
✅ **Access Control**: Endpoints require proper authentication

## Accessing the Users File

### View/Edit Users
1. Navigate to: `server/data/users.xlsx`
2. Open with Excel or LibreOffice Calc
3. View all registered users and their details
4. ⚠️ **Warning**: Do not edit password hashes manually!

### Backup Users
```bash
# Copy the file for backup
cp server/data/users.xlsx server/data/users_backup.xlsx
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with username/password
- `POST /api/auth/register` - Register new account
- `GET /api/auth/current-user` - Get logged-in user info

### Admin User Management
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/{user_id}` - Get specific user
- `DELETE /api/admin/users/{user_id}` - Delete user
- `PUT /api/admin/users/{user_id}/status` - Toggle active/inactive
- `GET /api/admin/stats` - Get system statistics

## Testing

### Test User Registration
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### Test User Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### View All Users (Admin)
```bash
curl http://localhost:8001/api/admin/users
```

## Troubleshooting

### Issue: "Cannot create users.xlsx"
**Solution**: Check that the `server/data/` directory exists and has write permissions

### Issue: "User not found after registration"
**Solution**: 
1. Restart the backend server
2. Check that `server/data/users.xlsx` exists
3. Look at the Excel file to verify the user was added

### Issue: "Login fails with correct credentials"
**Solution**:
1. Check the Excel file to ensure user exists
2. Verify the Is Active column is set to True
3. Restart the backend server

## Future Enhancements
- [ ] Database migration from Excel to PostgreSQL
- [ ] User profile editing
- [ ] Password reset functionality
- [ ] Export user reports
- [ ] Import users from CSV

## Support
For issues or questions, check the backend logs at:
```
http://localhost:8001/docs
```
