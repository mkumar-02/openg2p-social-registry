from datetime import datetime

from pydantic import BaseModel

from .header import Header, ResponseHeader


class QueryRequest(BaseModel):
    expression: str


class SearchCriteriaRequest(BaseModel):
    version: str = "1.0.0"
    reg_type: str = ""
    reg_event_type: str = ""
    query_type: str = "graphql"
    query: str


class SingleSearchRequest(BaseModel):
    reference_id: str = ""
    timestamp: datetime = datetime.utcnow()
    search_criteria: SearchCriteriaRequest
    locale: str = "eng"


class RegistrySearchRequest(BaseModel):
    transaction_id: str = ""
    search_request: list[SingleSearchRequest]


class RegistrySearchHttpRequest(BaseModel):
    signature: str | None = None
    header: Header
    message: RegistrySearchRequest


class QueryDataResponse(BaseModel):
    version: str = "1.0.0"
    reg_type: str | None = None
    reg_event_type: str | None = None
    reg_record_type: str
    reg_records: dict


class SingleSearchResponse(BaseModel):
    reference_id: str
    timestamp: datetime = datetime.now()
    status: str
    status_reason_code: str | None = None
    status_reason_message: str | None = None
    data: QueryDataResponse | None
    locale: str = "eng"


class RegistrySearchResponse(BaseModel):
    transaction_id: str
    correlation_id: str | None = None
    search_response: list[SingleSearchResponse]


class RegistrySearchHttpResponse(BaseModel):
    signature: str | None
    header: ResponseHeader
    message: RegistrySearchResponse
