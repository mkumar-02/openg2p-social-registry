# -*- coding: utf-8 -*-
# from odoo import http


# class G2pServiceProviderPortalBase(http.Controller):
#     @http.route('/g2p_service_provider_portal_base/g2p_service_provider_portal_base', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/g2p_service_provider_portal_base/g2p_service_provider_portal_base/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('g2p_service_provider_portal_base.listing', {
#             'root': '/g2p_service_provider_portal_base/g2p_service_provider_portal_base',
#             'objects': http.request.env['g2p_service_provider_portal_base.g2p_service_provider_portal_base'].search([]),
#         })

#     @http.route('/g2p_service_provider_portal_base/g2p_service_provider_portal_base/objects/<model("g2p_service_provider_portal_base.g2p_service_provider_portal_base"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('g2p_service_provider_portal_base.object', {
#             'object': obj
#         })

