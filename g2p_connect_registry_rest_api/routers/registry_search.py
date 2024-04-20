import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.graphql_base import GraphQLControllerMixin

from ..schema import schema
from ..schemas.registry_search import (
    QueryDataResponse,
    RegistrySearchHttpRequest,
    RegistrySearchHttpResponse,
    RegistrySearchResponse,
    ResponseHeader,
    SingleSearchResponse,
)

_logger = logging.getLogger(__name__)


g2p_connect_router = APIRouter(tags=["g2p-connect registry"])

cache_jwks = {}


@g2p_connect_router.post(
    "/registry/sync/search",
    responses={200: {"model": RegistrySearchHttpResponse}},
)
async def registry_search(
    data: RegistrySearchHttpRequest,
    env: Annotated[Environment, Depends(odoo_env)],
    Authorization: Annotated[str, Header()] = "",
):

    token = Authorization.removeprefix("Bearer")

    if not token:
        raise HTTPException(401, "Not authenticated.")

    iss_uri = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("g2p_dci_api_server.g2p_social_registry_auth_iss", "")
    )

    jwks_uri = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("g2p_dci_api_server.g2p_social_registry_auth_jwks_uri", "")
    )

    verified, payload = verify_and_decode_signature(token, iss_uri, jwks_uri)

    if not verified:
        raise HTTPException(status_code=401, detail="Invalid Access Token")

    message_id = data.header.message_id
    transaction_id = data.message.transaction_id
    search_requests = data.message.search_request

    today_isoformat = datetime.now(timezone.utc).isoformat()
    str(uuid.uuid4())

    # Process search requests and modify search_responses
    search_responses = []
    process_search_requests(search_requests, today_isoformat, search_responses)

    return RegistrySearchHttpResponse(
        signature=data.signature,
        header=ResponseHeader(
            message_id=message_id,
            action="on-search",
            status="",
            sender_id="",
            receiver_id="",
            total_count=-1,
            completed_count=0,
        ),
        message=RegistrySearchResponse(
            transaction_id=transaction_id,
            search_response=[
                SingleSearchResponse(
                    reference_id=res.get("reference_id", None),
                    timestamp=today_isoformat,
                    status="",
                    data=QueryDataResponse(
                        reg_type=res.get("data")["reg_type"]
                        if res.get("data")["reg_type"]
                        else None,
                        reg_record_type=res.get("data")["reg_record_type"]
                        if res.get("data")["reg_record_type"]
                        else None,
                        reg_records=res.get("data")["reg_record"]
                        if res.get("data")["reg_record"]
                        else {},
                    ),
                    locale="eng",
                )
                for res in search_responses
            ],
        ),
    )


def verify_and_decode_signature(token, iss_uri, jwks_uri):
    try:
        if not cache_jwks:
            jwks_res = requests.get(jwks_uri)
            jwks_res.raise_for_status()
            cache_jwks.update(jwks_res.json())

        return True, jwt.decode(
            token,
            cache_jwks,
            options={
                "verify_aud": False,
                "verify_iss": False,
                "verify_sub": False,
            },
        )
    except Exception as e:
        return False, str(e)


def process_query(query_type, query, graphql_schema):

    if query_type == "graphql":

        response = GraphQLControllerMixin._process_request(
            None, graphql_schema, data={"query": query}
        )

        response_error = json.loads(response.data).get("errors", "")
        if response_error:
            _logger.error("Error in the query result", response_error)
            raise HTTPException(404, response_error[0]["message"])

        return json.loads(response.data)["data"]

    return False, {}


def process_search_requests(search_requests, today_isoformat, search_responses):
    for req in search_requests:

        search_criteria = req.search_criteria
        query_type = search_criteria.query_type

        reg_type = search_criteria.reg_type

        reference_id = req.reference_id
        query = search_criteria.query

        # Process Query
        query_result = process_query(query_type, query, schema.graphql_schema)

        if query_result:
            search_responses.append(
                {
                    "reference_id": reference_id,
                    "timestamp": today_isoformat,
                    "status": "succ",
                    "status_reason_code": "string",
                    "status_reason_message": "",
                    "data": {
                        # "version": "1.0.0",
                        "reg_event_type": "string",
                        "reg_record_type": "person",
                        "reg_type": reg_type,
                        "reg_record": query_result,
                    },
                    "locale": "eng",
                }
            )

    return search_responses
