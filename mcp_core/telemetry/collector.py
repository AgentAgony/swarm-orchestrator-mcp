
import logging
import time
import functools
import hashlib
import platform
import uuid
from pathlib import Path
from typing import Optional, Callable
from mcp_core.telemetry.events import TelemetryEvent, EventType
from mcp_core.telemetry.buffer import LocalTelemetryBuffer

logger = logging.getLogger(__name__)

class TelemetryCollector:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryCollector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.session_id = str(uuid.uuid4())
        self.install_id = self._get_install_id()
        
        # Use ~/.swarm/telemetry.db
        db_path = Path.home() / ".swarm" / "telemetry.db"
        self.buffer = LocalTelemetryBuffer(db_path)
        
        self._initialized = True
        logger.info(f"Telemetry initialized. Session: {self.session_id}")

    def _get_install_id(self) -> str:
        """Generate anonymized install ID from system info."""
        try:
            # Combine reliable system identifiers
            sid = platform.node() + platform.machine() + platform.system()
            return hashlib.sha256(sid.encode()).hexdigest()[:16]
        except Exception:
            return "unknown"

    def track_event(self, event: TelemetryEvent):
        """Record an event to the buffer."""
        self.buffer.add_event(event)

    def track_tool(self, tool_name: str) -> Callable:
        """Decorator to track tool execution."""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_cat = None
                
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error_cat = type(e).__name__
                    raise e
                finally:
                    duration = (time.time() - start_time) * 1000
                    
                    event = TelemetryEvent(
                        session_id=self.session_id,
                        install_id=self.install_id,
                        type=EventType.TOOL_USE,
                        tool_name=tool_name,
                        success=success,
                        duration_ms=duration,
                        error_category=error_cat
                    )
                    self.track_event(event)
            return wrapper
        return decorator

# Global instance
collector = TelemetryCollector()
