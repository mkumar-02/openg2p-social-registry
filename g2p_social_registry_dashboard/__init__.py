# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.
from . import models

from odoo import _
from odoo.exceptions import MissingError


def init_materialized_view(env):
    """
    Initializes the res_partner_dashboard_data materialized view.
    """

    cr = env.cr
    cr.execute(
        """
        SELECT
            matviewname
        FROM
            pg_matviews
        WHERE
            matviewname = 'res_partner_dashboard_data';
    """
    )
    check = cr.fetchone()

    if check:
        return {}

    query = """
        CREATE MATERIALIZED VIEW res_partner_dashboard_data AS
        SELECT
            company_id,
            jsonb_build_object(
                'individual_count', COUNT(id)
                    FILTER (WHERE is_registrant = True AND is_group = False),
                'group_count', COUNT(id)
                    FILTER (WHERE is_registrant = True AND is_group = True)
            ) AS total_registrant,
            jsonb_build_object(
                'male_count', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND gender = 'Male'
                    ),
                'female_count', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND gender = 'Female'
                    )
            ) AS gender_spec,
            jsonb_build_object(
                'below_18', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND EXTRACT(YEAR FROM AGE(birthdate)) < 18
                    ),
                '18_to_30', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND EXTRACT(YEAR FROM AGE(birthdate)) BETWEEN 18 AND 30
                    ),
                '31_to_40', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND EXTRACT(YEAR FROM AGE(birthdate)) BETWEEN 31 AND 40
                    ),
                '41_to_50', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND EXTRACT(YEAR FROM AGE(birthdate)) BETWEEN 41 AND 50
                    ),
                'above_50', COUNT(id)
                    FILTER (
                        WHERE is_registrant = True
                        AND is_group = False
                        AND EXTRACT(YEAR FROM AGE(birthdate)) > 50
                    )
            ) AS age_distribution
        FROM
            res_partner
        GROUP BY
            company_id;
    """

    try:
        cr.execute(query)
    except Exception as exc:
        raise MissingError(
            _(
                "Failed to create the materialized view 'res_partner_dashboard_data'.\n"
                "Please create it manually by running the required SQL query with proper permissions."
            )
        ) from exc


def drop_materialized_view(env):
    """
    Drop the res_partner_dashboard_data materialized view.
    """

    cr = env.cr
    try:
        cr.execute(
            """
            DROP MATERIALIZED VIEW IF EXISTS
                res_partner_dashboard_data;
            """
        )

    except Exception as exc:
        raise Exception(
            _(
                "Failed to drop the materialized view 'res_partner_dashboard_data'.\n"
                "Please manually delete the view."
            )
        ) from exc
