# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    grp_deduplication_id_types_ids = fields.Many2many(
        "g2p.id.type",
    )

    ind_deduplication_id_types_ids = fields.Many2many("g2p.id.type", "g2p_registry_id_ind_deduplcation")

    def set_values(self):
        res = super().set_values()
        self.env["ir.config_parameter"].set_param(
            "g2p_registry_id_deduplication.grp_deduplication_id_types_ids",
            self.grp_deduplication_id_types_ids.ids,
        )
        self.env["ir.config_parameter"].set_param(
            "g2p_registry_id_deduplication.ind_deduplication_id_types_ids",
            self.ind_deduplication_id_types_ids.ids,
        )
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        grp_id_types = ir_config.get_param("g2p_registry_id_deduplication.grp_deduplication_id_types_ids")
        ind_id_types = ir_config.get_param("g2p_registry_id_deduplication.ind_deduplication_id_types_ids")
        res.update(grp_deduplication_id_types_ids=[(6, 0, literal_eval(grp_id_types))])
        res.update(ind_deduplication_id_types_ids=[(6, 0, literal_eval(ind_id_types))])
        return res
