# Healix Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Clone and Setup
```bash
git clone https://github.com/VanshajR/Healix.git
cd Healix
```

### Step 2: Run Deployment
```bash
./deploy.sh
```

### Step 3: Choose Your Option
- **Option 1**: Docker GUI (Traditional desktop app)
- **Option 2**: Docker Web Interface (Browser-based)
- **Option 3**: Local Installation

## 🌐 Web Interface Demo

The web interface provides browser-based access to Healix:

### Login Page
- Access at `http://localhost:5000`
- Login as Patient, Doctor, or Admin
- Default admin: `admin` / `admin123`

### Dashboards
- **Patient Dashboard**: View assigned doctors and medical info
- **Doctor Dashboard**: Manage patients and appointments  
- **Admin Dashboard**: Full hospital management features

## 🐳 Docker Deployment

### Quick Docker Commands
```bash
# Web Interface (Recommended for new users)
docker-compose --profile web up -d

# GUI Interface (Full features)
docker-compose up app

# View logs
docker-compose logs

# Stop services
docker-compose down
```

## 🔧 Environment Configuration

Copy `.env.template` to `.env` and customize:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
ADMIN_ID=your_admin_id
ADMIN_PASSWORD=your_secure_password
```

## 📱 Access Methods

| Method | Access | Features | Best For |
|--------|--------|----------|----------|
| GUI | Desktop app | Full features | Admin/Power users |
| Web | Browser | Core features | Remote access |
| Mobile | Web browser | Basic features | On-the-go |

## 🆘 Need Help?

1. **Issues**: Check `./verify-deployment.sh`
2. **Documentation**: Read `DEPLOYMENT.md`
3. **Logs**: `docker-compose logs`
4. **Database**: Default credentials in `.env.template`

## 🔐 Security Notes

**Before Production:**
- Change default passwords
- Use secure database credentials
- Enable SSL/HTTPS
- Configure firewall rules
- Set up regular backups

---

**Ready to deploy? Run `./deploy.sh` now!** 🚀