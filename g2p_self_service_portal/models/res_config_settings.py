from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    self_service_logo = fields.Many2one(
        "ir.attachment",
        config_parameter="g2p_self_service_portal.self_service_logo_attachment",
    )

    self_service_form = fields.Many2one(
        "website.page", config_parameter="g2p_self_service_portal.self_service_form"
    )

    @api.constrains("self_service_form")
    def update_form_template(self):
        form_view = self.self_service_form.view_id
        if form_view:
            form_view_template = form_view.arch_db
            form_view.write(
                {
                    "arch_db": form_view_template.replace(
                        "website.layout",
                        "g2p_self_service_portal.self_service_form_template",
                    )
                }
            )
