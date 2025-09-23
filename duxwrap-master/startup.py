#!/usr/bin/env python3
"""
Azure App Service startup script for Chaknal
"""

import os
import sys
from webhook_data_collector_azure import app

if __name__ == '__main__':
    # Set the port from environment variable (Azure App Service sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port) 