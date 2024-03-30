import logging

from werkzeug.exceptions import Forbidden, Unauthorized

from odoo import _, http
from odoo.http import request

from odoo.addons.auth_oidc.controllers.main import OpenIDLogin
from odoo.addons.web.controllers.home import Home

_logger = logging.getLogger(__name__)


class SelfServiceController(http.Controller):
    @http.route(["/selfservice"], type="http", auth="public", website=True)
    def self_service_root(self, **kwargs):
        if request.session and request.session.uid:
            return request.redirect("/selfservice/apply")
        else:
            return request.redirect("/selfservice/login")

    @http.route(["/selfservice/login"], type="http", auth="public", website=True)
    def self_service_login(self, **kwargs):
        if request.session and request.session.uid:
            return request.redirect("/selfservice/apply")
        request.params["redirect"] = "/"
        context = {}

        providers = []
        try:
            providers = OpenIDLogin().list_providers(domain=[("g2p_self_service_allowed", "=", True)])
        except Exception:
            providers = OpenIDLogin().list_providers()

        context.update(dict(providers=providers))

        if request.httprequest.method == "POST":
            res = Home().web_login(**kwargs)

            if not request.params["login_success"]:
                context["error"] = "Invalid Credentials"
                return request.render("g2p_self_service_portal.login_page", qcontext=context)

            return res

        return request.render("g2p_self_service_portal.login_page", qcontext=context)

    @http.route(["/selfservice/logo"], type="http", auth="public", website=True)
    def self_service_logo(self, **kwargs):
        config = request.env["ir.config_parameter"].sudo()
        attachment_id = config.get_param("g2p_self_service_portal.self_service_logo_attachment")
        return request.redirect("/web/content/%s" % attachment_id)

    @http.route(["/selfservice/myprofile"], type="http", auth="public", website=True)
    def self_service_profile(self, **kwargs):
        if request.session and request.session.uid:
            current_partner = request.env.user.partner_id
            return request.render(
                "g2p_self_service_portal.profile_page",
                {
                    "current_partner": current_partner,
                },
            )

    @http.route(["/selfservice/apply"], type="http", auth="user", website=True)
    def self_service_home(self, **kwargs):
        self.self_service_check_roles("REGISTRANT")

        config = request.env["ir.config_parameter"].sudo()

        form_id = config.get_param("g2p_self_service_portal.self_service_form", None)

        view_id = request.env["website.page"].sudo().browse(int(form_id)).view_id

        return request.render(
            view_id.id
            # {"programs": myprograms, "data": data},
        )

    @http.route(
        ["/selfservice/submit"],
        type="http",
        auth="user",
        website=True,
        csrf=False,
    )
    def self_service_form_submit(self, **kwargs):
        self.self_service_check_roles("REGISTRANT")
        _logger.info(kwargs)
        self.get_field_to_exclude(kwargs)
        return request.render(
            "g2p_self_service_portal.self_service_form_submitted",
            {
                "user": request.env.user.given_name,
            },
        )

    def self_service_check_roles(self, role_to_check):
        # And add further role checks and return types
        if role_to_check == "REGISTRANT":
            if not request.session or not request.env.user:
                raise Unauthorized(_("User is not logged in"))
            if not request.env.user.partner_id.is_registrant:
                raise Forbidden(_("User is not allowed to access the portal"))

    def get_field_to_exclude(self, data):
        current_partner = request.env.user.partner_id
        keys = []
        for key in data:
            if key in current_partner:
                current_partner[key] = data[key]
                keys.append(key)

        return keys
