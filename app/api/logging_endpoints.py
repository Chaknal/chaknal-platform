"""
Logging Endpoints for Debugging Contact Import
Provides endpoints to monitor and debug the import process
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import json

router = APIRouter()

# In-memory log storage for debugging
import_logs = []

class ImportLogEntry:
    """Log entry for import operations"""
    def __init__(self, operation: str, message: str, level: str = "INFO", **kwargs):
        self.timestamp = datetime.utcnow()
        self.operation = operation
        self.message = message
        self.level = level
        self.context = kwargs
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "operation": self.operation,
            "message": self.message,
            "level": self.level,
            "context": self.context
        }

def log_import_operation(operation: str, message: str, level: str = "INFO", **kwargs):
    """Log an import operation"""
    entry = ImportLogEntry(operation, message, level, **kwargs)
    import_logs.append(entry)
    
    # Keep only last 100 entries
    if len(import_logs) > 100:
        import_logs.pop(0)
    
    # Also log to console
    print(f"[{entry.timestamp}] {level} | {operation} | {message} | {json.dumps(kwargs)}")

@router.get("/logs/import", tags=["Logging"])
async def get_import_logs(
    limit: int = 50,
    level: str = "ALL",
    operation: str = None
):
    """Get import operation logs"""
    try:
        filtered_logs = import_logs.copy()
        
        # Filter by level
        if level != "ALL":
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        # Filter by operation
        if operation:
            filtered_logs = [log for log in filtered_logs if operation in log.operation]
        
        # Limit results
        filtered_logs = filtered_logs[-limit:] if limit > 0 else filtered_logs
        
        return {
            "success": True,
            "logs": [log.to_dict() for log in filtered_logs],
            "total_logs": len(import_logs),
            "filtered_count": len(filtered_logs),
            "filters": {
                "limit": limit,
                "level": level,
                "operation": operation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@router.post("/logs/import/clear", tags=["Logging"])
async def clear_import_logs():
    """Clear import operation logs"""
    try:
        global import_logs
        import_logs.clear()
        log_import_operation("LOG_CLEAR", "Import logs cleared", "INFO")
        
        return {
            "success": True,
            "message": "Import logs cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {str(e)}")

@router.get("/logs/import/stats", tags=["Logging"])
async def get_import_stats():
    """Get import operation statistics"""
    try:
        if not import_logs:
            return {
                "success": True,
                "stats": {
                    "total_operations": 0,
                    "operations_by_type": {},
                    "operations_by_level": {},
                    "recent_activity": []
                }
            }
        
        # Calculate statistics
        operations_by_type = {}
        operations_by_level = {}
        
        for log in import_logs:
            # Count by operation type
            op_type = log.operation.split('_')[0] if '_' in log.operation else log.operation
            operations_by_type[op_type] = operations_by_type.get(op_type, 0) + 1
            
            # Count by level
            operations_by_level[log.level] = operations_by_level.get(log.level, 0) + 1
        
        # Get recent activity (last 10 entries)
        recent_activity = [log.to_dict() for log in import_logs[-10:]]
        
        return {
            "success": True,
            "stats": {
                "total_operations": len(import_logs),
                "operations_by_type": operations_by_type,
                "operations_by_level": operations_by_level,
                "recent_activity": recent_activity,
                "time_range": {
                    "oldest": import_logs[0].timestamp.isoformat() if import_logs else None,
                    "newest": import_logs[-1].timestamp.isoformat() if import_logs else None
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")

@router.get("/logs/import/test", tags=["Logging"])
async def test_import_logging():
    """Test the import logging system"""
    try:
        log_import_operation("TEST", "Testing import logging system", "INFO", test=True)
        log_import_operation("TEST", "This is a warning message", "WARNING", warning=True)
        log_import_operation("TEST", "This is an error message", "ERROR", error=True)
        
        return {
            "success": True,
            "message": "Import logging system tested successfully",
            "test_logs_added": 3,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing logging: {str(e)}")
