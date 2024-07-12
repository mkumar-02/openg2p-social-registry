# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    dedup_criteria_id = fields.Many2one(
        "g2p.registry.id.deduplication_criteria",
        config_parameter="g2p_registry_id_deduplication.dedup_criteria_id",
    )
