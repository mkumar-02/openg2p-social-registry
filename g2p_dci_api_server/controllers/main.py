import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt

from odoo import fields, models
from odoo.api import Environment
from odoo.http import request

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.graphql_base import GraphQLControllerMixin

from ..models.registry_search import RegistrySearchHttpRequest, RegistrySearchHttpResponse
from ..schema import schema
from ..tools import constants

_logger = logging.getLogger(__name__)


class G2PDCIServerFastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("socialregistry", "Social Registry Endpoint")],
        ondelete={"socialregistry": "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == "socialregistry":
            return [api_router]
        return super()._get_fastapi_routers()


api_router = APIRouter()


cache_jwks = {}


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


def get_auth_header(headers, raise_exception=False):
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        if raise_exception:
            raise HTTPException(status_code=401, detail="Not authenticated")
        else:
            return None
    return auth_header


@api_router.post(
    constants.SYNC_SEARCH_ENDPOINT, response_model=RegistrySearchHttpResponse
)
async def registry_search(
    data: RegistrySearchHttpRequest, env: Annotated[Environment, Depends(odoo_env)]
):

    auth_header = get_auth_header(request.httprequest.headers, raise_exception=True)

    if not auth_header:
        raise HTTPException(status_code=401, detail="Not authenticated")

    access_token = auth_header.replace("Bearer ", "")

    iss_uri = (
        request.env["ir.config_parameter"]
        .sudo()
        .get_param("g2p_dci_api_server.g2p_social_registry_auth_iss", "")
    )

    jwks_uri = (
        request.env["ir.config_parameter"]
        .sudo()
        .get_param("g2p_dci_api_server.g2p_social_registry_auth_jwks_uri", "")
    )

    verified, payload = verify_and_decode_signature(access_token, iss_uri, jwks_uri)

    if not verified:
        raise HTTPException(status_code=401, detail="Invalid Access Token")

    message_id = data.header.message_id
    transaction_id = data.message.transaction_id
    search_requests = data.message.search_request

    today_isoformat = datetime.now(timezone.utc).isoformat()
    correlation_id = str(uuid.uuid4())

    # Process search requests and modify search_responses
    search_responses = []
    process_search_requests(search_requests, today_isoformat, search_responses)

    signature = data.signature

    header = {
        "version": "1.0.0",
        "message_id": message_id,
        "message_ts": today_isoformat,
        "action": "search",
        "status": "succ",
        "status_reason_code": "",
        "status_reason_message": "",
        "total_count": -1,
        "completed_count": -1,
        "sender_id": "",
        "receiver_id": "",
        "is_msg_encrypted": False,
        "meta": {},
    }
    message = {
        "transaction_id": transaction_id,
        "correlation_id": correlation_id,
        "search_response": search_responses,
    }

    return {"signature": signature, "header": header, "message": message}

    # return RegistrySearchHttpResponse(
    #     signature=data.signature,
    #     header=ResponseHeader(
    #         message_id=data.header.message_id,
    #         action="on-search",
    #         status="",
    #         sender_id="",
    #         receiver_id="",
    #         total_count=-1,
    #         completed_count=0
    #     ),
    #     message=RegistrySearchResponse(
    #         transaction_id=data.message.transaction_id,
    #         search_response=[
    #             SingleSearchResponse(
    #                 reference_id=res.reference_id,
    #                 timestamp=today_isoformat,
    #                 status="",
    #                 data=QueryDataResponse(
    #                     reg_type=res.data.reg_type,
    #                     reg_record_type=res.data.reg_record_type,
    #                     reg_records={}
    #                 ),
    #                 locale="eng"

    #             )
    #             for res in request.message.search_response
    #         ]
    #     )
    # )


def process_query(query_type, query, graphql_schema, error=None):

    if query_type == constants.GRAPHQL:

        response = GraphQLControllerMixin._process_request(
            None, graphql_schema, data={"query": query}
        )

        response_error = json.loads(response.data).get("errors", "")
        if response_error:
            _logger.error("Error in the query result", response_error)
            error = True
            return error, response_error

        return error, json.loads(response.data)["data"]

    return False, {}


def process_search_requests(search_requests, today_isoformat, search_responses):
    for req in search_requests:

        search_criteria = req.search_criteria
        query_type = search_criteria.query_type

        reg_type = search_criteria.reg_type

        reference_id = req.reference_id
        query = search_criteria.query

        # Process Query
        error, query_result = process_query(
            query_type, query, schema.graphql_schema, None
        )

        if query_result and not error:
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
