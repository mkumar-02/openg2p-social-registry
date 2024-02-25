from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .header import Header, ResponseHeader


class QueryRequest(BaseModel):
    expression: str


class SearchCriteriaRequest(BaseModel):
    version: str = "1.0.0"
    reg_type: str = ""
    reg_event_type: str = ""
    query_type: str = ""
    query: str


class SingleSearchRequest(BaseModel):
    reference_id: str = ""
    timestamp: datetime = datetime.utcnow()
    search_criteria: SearchCriteriaRequest
    locale: str = "eng"


class RegistrySearchRequest(BaseModel):
    transaction_id: str = ""
    search_request: List[SingleSearchRequest]


class RegistrySearchHttpRequest(BaseModel):
    signature: Optional[str]
    header: Header
    message: RegistrySearchRequest


class QueryDataResponse(BaseModel):
    version: str = "1.0.0"
    reg_type: str
    reg_event_type: str
    reg_record_type: str
    reg_record: Optional[dict] = {}


class SingleSearchResponse(BaseModel):
    reference_id: str
    timestamp: datetime = datetime.utcnow()
    status: str
    status_reason_code: str = None
    status_reason_message: Optional[str] = ""
    data: Optional[QueryDataResponse]
    locale: str = "eng"


class RegistrySearchResponse(BaseModel):
    transaction_id: str
    correlation_id: str
    search_response: List[SingleSearchResponse]


class RegistrySearchHttpResponse(BaseModel):
    signature: Optional[str]
    header: ResponseHeader
    message: RegistrySearchResponse
