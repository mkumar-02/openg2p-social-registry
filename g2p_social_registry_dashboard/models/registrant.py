from odoo import api, models


class ResPartnerDashboard(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_dashboard_data(self):
        """Fetch data from materialized view and prepare it for charts."""
        company_id = self.env.company.id

        # Fetch data from the materialized view
        query = """
            SELECT total_registrant, gender_spec, age_distribution
            FROM res_partner_dashboard_data
            WHERE company_id = %s
        """
        self.env.cr.execute(query, (company_id,))
        result = self.env.cr.fetchone()

        if not result:
            return {
                "total_individuals": 0,
                "total_groups": 0,
                "gender_distribution": {"male": 0, "female": 0},
                "age_distribution": {
                    "below_18": 0,
                    "18_to_30": 0,
                    "31_to_40": 0,
                    "41_to_50": 0,
                    "above_50": 0,
                },
            }

        total_registrant, gender_spec, age_distribution = result

        # Return formatted data
        return {
            "total_individuals": total_registrant.get("individual_count", 0),
            "total_groups": total_registrant.get("group_count", 0),
            "gender_distribution": {
                "male": gender_spec.get("male_count", 0),
                "female": gender_spec.get("female_count", 0),
            },
            "age_distribution": {
                "Below 18": age_distribution.get("below_18", 0),
                "18 to 30": age_distribution.get("18_to_30", 0),
                "31 to 40": age_distribution.get("31_to_40", 0),
                "41 to 50": age_distribution.get("41_to_50", 0),
                "Above 50": age_distribution.get("above_50", 0),
            },
        }
