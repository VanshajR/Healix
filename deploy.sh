#!/bin/bash

# Healix Deployment Script
# This script helps deploy Healix Hospital Management System

set -e

echo "🏥 Healix Hospital Management System - Deployment Script"
echo "========================================================="

# Function to check if docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    echo "✅ Docker and Docker Compose are installed"
}

# Function to setup environment
setup_environment() {
    if [ ! -f .env ]; then
        echo "📝 Setting up environment file..."
        cp .env.template .env
        echo "✅ Created .env file from template"
        echo "⚠️  Please review and update .env file with your settings"
    else
        echo "✅ Environment file already exists"
    fi
}

# Function to deploy web interface with Docker
deploy_web() {
    echo "🌐 Starting Web Interface deployment..."
    
    # Build and start services
    docker-compose up --build -d db
    
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Check if database is healthy
    if docker-compose exec db pg_isready -U healix_user -d healix_db; then
        echo "✅ Database is ready"
    else
        echo "❌ Database is not ready. Please check logs: docker-compose logs db"
        exit 1
    fi
    
    # Start web interface
    docker-compose --profile web up -d web
    
    echo "🚀 Web deployment complete!"
    echo ""
    echo "🌐 Web interface is available at: http://localhost:5000"
    echo ""
    echo "Available commands:"
    echo "  View web logs:      docker-compose logs web"
    echo "  View all logs:      docker-compose logs"
    echo "  Stop services:      docker-compose down"
    echo "  Restart web:        docker-compose restart web"
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Starting Docker deployment..."
    
    # Build and start services
    docker-compose up --build -d db
    
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Check if database is healthy
    if docker-compose exec db pg_isready -U healix_user -d healix_db; then
        echo "✅ Database is ready"
    else
        echo "❌ Database is not ready. Please check logs: docker-compose logs db"
        exit 1
    fi
    
    echo "🚀 Deployment complete!"
    echo ""
    echo "Available commands:"
    echo "  Admin Interface:    docker-compose up app"
    echo "  Login Interface:    docker-compose --profile main up main"
    echo "  Web Interface:      docker-compose --profile web up web"
    echo "  View logs:          docker-compose logs"
    echo "  Stop services:      docker-compose down"
    echo ""
    echo "Web interface will be available at: http://localhost:5000"
}

# Function to deploy locally
deploy_local() {
    echo "💻 Setting up local deployment..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "🐍 Python version: $python_version"
    
    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    echo "✅ Local setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Setup PostgreSQL database and run healix_statements.sql"
    echo "2. Update .env file with your database connection"
    echo "3. Run: python3 admin.py (for admin interface)"
    echo "4. Run: python3 main.py (for login interface)"
}

# Main menu
main() {
    echo "Choose deployment option:"
    echo "1) Docker Deployment (GUI - Recommended)"
    echo "2) Docker Web Interface Deployment"
    echo "3) Local Deployment"
    echo "4) Exit"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            check_docker
            setup_environment
            deploy_docker
            ;;
        2)
            check_docker
            setup_environment
            deploy_web
            ;;
        3)
            setup_environment
            deploy_local
            ;;
        4)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            main
            ;;
    esac
}

# Run main function
main