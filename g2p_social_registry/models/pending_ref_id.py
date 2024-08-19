import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FallbackTable(models.Model):
    _name = "g2p.pending.reference_id"

    registrant_id = fields.Many2one("res.partner")
    ref_id = fields.Char()
    status = fields.Selection([("failed", "Failed"), ("success", "Success")], default="failed")

    @api.model
    def retry_generate_ref_id(self):
        records = self.search([("status", "=", "failed")])
        for record in records:
            partner = record.registrant_id
            if partner:
                partner.generate_ref_id()
                if partner.ref_id:
                    record.status = "success"
                    record.ref_id = partner.ref_id

    def generate_ref_id_for_selected(self):
        for rec in self.env.context.get("active_ids"):
            partner = self.env["res.partner"].browse(rec)
            registrant = self.env["g2p.pending.reference_id"].search([("registrant_id", "=", rec)], limit=1)

            if not partner.ref_id:
                partner.generate_ref_id()

                if partner.ref_id and registrant:
                    registrant.status = "success"
                    registrant.ref_id = partner.ref_id
