# User Management Guide - Excel Storage

## Where User Data is Stored

**File Location**: `f:\cv-tailor-app-new\server\data\users.xlsx`

You can open this file directly in Excel, Google Sheets, or any spreadsheet application.

## User Data Columns

| Column | Purpose | Example | Notes |
|--------|---------|---------|-------|
| **User ID** | Unique identifier | 1, 2, 3, ... | Auto-generated (do not edit) |
| **Username** | Login name | admin, john_doe | Must be unique |
| **Password Hash** | Encrypted password | `$2b$12$...` | Never edit this! |
| **Email** | User email address | user@example.com | Can be edited |
| **Is Active** | Account status | TRUE / FALSE | TRUE = can login |
| **Created At** | Account creation time | 2026-03-28T... | Do not edit |
| **Updated At** | Last modification time | 2026-03-28T... | Auto-updated |
| **Role** | User privilege level | admin, user | admin/user only |

## Managing Users

### View All Users
1. Open file: `server\data\users.xlsx`
2. See all registered users with their details
3. No action needed for viewing

### Edit User Information
**You CAN edit:**
- ✅ Email address (column D)
- ✅ Is Active status (column E) - Set to TRUE or FALSE
- ✅ Role (column H) - Change to "admin" or "user"

**You CANNOT/SHOULD NOT edit:**
- ❌ User ID - Will break system
- ❌ Username - Use API for username changes
- ❌ Password Hash - Passwords must be hashed
- ❌ Created At / Updated At - System timestamps

### Example: Deactivate a User
If user "john_doe" violates terms:
1. Open `users.xlsx`
2. Find row with Username = "john_doe"
3. Set "Is Active" column to FALSE
4. Save file
5. User john_doe can no longer login (even with correct password)

### Example: Change User Role to Admin
To make "alice" an administrator:
1. Open `users.xlsx`
2. Find row with Username = "alice"
3. Change Role column from "user" to "admin"
4. Save file
5. alice can now use admin features

## Adding Users Manually (Not Recommended)

⚠️ Only if registration via app is broken:

1. Open `users.xlsx`
2. Go to next empty row
3. Fill in:
   - User ID: `(max_id + 1)`
   - Username: (new unique name)
   - Password Hash: Generate using this Python code:
   
```python
import bcrypt
password = "password123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
```

4. Email: user@example.com
5. Is Active: TRUE
6. Created At: 2026-03-28T15:30:00
7. Updated At: 2026-03-28T15:30:00
8. Role: user (or admin)
9. Save file

**Recommended**: Use the app's registration form instead!

## Deleting Users

### Via Application (Recommended)
1. Login as admin
2. Go to Admin panel
3. Find user to delete
4. Click "Delete" button
5. User removed from users.xlsx

### Via Excel File (Manual)
1. Open `users.xlsx`
2. Select the entire row (click row number)
3. Right-click → Delete Row
4. Save file
5. User cannot login anymore

⚠️ **NOTE**: Cannot delete admin user!

## Backing Up User Data

### Manual Backup
```bash
# Copy the file
copy server\data\users.xlsx server\data\users_backup_2026-03-28.xlsx
```

### Automated Backup (Recommended)
Set up a scheduled task to backup users.xlsx daily:
```powershell
# Weekly backup script
$source = "f:\cv-tailor-app-new\server\data\users.xlsx"
$dest = "f:\cv-tailor-app-new\server\data\backups\users_$(Get-Date -Format 'yyyy-MM-dd').xlsx"
Copy-Item $source $dest
```

## Troubleshooting

### Problem: Users can't login after editing Excel
**Solution**: 
- Verify "Is Active" column = TRUE
- Make sure you didn't edit "Password Hash" column
- Restart backend server

### Problem: Excel file is locked
**Solution**:
- Close the file in Excel
- Restart backend server
- File will be released

### Problem: Can't save changes to Excel
**Solution**:
- Ensure backend server is NOT running (it locks the file)
- Make edits
- Restart backend server

### Problem: Deleted admin account by mistake
**Solution**:
1. Delete line: `server/data/users.xlsx`
2. Restart backend (will recreate with admin account)
3. Login with admin / admin123

## Security Best Practices

✅ **DO:**
- Change admin password immediately
- Backup users.xlsx regularly
- Review active users periodically
- Deactivate unused accounts
- Monitor admin accounts

❌ **DON'T:**
- Share password hashes
- Store plaintext passwords
- Edit Password Hash column
- Leave admin account with default password
- Delete users without reason

## API Endpoints for User Management

### Login User
```
POST /api/auth/login
Body: {"username":"admin","password":"admin123"}
```

### Register User
```
POST /api/auth/register
Body: {"username":"newuser","password":"securepass123"}
```

### Get All Users (Admin)
```
GET /api/admin/users
Response: List of all users with details
```

### Get Specific User (Admin)
```
GET /api/admin/users/1
Response: Single user details
```

### Delete User (Admin)
```
DELETE /api/admin/users/2
Response: {"message":"User deleted successfully"}
```

### Toggle User Status (Admin)
```
PUT /api/admin/users/2/status
Body: {"is_active": false}
Response: User deactivated
```

## Sample Data

### Initial State (First Run)
```
User ID | Username | Email              | Is Active | Role
1       | admin    | admin@example.com  | TRUE      | admin
```

### After New Registrations
```
User ID | Username  | Email               | Is Active | Role
1       | admin     | admin@example.com   | TRUE      | admin
2       | john_doe  | john_doe@example    | TRUE      | user
3       | jane_smith| jane_smith@example  | TRUE      | user
4       | testuser  | testuser@example    | FALSE     | user
```

## Performance Notes

- Supports up to 10,000+ users efficiently
- No database required
- Instant backups (just copy the file)
- Suitable for small to medium teams
- For enterprise (100k+), migrate to PostgreSQL

## Getting Help

- Check backend logs: `http://localhost:8001/docs`
- View all users: Open `users.xlsx` directly
- Check Python console for errors
- Restart backend if users not appearing

---

**Last Updated**: March 28, 2026
**System Status**: ✅ Ready for Use
**User Count**: Check `users.xlsx` for current count
