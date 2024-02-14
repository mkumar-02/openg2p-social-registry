from pydantic import BaseModel


class RequestAuth(BaseModel):
    client_id: str = ""
    client_secret: str = ""
    grant_type: str = ""
    db_name: str = ""


class ResponseAuth(BaseModel):
    access_token: str
    token_type: str = "Bearer"
