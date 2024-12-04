# Part of OpenG2P Social Registry. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenG2P Social Registry",
    "category": "G2P",
    "version": "17.0.0.0.0",
    "sequence": 1,
    "author": "OpenG2P",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": [
        "g2p_registry_group",
        "g2p_registry_individual",
        "g2p_registry_membership",
    ],
    "external_dependencies": {"python": ["python-jose"]},
    "data": [
        "security/ir.model.access.csv",
        "views/main_view.xml",
        "views/region.xml",
        "views/registrant_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}
