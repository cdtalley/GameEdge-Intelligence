#!/bin/bash

# GameEdge Intelligence - Quick Start Script
# This script will set up the development environment

echo "🚀 GameEdge Intelligence - Quick Start"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p backend/models
mkdir -p frontend/.next
mkdir -p data
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Copy environment files
echo "⚙️ Setting up environment configuration..."
if [ ! -f backend/.env ]; then
    cp backend/env.example backend/.env
    echo "✅ Backend environment file created"
else
    echo "ℹ️ Backend environment file already exists"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/env.example frontend/.env
    echo "✅ Frontend environment file created"
else
    echo "ℹ️ Frontend environment file already exists"
fi

# Start database services
echo "🗄️ Starting database services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps postgres | grep -q "Up"; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL failed to start"
    exit 1
fi

if docker-compose ps redis | grep -q "Up"; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Start the application
echo "🚀 Starting GameEdge Intelligence..."
echo ""
echo "📋 Services will be available at:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Database: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "🔄 Starting services in the background..."

# Start backend
cd backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Save PIDs for later cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "✅ Services started successfully!"
echo ""
echo "📝 Logs are available at:"
echo "   Backend: backend.log"
echo "   Frontend: frontend.log"
echo ""
echo "🛑 To stop services, run: ./stop-services.sh"
echo ""
echo "🎉 GameEdge Intelligence is now running!"
echo "   Open http://localhost:3000 in your browser to view the dashboard"
