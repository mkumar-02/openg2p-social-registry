from odoo import models


class DashboardCron(models.Model):
    _inherit = "ir.cron"

    def _refresh_dashboard_materialized_view(self):
        self.env.cr.execute("REFRESH MATERIALIZED VIEW res_partner_dashboard_data")
