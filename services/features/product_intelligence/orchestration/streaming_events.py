from datetime import datetime
from typing import Optional, Dict, Any


class EventEmitter:
    """Helper class để tạo events chuẩn cho SSE streaming"""
    
    @staticmethod
    def step_start(step: str, step_name: str, message: str) -> Dict[str, Any]:
        """Emit khi bắt đầu một step"""
        return {
            "type": "step_start",
            "step": step,
            "step_name": step_name,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def ai_thinking(step: str, message: str) -> Dict[str, Any]:
        """Emit khi AI đang suy nghĩ/processing"""
        return {
            "type": "ai_thinking",
            "step": step,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def step_progress(step: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Emit progress update trong một step"""
        event = {
            "type": "step_progress",
            "step": step,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if data:
            event["data"] = data
        return event
    
    @staticmethod
    def step_complete(step: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Emit khi hoàn thành một step"""
        event = {
            "type": "step_complete",
            "step": step,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if data:
            event["data"] = data
        return event
    
    @staticmethod
    def step_error(step: str, step_name: str, message: str, error: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Emit khi có lỗi ở một step"""
        event = {
            "type": "step_error",
            "step": step,
            "step_name": step_name,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if error:
            event["error"] = error
        return event
    
    @staticmethod
    def final_result(message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Emit kết quả cuối cùng"""
        return {
            "type": "final_result",
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }


