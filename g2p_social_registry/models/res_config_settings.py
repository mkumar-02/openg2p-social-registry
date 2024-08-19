# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    id_generator_base_api_url = fields.Char()
    id_generator_auth_url = fields.Char()
    id_generator_auth_client_id = fields.Char()
    id_generator_auth_client_secret = fields.Char()
    id_generator_auth_grant_type = fields.Char()
    id_generator_api_timeout = fields.Integer()

    def set_values(self):
        res = super().set_values()
        config = self.env["g2p.reference_id.config"].get_config()

        config.write(
            {
                "base_api_url": self.id_generator_base_api_url,
                "auth_url": self.id_generator_auth_url,
                "auth_client_id": self.id_generator_auth_client_id,
                "auth_client_secret": self.id_generator_auth_client_secret,
                "auth_grant_type": self.id_generator_auth_grant_type,
                "api_timeout": self.id_generator_api_timeout,
            }
        )

        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        config = self.env["g2p.reference_id.config"].get_config()

        res.update(
            {
                "id_generator_base_api_url": config.base_api_url,
                "id_generator_auth_url": config.auth_url,
                "id_generator_auth_client_id": config.auth_client_id,
                "id_generator_auth_client_secret": config.auth_client_secret,
                "id_generator_auth_grant_type": config.auth_grant_type,
                "id_generator_api_timeout": config.api_timeout,
            }
        )

        return res

    def add_missing_ref_id_to_retry(self):
        query = """
            SELECT id FROM res_partner
            WHERE is_registrant = TRUE AND ref_id is Null
        """

        pending_ref_id_model = self.env["g2p.pending.reference_id"]

        try:
            self._cr.execute(query)  # pylint: disable=sql-injection

            for rec in [record[0] for record in (self._cr.fetchall())]:
                if not pending_ref_id_model.search([("registrant_id", "=", rec)], limit=1):
                    pending_ref_id_model.create({"registrant_id": rec, "status": "failed"})

        except Exception as e:
            _logger.error("Database Query Error: %s", e)
            raise UserError(_("Database Query Error: %s") % e) from None
