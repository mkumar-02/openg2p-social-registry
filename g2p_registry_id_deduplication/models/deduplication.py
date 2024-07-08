# Part of OpenG2P Social Registry. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class G2PDeduplicationCriteria(models.Model):
    _name = "g2p.registry.id.deduplication_criteria"

    name = fields.Char(string="Criteria Name", required=True)
    id_types = fields.Many2many("g2p.id.type")
