"""
Enhanced Webhook Data Collector with Azure Database Integration

This script receives webhooks from Dux-Soup and stores them directly
in Azure PostgreSQL Database for real-time processing.
"""

import json
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from azure_database import AzureDatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize database manager
db_manager = None

def init_database():
    """Initialize database connection"""
    global db_manager
    
    connection_string = os.getenv('AZURE_POSTGRES_CONNECTION_STRING')
    if not connection_string:
        logger.error("❌ AZURE_POSTGRES_CONNECTION_STRING not found in environment")
        logger.info("Please run setup_azure_database.py first")
        return False
    
    try:
        db_manager = AzureDatabaseManager(connection_string)
        logger.info("✅ Azure database connection initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Dux-Soup"""
    try:
        # Get webhook data
        webhook_data = request.get_json()
        
        if not webhook_data:
            logger.error("❌ No JSON data received")
            return jsonify({'error': 'No JSON data'}), 400
        
        # Extract basic info for logging
        event_type = webhook_data.get('type', 'unknown')
        event_name = webhook_data.get('event', 'unknown')
        profile_url = webhook_data.get('profile', 'N/A')
        
        logger.info(f"📥 Received webhook: {event_type}.{event_name} for {profile_url}")
        
        # Store in database
        if db_manager:
            event_id = db_manager.store_webhook_event(webhook_data)
            logger.info(f"✅ Webhook stored in database: {event_id}")
        else:
            logger.warning("⚠️ Database not available, webhook not stored")
        
        return jsonify({'status': 'success', 'event_id': event_id if db_manager else None}), 200
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    db_status = "connected" if db_manager else "disconnected"
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    if not db_manager:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        # Get basic stats
        stats = {
            'total_webhook_events': 0,
            'events_by_type': {},
            'recent_events': []
        }
        
        # You can add more detailed statistics here
        # For now, return basic info
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/contacts/replied', methods=['GET'])
def get_contacts_replied():
    """Get contacts who replied to campaigns"""
    if not db_manager:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        campaign_id = request.args.get('campaign_id')
        if not campaign_id:
            return jsonify({'error': 'campaign_id parameter required'}), 400
        
        contacts = db_manager.get_contacts_who_replied(campaign_id)
        return jsonify({'contacts': contacts}), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting contacts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/messages/<contact_id>', methods=['GET'])
def get_message_history(contact_id):
    """Get message history for a contact"""
    if not db_manager:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        messages = db_manager.get_message_history(contact_id)
        return jsonify({'messages': messages}), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting messages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns/<campaign_id>/stats', methods=['GET'])
def get_campaign_stats(campaign_id):
    """Get campaign statistics"""
    if not db_manager:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        stats = db_manager.get_campaign_stats(campaign_id)
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns/active', methods=['GET'])
def get_active_campaigns():
    """Get all active campaigns (between scheduled_start and end_date)"""
    if not db_manager:
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        active_campaigns = db_manager.get_active_campaigns()
        return jsonify({
            'active_campaigns': active_campaigns,
            'count': len(active_campaigns)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting active campaigns: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home page with API documentation"""
    return jsonify({
        'service': 'Chaknal',
        'version': '1.0.0',
        'endpoints': {
            'webhook': 'POST /webhook - Receive Dux-Soup webhooks',
            'health': 'GET /health - Health check',
            'stats': 'GET /stats - Database statistics',
            'contacts_replied': 'GET /contacts/replied?campaign_id=<id> - Get contacts who replied',
            'message_history': 'GET /messages/<contact_id> - Get message history',
            'campaign_stats': 'GET /campaigns/<campaign_id>/stats - Get campaign statistics',
            'active_campaigns': 'GET /campaigns/active - Get all active campaigns'
        },
        'database': 'connected' if db_manager else 'disconnected'
    }), 200

def main():
    """Main function to start the webhook server"""
    print("="*60)
    print("🚀 CHAKNAL")
    print("="*60)
    
    # Initialize database
    if not init_database():
        print("❌ Failed to initialize database. Please check your configuration.")
        print("Run 'python setup_azure_database.py' to configure the database.")
        return
    
    print("✅ Database connection established")
    print("📡 Webhook URL: http://localhost:5000/webhook")
    print("🏥 Health Check: http://localhost:5000/health")
    print("📊 Statistics: http://localhost:5000/stats")
    print("="*60)
    print("📋 Next Steps:")
    print("1. Configure Dux-Soup webhook URL to point to this server")
    print("2. Start your LinkedIn campaigns")
    print("3. Monitor webhook events via the API endpoints")
    print("4. Use the database for real-time analytics")
    print("🛑 Press Ctrl+C to stop the server")
    print("="*60)
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main() 