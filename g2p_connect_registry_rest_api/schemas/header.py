from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Header(BaseModel):
    version: str = "1.0.0"
    message_id: str = ""
    message_ts: datetime = datetime.utcnow()
    action: str = "search"
    sender_id: str = ""
    sender_uri: Optional[str] = ""
    receiver_id: Optional[str] = ""
    total_count: int
    is_msg_encrypted: bool = False
    meta: dict = {}


class ResponseHeader(BaseModel):
    version: str = "1.0.0"
    message_id: str
    message_ts: datetime = datetime.utcnow()
    action: str = "on-search"
    status: str = ""
    status_reason_code: str = ""
    status_reason_message: Optional[str] = ""
    total_count: Optional[int] = -1
    completed_count: Optional[int] = -1
    sender_id: Optional[str] = ""
    receiver_id: Optional[str] = ""
    is_msg_encrypted: bool = False
    meta: dict = {}
