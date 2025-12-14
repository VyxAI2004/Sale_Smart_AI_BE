import asyncio
import logging
from uuid import UUID
from typing import Optional, AsyncGenerator
from sqlalchemy.orm import Session
from queue import Queue
import threading

from services.features.product_intelligence.orchestration.auto_discovery_service import AutoDiscoveryService
from services.features.product_intelligence.orchestration.streaming_events import EventEmitter

logger = logging.getLogger(__name__)


class AutoDiscoveryStreamingService:
    """Wrapper service để emit events trong quá trình auto discovery với SSE streaming"""
    
    def __init__(self, db: Session):
        self.auto_discovery_service = AutoDiscoveryService(db)
        self.db = db
    
    async def execute_auto_discovery_stream(
        self,
        project_id: UUID,
        user_id: UUID,
        user_input: str
    ) -> AsyncGenerator[dict, None]:
        """
        Execute auto discovery và yield events từng step cho SSE streaming (real-time)
        
        Args:
            project_id: Project ID
            user_id: User ID
            user_input: Natural language input
        
        Yields:
            Event dictionaries để gửi qua SSE (yield ngay khi có event)
        """
        event_queue = Queue()
        result_container = {"result": None, "error": None}
        
        def collect_event(event: dict):
            """Collect events và put vào queue để yield real-time"""
            event_queue.put(event)
        
        def run_discovery():
            """Run discovery in separate thread để không block async generator"""
            try:
                result = self.auto_discovery_service.execute_auto_discovery_from_natural_language(
                    project_id=project_id,
                    user_id=user_id,
                    user_input=user_input,
                    on_event=collect_event
                )
                result_container["result"] = result
            except Exception as e:
                logger.error(f"Streaming execution failed: {str(e)}", exc_info=True)
                result_container["error"] = str(e)
                event_queue.put(EventEmitter.step_error(
                    "unknown",
                    "Lỗi hệ thống",
                    f"Lỗi trong quá trình thực thi: {str(e)}",
                    {"error_type": "execution_error"}
                ))
            finally:
                event_queue.put(None)
        
        thread = threading.Thread(target=run_discovery, daemon=True)
        thread.start()
        
        try:
            while True:
                try:
                    event = event_queue.get(timeout=0.1)
                    if event is None:
                        break
                    yield event
                except:
                    if not thread.is_alive():
                        if result_container["error"]:
                            break
                        await asyncio.sleep(0.05)
                        continue
                    await asyncio.sleep(0.05)
        finally:
            if thread.is_alive():
                thread.join(timeout=5)

