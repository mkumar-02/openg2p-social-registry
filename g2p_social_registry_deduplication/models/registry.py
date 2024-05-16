# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    is_duplicate = fields.Boolean("Duplicate")

    def deduplicate_beneficiaries(self):
        record = self.search(
            [
                ("active", "=", True),
                ("is_registrant", "=", True),
                ("is_duplicate", "=", False),
                ("is_group", "=", self._context.get("default_is_group")),
            ]
        )
        id_dedup = self.env["g2p.deduplication.manager.id_dedup"].sudo()
        if self._context.get("default_is_group"):
            type_registry = "group"
        else:
            type_registry = "individual"

        deduplication_config = id_dedup.search([], limit=1)
        message = None
        kind = "success"
        if len(deduplication_config):
            states = ["draft", "enrolled", "eligible", "paused", "duplicated"]
            duplicates = 0
            for el in deduplication_config:
                duplicates += el.deduplicate_beneficiaries(str(type_registry), record, states)

            if duplicates > 0:
                message = _("%s Beneficiaries duplicate.", duplicates)
                kind = "warning"
            else:
                message = _("No duplicates found.")
                kind = "success"
        else:
            raise UserError(_("No ID Deduplication configuration is defined."))

        if message:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Deduplication"),
                    "message": message,
                    "sticky": False,
                    "type": kind,
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }
