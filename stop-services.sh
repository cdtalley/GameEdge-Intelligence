#!/bin/bash

# GameEdge Intelligence - Stop Services Script

echo "🛑 Stopping GameEdge Intelligence Services"
echo "========================================="

# Stop backend service
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "🔄 Stopping backend service (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm .backend.pid
        echo "✅ Backend service stopped"
    else
        echo "ℹ️ Backend service is not running"
        rm .backend.pid
    fi
else
    echo "ℹ️ No backend PID file found"
fi

# Stop frontend service
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "🔄 Stopping frontend service (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm .frontend.pid
        echo "✅ Frontend service stopped"
    else
        echo "ℹ️ Frontend service is not running"
        rm .frontend.pid
    fi
else
    echo "ℹ️ No frontend PID file found"
fi

# Stop Docker services
echo "🔄 Stopping Docker services..."
docker-compose down

echo "✅ All services stopped successfully!"
echo ""
echo "💡 To start services again, run: ./quick-start.sh"
