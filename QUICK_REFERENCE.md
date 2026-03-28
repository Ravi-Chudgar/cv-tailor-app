# 🎯 Quick Reference - Excel-Based User Storage

## ✅ What Was Done

1. **Excel File Created**: `server/data/users.xlsx`
   - Auto-created on first run
   - Stores all user data permanently
   - Formatted with headers and styling

2. **Secure Passwords**
   - All passwords hashed with bcrypt
   - Never stored in plaintext
   - Can't be reversed (one-way encryption)

3. **User Persistence**
   - Users saved even after app restart
   - Admin can delete users (except admin account)
   - Users fetched from Excel on every login

4. **Admin Controls**
   - View all users
   - Deactivate users (they can't login)
   - Delete users
   - View system stats

## 📁 Files to Know

| File | Purpose |
|------|---------|
| `server/data/users.xlsx` | User database (open with Excel) |
| `server/app/users_storage.py` | User management code |
| `EXCEL_USER_STORAGE.md` | Technical documentation |
| `USER_MANAGEMENT_GUIDE.md` | How to manage users |
| `IMPLEMENTATION_SUMMARY.md` | What was built |

## 🚀 Quick Start

### Start the App
```bash
# Terminal 1 - Backend
cd f:\cv-tailor-app-new
python -m uvicorn server.app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
cd f:\cv-tailor-app-new\client
npm run dev
```

### Access
- **App**: http://localhost:5173
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 👥 Default Login

| Username | Password |
|----------|----------|
| admin    | admin123 |

⚠️ **Change this password immediately after first login!**

## 📊 User Excel File Structure

Open `server/data/users.xlsx` to see:
- User ID (auto-generated)
- Username (login name)
- Password Hash (encrypted - don't edit!)
- Email (can edit)
- Is Active (TRUE = can login, FALSE = blocked)
- Created At (timestamp)
- Updated At (timestamp)
- Role (admin or user)

## 🎮 What Users Can Do

- ✅ Register new account → Saved to Excel
- ✅ Login → Verified against Excel
- ✅ Upload CV
- ✅ Analyze job description
- ✅ Tailor CV for jobs
- ✅ Download PDF of tailored CV
- ✅ View profile

## 👮 What Admins Can Do

- ✅ View all users
- ✅ Delete users
- ✅ Deactivate/reactivate users
- ✅ View system statistics
- ✅ Access admin dashboard

## 💾 Backup Your Users

```bash
# Simple backup
copy server\data\users.xlsx server\data\users_backup.xlsx

# Or just copy the file to a safe location
```

## 🔍 Verify Everything Works

1. ✅ Open http://localhost:5173
2. ✅ Login: admin / admin123
3. ✅ Click Register
4. ✅ Create new user: testuser / testpass123
5. ✅ Logout
6. ✅ Login as testuser / testpass123
7. ✅ Verify users in `server/data/users.xlsx`
8. ✅ Go to Admin and see all users

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Users can't register | Check backend logs |
| Login fails | Verify `users.xlsx` exists |
| Changes not saved | Restart backend |
| Can't delete admin | By design - use API if needed |
| Excel file locked | Restart backend |

## 📝 Common Tasks

### Change User Email
1. Open `users.xlsx`
2. Find user row
3. Edit Email column
4. Save

### Deactivate User
1. Open `users.xlsx`
2. Find user row
3. Set "Is Active" to FALSE
4. Save

### Delete User
Via App:
- Login as admin → Admin panel → Delete user

Via Excel:
- Delete the entire row from `users.xlsx`

### Reset Admin Password
1. Delete `server/data/users.xlsx`
2. Restart backend
3. Admin account recreated with password: admin123

## 🎓 Testing the System

### Test Registration
```bash
POST http://localhost:8001/api/auth/register
Body: {"username":"testuser","password":"password123"}
```

### Test Login
```bash
POST http://localhost:8001/api/auth/login
Body: {"username":"admin","password":"admin123"}
```

### View All Users (Admin)
```bash
GET http://localhost:8001/api/admin/users
```

## 🔐 Security Summary

✅ Passwords are hashed (bcrypt)
✅ Admin account protected
✅ Users can't delete themselves
✅ Inactive users can't login
✅ All data is in one Excel file

## 📈 Next Steps

- [ ] Change admin password in production
- [ ] Setup automatic backups of users.xlsx
- [ ] Monitor user growth
- [ ] Migrate to database when scaling
- [ ] Add password reset feature
- [ ] Add email verification

## 📞 Need Help?

- Check: `EXCEL_USER_STORAGE.md` (technical details)
- Check: `USER_MANAGEMENT_GUIDE.md` (how to manage users)
- Check: `IMPLEMENTATION_SUMMARY.md` (what was built)

---

**Status**: ✅ READY TO USE
**Backend**: ✅ Running on port 8001
**Frontend**: ✅ Running on port 5173
**Database**: ✅ Excel file created at server/data/users.xlsx
