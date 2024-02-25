from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    g2p_social_registry_auth_iss = fields.Char(
        config_parameter="g2p_dci_api_server.g2p_social_registry_auth_iss"
    )

    g2p_social_registry_auth_jwks_uri = fields.Char(
        config_parameter="g2p_dci_api_server.g2p_social_registry_auth_jwks_uri"
    )
