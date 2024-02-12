# Part of OpenG2P Social Registry. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenG2P API: DCI Server",
    "summary": "RESTful API routes for OpenG2P",
    "category": "G2P",
    "version": "17.0.1.0.0",
    "author": "OpenG2P",
    "development_status": "Alpha",
    "website": "https://openg2p.org",
    "license": "Other OSI approved licence",
    "depends": [
        "base",
        "g2p_registry_base",
        "g2p_registry_individual",
        "fastapi",
        "graphql_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_params.xml",
    ],
    "external_dependencies": {"python": ["PyLD", "pyjwt>=2.4.0"]},
    "application": True,
    "auto_install": False,
    "installable": True,
}
