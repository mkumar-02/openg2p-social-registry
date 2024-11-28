# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.
from . import models


def post_init_hook(env):
    partners = env["res.partner"].search([("is_registrant", "=", True), ("unique_id", "=", False)])
    for partner in partners:
        env["g2p.que.id.generation"].create(
            {
                "registrant_id": partner.id,
                "id_generation_request_status": "pending",
                "id_generation_update_status": "not_applicable",
            }
        )
