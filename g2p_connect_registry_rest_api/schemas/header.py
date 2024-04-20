from datetime import datetime

from pydantic import BaseModel


class Header(BaseModel):
    version: str = "1.0.0"
    message_id: str = ""
    message_ts: datetime = datetime.utcnow()
    action: str = "search"
    sender_id: str = ""
    sender_uri: str | None = ""
    receiver_id: str | None = ""
    total_count: int
    is_msg_encrypted: bool = False
    meta: dict = {}


class ResponseHeader(BaseModel):
    version: str = "1.0.0"
    message_id: str
    message_ts: datetime = datetime.now()
    action: str = "on-search"
    status: str = ""
    status_reason_code: str = ""
    status_reason_message: str | None = ""
    total_count: int | None = -1
    completed_count: int | None = -1
    sender_id: str | None = ""
    receiver_id: str | None = ""
    is_msg_encrypted: bool = False
    meta: dict = {}
