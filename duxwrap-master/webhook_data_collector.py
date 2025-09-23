"""
Webhook Data Collector for Dux-Soup

This script receives webhooks from Dux-Soup and logs the data
to help design the database schema correctly.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from dataclasses import dataclass, asdict
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class WebhookEvent:
    """Structured webhook event data"""
    event_id: str
    event_type: str
    event_name: str
    profile_url: Optional[str]
    dux_user_id: Optional[str]
    timestamp: datetime
    raw_data: Dict[str, Any]
    processed: bool = False
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"event_{int(time.time() * 1000)}"

class WebhookDataCollector:
    """
    Collects and analyzes webhook data from Dux-Soup
    """
    
    def __init__(self, data_dir: str = "webhook_data"):
        """
        Initialize the webhook data collector
        
        Args:
            data_dir: Directory to store webhook data
        """
        self.data_dir = data_dir
        self.events: list[WebhookEvent] = []
        self.event_types_seen = set()
        self.profiles_seen = set()
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create subdirectories
        os.makedirs(f"{data_dir}/raw", exist_ok=True)
        os.makedirs(f"{data_dir}/processed", exist_ok=True)
        os.makedirs(f"{data_dir}/analysis", exist_ok=True)
        
        logger.info(f"Webhook data collector initialized. Data directory: {data_dir}")
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> WebhookEvent:
        """
        Process incoming webhook data
        
        Args:
            webhook_data: Raw webhook data from Dux-Soup
            
        Returns:
            Structured webhook event
        """
        # Extract basic information
        event_type = webhook_data.get("type", "unknown")
        event_name = webhook_data.get("event", "unknown")
        profile_url = webhook_data.get("profile")
        dux_user_id = webhook_data.get("userid")
        
        # Create structured event
        event = WebhookEvent(
            event_id=f"event_{int(time.time() * 1000)}",
            event_type=event_type,
            event_name=event_name,
            profile_url=profile_url,
            dux_user_id=dux_user_id,
            timestamp=datetime.now(),
            raw_data=webhook_data
        )
        
        # Store event
        self.events.append(event)
        
        # Track unique values
        self.event_types_seen.add(event_type)
        if profile_url:
            self.profiles_seen.add(profile_url)
        
        # Save raw data
        self._save_raw_webhook(event)
        
        # Save processed event
        self._save_processed_event(event)
        
        # Log event
        logger.info(f"📥 Received webhook: {event_type}.{event_name} for {profile_url or 'N/A'}")
        
        return event
    
    def _save_raw_webhook(self, event: WebhookEvent):
        """Save raw webhook data"""
        filename = f"{self.data_dir}/raw/{event.event_id}.json"
        with open(filename, 'w') as f:
            json.dump(event.raw_data, f, indent=2, default=str)
    
    def _save_processed_event(self, event: WebhookEvent):
        """Save processed event data"""
        filename = f"{self.data_dir}/processed/{event.event_id}.json"
        with open(filename, 'w') as f:
            json.dump(asdict(event), f, indent=2, default=str)
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """
        Generate analysis report of collected webhook data
        
        Returns:
            Analysis report
        """
        if not self.events:
            return {"message": "No events collected yet"}
        
        # Event type breakdown
        event_type_counts = {}
        for event in self.events:
            key = f"{event.event_type}.{event.event_name}"
            event_type_counts[key] = event_type_counts.get(key, 0) + 1
        
        # Profile breakdown
        profile_counts = {}
        for event in self.events:
            if event.profile_url:
                profile_counts[event.profile_url] = profile_counts.get(event.profile_url, 0) + 1
        
        # Time analysis
        timestamps = [event.timestamp for event in self.events]
        time_range = {
            "first_event": min(timestamps).isoformat(),
            "last_event": max(timestamps).isoformat(),
            "total_events": len(self.events)
        }
        
        # Data structure analysis
        data_structure_analysis = self._analyze_data_structures()
        
        report = {
            "summary": {
                "total_events": len(self.events),
                "unique_event_types": len(self.event_types_seen),
                "unique_profiles": len(self.profiles_seen),
                "time_range": time_range
            },
            "event_type_breakdown": event_type_counts,
            "profile_activity": dict(sorted(profile_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "data_structure_analysis": data_structure_analysis,
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        filename = f"{self.data_dir}/analysis/analysis_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _analyze_data_structures(self) -> Dict[str, Any]:
        """Analyze the structure of webhook data"""
        if not self.events:
            return {}
        
        # Sample event for structure analysis
        sample_event = self.events[0]
        
        # Analyze common fields
        common_fields = set(sample_event.raw_data.keys())
        for event in self.events[1:]:
            common_fields = common_fields.intersection(set(event.raw_data.keys()))
        
        # Analyze data types
        field_types = {}
        for event in self.events[:10]:  # Analyze first 10 events
            for key, value in event.raw_data.items():
                if key not in field_types:
                    field_types[key] = set()
                field_types[key].add(type(value).__name__)
        
        return {
            "common_fields": list(common_fields),
            "field_types": {k: list(v) for k, v in field_types.items()},
            "sample_event_structure": sample_event.raw_data
        }
    
    def _generate_recommendations(self) -> Dict[str, Any]:
        """Generate database schema recommendations"""
        recommendations = {
            "database_tables": [],
            "field_mappings": {},
            "indexes": [],
            "constraints": []
        }
        
        # Based on event types seen, suggest tables
        if "message" in self.event_types_seen:
            recommendations["database_tables"].append({
                "name": "messages",
                "description": "Store message events from Dux-Soup",
                "key_fields": ["event_id", "profile_url", "event_type", "timestamp"]
            })
        
        if "action" in self.event_types_seen:
            recommendations["database_tables"].append({
                "name": "actions",
                "description": "Store action events (connect, visit, etc.)",
                "key_fields": ["event_id", "profile_url", "action_type", "timestamp"]
            })
        
        if "rccommand" in self.event_types_seen:
            recommendations["database_tables"].append({
                "name": "robot_commands",
                "description": "Store robot command events",
                "key_fields": ["event_id", "command_type", "status", "timestamp"]
            })
        
        # Suggest indexes
        recommendations["indexes"].extend([
            "CREATE INDEX idx_events_profile_url ON events(profile_url)",
            "CREATE INDEX idx_events_timestamp ON events(timestamp)",
            "CREATE INDEX idx_events_type ON events(event_type)"
        ])
        
        return recommendations

# Initialize Flask app
app = Flask(__name__)
collector = WebhookDataCollector()

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    """
    Receive webhooks from Dux-Soup
    """
    try:
        # Get webhook data
        webhook_data = request.get_json()
        
        if not webhook_data:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        # Process webhook
        event = collector.process_webhook(webhook_data)
        
        # Return success
        return jsonify({
            "success": True,
            "event_id": event.event_id,
            "message": f"Webhook processed: {event.event_type}.{event.event_name}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "events_collected": len(collector.events),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analysis', methods=['GET'])
def get_analysis():
    """Get analysis report"""
    try:
        report = collector.generate_analysis_report()
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    """Get recent events"""
    try:
        limit = request.args.get('limit', 50, type=int)
        events = collector.events[-limit:] if collector.events else []
        
        return jsonify({
            "events": [asdict(event) for event in events],
            "total_events": len(collector.events)
        }), 200
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home page with instructions"""
    return jsonify({
        "service": "Chaknal - Webhook Data Collector",
        "endpoints": {
            "webhook": "POST /webhook - Receive webhooks from Dux-Soup",
            "health": "GET /health - Health check",
            "analysis": "GET /analysis - Get analysis report",
            "events": "GET /events?limit=50 - Get recent events"
        },
        "status": {
            "events_collected": len(collector.events),
            "data_directory": collector.data_dir
        },
        "instructions": [
            "1. Configure Dux-Soup webhook URL to point to this server",
            "2. Start your LinkedIn campaigns",
            "3. Monitor webhook events via /analysis endpoint",
            "4. Use collected data to design your database schema"
        ]
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CHAKNAL - WEBHOOK DATA COLLECTOR")
    print("=" * 60)
    print(f"📡 Webhook URL: http://localhost:5000/webhook")
    print(f"🏥 Health Check: http://localhost:5000/health")
    print(f"📊 Analysis: http://localhost:5000/analysis")
    print(f"📋 Events: http://localhost:5000/events")
    print("=" * 60)
    print("📋 Next Steps:")
    print("1. Configure Dux-Soup webhook URL to point to this server")
    print("2. Start your LinkedIn campaigns")
    print("3. Monitor webhook events via the analysis endpoint")
    print("4. Use collected data to design your database schema")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False) 