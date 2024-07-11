# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class G2PDeduplicationCriteria(models.Model):
    _name = "g2p.registry.id.deduplication_criteria"

    name = fields.Char(string="Criteria Name", required=True)
    grp_id_types = fields.Many2many("g2p.id.type", "g2p_registry_id_dedup_grp", string="ID Types")
    ind_id_types = fields.Many2many("g2p.id.type", "g2p_registry_id_dedup_ind", string="ID Types")
