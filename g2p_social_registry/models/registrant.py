import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    region = fields.Many2one("g2p.region")
    ref_id = fields.Char(string="Reference ID", index=True)

    _sql_constraints = [
        ("ref_id_uniq", "UNIQUE(ref_id)", "ref_id is an unique identifier!"),
    ]

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.generate_ref_id()
        return record

    def generate_ref_id(self):
        for rec in self:
            try:
                config = self.env["g2p.reference_id.config"].get_config()

                access_token = config.get_access_token()
                headers = {"Cookie": f"Authorization={access_token}"}

                response = requests.get(config.base_api_url, headers=headers, timeout=config.api_timeout)
                _logger.debug("ID Generator API response: %s", response.text)
                response.raise_for_status()
                res = response.json()

                unique_id = res.get("response")["uin"]
                rec.ref_id = rec.get_ref_id_prefix() + unique_id

            except Exception as e:
                _logger.error("Failed to generate ref_id for partner %s: %s", rec.id, str(e))

                pending_ref_id_model = self.env["g2p.pending.reference_id"]

                if not pending_ref_id_model.search([("registrant_id", "=", rec.id)]):
                    pending_ref_id_model.create({"registrant_id": rec.id, "status": "failed"})

    def get_ref_id_prefix(self):
        for rec in self:
            if not rec.is_registrant:
                return ""
            if rec.is_group:
                return "GRP-"
            return "IND-"
