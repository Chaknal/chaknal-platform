
    #!/bin/bash
    # Chaknal Platform Health Check Webhook
    
    BACKEND_URL="https://chaknal-backend-container.azurewebsites.net"
    FRONTEND_URL="https://agreeable-bush-01890e00f.1.azurestaticapps.net"
    
    # Check backend health
    if ! curl -f -s "$BACKEND_URL/health" > /dev/null; then
        echo "❌ Backend health check failed"
        exit 1
    fi
    
    # Check frontend accessibility
    if ! curl -f -s "$FRONTEND_URL" > /dev/null; then
        echo "❌ Frontend accessibility check failed"
        exit 1
    fi
    
    echo "✅ All health checks passed"
    exit 0
    