# -*- coding: utf-8 -*-
{
    "name": "Registration Portal User",
    "category": "G2P",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenG2P",
    "website": "https://openg2p.org",
    "license": "Other OSI approved licence",
    'depends': ['g2p_service_provider_portal_base','g2p_odk_importer'],
    'data': [
        'security/ir.model.access.csv',
        'views/registration_user_view.xml',
        "views/odk_app_user.xml",
    ],
    "assets": {
        "web.assets_frontend": [],
        "web.assets_common": [],
        "website.assets_wysiwyg": [],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}

