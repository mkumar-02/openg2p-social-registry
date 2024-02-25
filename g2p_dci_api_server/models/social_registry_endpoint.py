from odoo import fields, models

from ..controllers import social_registry_api_router


class G2PDCIServerFastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("socialregistry", "Social Registry Endpoint")],
        ondelete={"socialregistry": "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == "socialregistry":
            return [social_registry_api_router]
        return super()._get_fastapi_routers()
