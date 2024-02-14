from odoo import fields, models

from ..controllers import social_registry_api_router


class G2PDCIServerFastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("social_registry", "Social Registry Endpoint")],
        ondelete={"social_registry": "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == "social_registry":
            return [social_registry_api_router]
        return super()._get_fastapi_routers()
