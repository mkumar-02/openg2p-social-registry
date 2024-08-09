import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FallbackTable(models.Model):
    _name = "g2p.pending.reference_id"

    registrant_id = fields.Many2one("res.partner")
    ref_id = fields.Char()
    status = fields.Selection(
        [("under_process", "Under Process"), ("resolved", "Resolved")], default="under_process"
    )

    @api.model
    def retry_generate_ref_id(self):
        records = self.search([("status", "=", "under_process")])
        for record in records:
            partner = record.registrant_id
            if partner:
                partner.generate_ref_id()
                if partner.ref_id:
                    record.status = "resolved"
                    record.ref_id = partner.ref_id
