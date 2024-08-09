# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.
from . import models


def post_init_hook(env):
    partners = env["res.partner"].search([("is_registrant", "=", True), ("ref_id", "=", False)])
    for partner in partners:
        env["g2p.pending.reference_id"].create(
            {"registrant_id": partner.id, "status": "under_process"}
        )
