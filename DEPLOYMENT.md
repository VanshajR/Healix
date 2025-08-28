# Healix Deployment Guide

This guide provides multiple deployment options for the Healix Hospital Management System.

## 🚀 Quick Start (Recommended: Docker)

The easiest way to deploy Healix is using Docker:

```bash
# Clone the repository
git clone https://github.com/VanshajR/Healix.git
cd Healix

# Run the deployment script
./deploy.sh
```

Select option 1 for Docker deployment, and the script will handle everything automatically.

## 📋 Deployment Options

### 1. Docker Deployment (Recommended)

**Advantages:**
- Easy setup and deployment
- Isolated environment
- Automatic database setup
- Cross-platform compatibility

**Requirements:**
- Docker and Docker Compose installed
- X11 forwarding (for GUI on Linux/macOS)

**Steps:**

1. **Setup environment:**
   ```bash
   cp .env.template .env
   # Edit .env file if needed (default values work for Docker)
   ```

2. **Deploy with Docker:**
   ```bash
   # Start database
   docker-compose up -d db
   
   # Wait for database to initialize (about 30 seconds)
   
   # Run admin interface
   docker-compose up app
   
   # OR run login interface
   docker-compose --profile main up main
   ```

3. **For Linux users with GUI:**
   ```bash
   # Allow X11 forwarding
   xhost +local:docker
   
   # Then run the containers as above
   ```

**Docker Commands:**
```bash
# View logs
docker-compose logs

# Stop all services
docker-compose down

# Remove all data (including database)
docker-compose down -v

# Rebuild application
docker-compose build app
```

### 2. Local Development Setup

**Requirements:**
- Python 3.10+
- PostgreSQL 12+
- pip package manager

**Steps:**

1. **Setup Python environment:**
   ```bash
   # Create virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL database:**
   ```bash
   # Create database
   createdb healix_db
   
   # Run database setup
   psql -d healix_db -f healix_statements.sql
   ```

3. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your database connection details
   ```

4. **Run the application:**
   ```bash
   # Admin interface
   python admin.py
   
   # Login interface
   python main.py
   ```

### 3. Cloud Deployment Options

#### 3.1 AWS Deployment

**Using AWS ECS with RDS:**

1. **Setup RDS PostgreSQL instance**
2. **Create ECS task definition** using the Dockerfile
3. **Setup Application Load Balancer** (if adding web interface)
4. **Configure environment variables** in ECS task

**Using AWS EC2:**

1. **Launch EC2 instance** with Docker installed
2. **Clone repository** and setup Docker Compose
3. **Setup RDS PostgreSQL** separately
4. **Update environment variables** to point to RDS

#### 3.2 Google Cloud Deployment

**Using Google Cloud Run:**

1. **Build and push image** to Google Container Registry
2. **Setup Cloud SQL PostgreSQL** instance
3. **Deploy to Cloud Run** with environment variables

**Using Google Compute Engine:**

1. **Create VM instance** with Docker
2. **Setup Cloud SQL** database
3. **Deploy using Docker Compose**

#### 3.3 Azure Deployment

**Using Azure Container Instances:**

1. **Setup Azure Database for PostgreSQL**
2. **Create container group** with the application
3. **Configure environment variables**

#### 3.4 DigitalOcean Deployment

**Using DigitalOcean App Platform:**

1. **Setup Managed PostgreSQL** database
2. **Deploy from GitHub** repository
3. **Configure environment variables**

**Using DigitalOcean Droplet:**

1. **Create droplet** with Docker
2. **Setup Managed Database**
3. **Deploy with Docker Compose**

### 4. Production Considerations

#### 4.1 Security

```bash
# Strong database credentials
DATABASE_URL=postgresql://secure_user:complex_password@host:5432/healix_db

# Strong admin credentials
ADMIN_ID=admin_user
ADMIN_PASSWORD=very_secure_password_123!
```

#### 4.2 Backup Strategy

**Database Backup:**
```bash
# Automated backup script
#!/bin/bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# For Docker deployment
docker-compose exec db pg_dump -U healix_user healix_db > backup.sql
```

#### 4.3 Monitoring

**Health Checks:**
```bash
# Database health
docker-compose exec db pg_isready -U healix_user -d healix_db

# Application logs
docker-compose logs app
```

#### 4.4 Scaling

**For higher usage:**
- Use connection pooling (PgBouncer)
- Setup read replicas for database
- Consider converting to web interface for multiple users

## 🔧 Troubleshooting

### Common Issues

**1. GUI not showing in Docker:**
```bash
# Linux: Allow X11 forwarding
xhost +local:docker

# macOS: Install XQuartz and allow connections
# Windows: Use VcXsrv or similar X11 server
```

**2. Database connection issues:**
```bash
# Check database status
docker-compose exec db pg_isready -U healix_user -d healix_db

# Check logs
docker-compose logs db
```

**3. Permission issues:**
```bash
# Fix file permissions
chmod +x deploy.sh
```

**4. Port conflicts:**
```bash
# Check if port 5432 is in use
netstat -an | grep 5432

# Change port in docker-compose.yml if needed
```

### Getting Help

1. **Check logs:** `docker-compose logs`
2. **Database issues:** `docker-compose logs db`
3. **Application issues:** `docker-compose logs app`
4. **Environment issues:** Verify `.env` file settings

## 🌐 Web Interface Option

For a web-based deployment, consider these approaches:

1. **Streamlit conversion** - Convert GUI to web interface
2. **Flask/Django** - Create web API and interface
3. **Remote desktop** - Use VNC/RDP for GUI access

The current GUI application can be accessed remotely using:
- VNC server in Docker container
- Remote desktop solutions
- X11 forwarding over SSH

## 📝 Next Steps

After deployment:

1. **Test the application** with sample data
2. **Setup regular backups**
3. **Configure monitoring**
4. **Document user procedures**
5. **Plan for updates and maintenance**

For production use, consider:
- SSL/TLS certificates
- Firewall configuration
- User access management
- Data retention policies