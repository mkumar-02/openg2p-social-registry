from odoo import fields, models


class G2PSelfServiceOauthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    g2p_self_service_allowed = fields.Boolean("Allowed in Self Service Portal", default=False)
