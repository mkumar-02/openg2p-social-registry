# Part of OpenG2P Social Registry. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_duplicate = fields.Boolean(default=False)

    def deduplicate_registrants(self):
        is_group = self._context.get("default_is_group")

        id_types = self.get_id_types()
        self.reset_duplicate_flag(is_group)

        if not is_group:
            ind_duplicate_ids = []
            duplicates = self.get_duplicate_registrants(
                is_group, id_types, group_condition="group_kind.name IS NULL"
            )

            for duplicate in duplicates:
                duplicate_partner_ids_str = duplicate.get("partner_ids")
                ind_duplicate_ids += duplicate_partner_ids_str.split(",")

            updated_ind_duplicate_ids = list(set(ind_duplicate_ids))
            self.mark_registrant_as_duplicated(updated_ind_duplicate_ids)

            message = f"{len(updated_ind_duplicate_ids)} individuals"

        else:
            group_duplicate_ids = []
            member_duplicate_ids = []
            grouped_kinds = self.get_grouped_kinds()
            for kind in grouped_kinds:
                group_kind_name = kind.get("kind")
                group_ids_str = kind.get("group_ids")

                group_duplicates = self.get_duplicate_registrants(
                    is_group, id_types, group_condition=f"group_kind.name = '{group_kind_name}'"
                )

                # Group Duplicate
                for duplicate in group_duplicates:
                    duplicate_partner_ids_str = duplicate.get("partner_ids")
                    group_duplicate_ids += duplicate_partner_ids_str.split(",")

                updated_grp_duplicate_ids = list(set(group_duplicate_ids))
                self.mark_registrant_as_duplicated(updated_grp_duplicate_ids)

                # Group Member Duplicate
                group_member_duplicates = self.get_duplicate_group_members(group_ids_str, id_types)
                for member_duplicate in group_member_duplicates:
                    duplicate_partner_ids_str = member_duplicate.get("partner_ids")
                    member_duplicate_ids += duplicate_partner_ids_str.split(",")

                updated_member_duplicate_ids = list(set(member_duplicate_ids))
                self.mark_registrant_as_duplicated(updated_member_duplicate_ids)

            if len(updated_grp_duplicate_ids) > 0 and len(updated_member_duplicate_ids) > 0:
                message = f"{len(updated_grp_duplicate_ids)} groups and \
                    {len(updated_member_duplicate_ids)} group members"
            elif len(updated_member_duplicate_ids) > 0:
                message = f"{len(updated_member_duplicate_ids)} group members"
            else:
                message = f"{len(updated_grp_duplicate_ids)} groups"

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Duplicate"),
                "message": f"{message} are duplicated.",
                "sticky": False,
                "type": "success",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def get_id_types(self):
        id_types = []

        dedup_criteria_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("g2p_registry_id_deduplication.dedup_criteria_id", default=None)
        )

        if not dedup_criteria_id:
            raise UserError(_("No deduplication criteria configured. Please configure it in the settings."))

        dedup_criteria = self.env["g2p.registry.id.deduplication_criteria"].search(
            [("id", "=", dedup_criteria_id)], limit=1
        )

        if not dedup_criteria:
            raise UserError(_("Deduplication configuration not found."))

        for id_type in dedup_criteria.id_types:
            id_types.append(id_type.name)

        if len(id_types) < 1:
            raise UserError(_("No ID Types found in the Deduplication Configuration."))

        return tuple(id_types) if len(id_types) != 1 else f"('{id_types[0]}')"

    def mark_registrant_as_duplicated(self, partner_ids):
        for partner in partner_ids:
            registrant = self.browse(int(partner))
            if registrant:
                registrant.update({"is_duplicate": True})

    def reset_duplicate_flag(self, is_group):
        query = f"""
            UPDATE res_partner
            SET is_duplicate = FALSE
            WHERE is_registrant = TRUE AND is_group = {is_group}
        """
        _logger.debug("DB Query: %s" % query)

        try:
            self._cr.execute(query)  # pylint: disable=sql-injection
        except Exception as e:
            _logger.error("Database Query Error: %s", e)
            raise UserError(_("Database Query Error: %s") % e) from None

    def get_grouped_kinds(self):
        query = """
            SELECT
            group_kind.name AS kind, STRING_AGG(partner.id::text, ',')
            AS group_ids
            FROM res_partner AS partner
            LEFT JOIN g2p_group_kind AS group_kind ON group_kind.id = partner.kind
            WHERE is_registrant = TRUE AND is_group = TRUE
            GROUP BY group_kind.name
        """

        try:
            self._cr.execute(query)  # pylint: disable=sql-injection
            grouped_kinds = self._cr.dictfetchall()
            return grouped_kinds
        except Exception as e:
            _logger.error("Database Query Error: %s", e)
            raise UserError(_("Database Query Error: %s") % e) from None

    def get_duplicate_registrants(self, is_group, id_types, group_condition):
        query = f"""
            SELECT
            reg_id.value AS id_value, STRING_AGG(partner.id::text, ',')
            AS partner_ids
            FROM res_partner AS partner
            INNER JOIN g2p_reg_id AS reg_id ON reg_id.partner_id = partner.id
            JOIN g2p_id_type AS id_type ON id_type.id = reg_id.id_type
            LEFT JOIN g2p_group_kind AS group_kind ON group_kind.id = partner.kind
            WHERE is_registrant = TRUE AND id_type.name IN {id_types} AND is_group = {is_group}
            AND {group_condition}
            GROUP BY reg_id.value
            HAVING COUNT(partner.id) > 1
        """

        try:
            self._cr.execute(query)  # pylint: disable=sql-injection
            individual_duplicates = self._cr.dictfetchall()
            return individual_duplicates
        except Exception as e:
            _logger.error("Database Query Error: %s", e)
            raise UserError(_("Database Query Error: %s") % e) from None

    def get_duplicate_group_members(self, group_ids, id_types):
        query = f"""
            SELECT
            reg_id.value AS id_value, STRING_AGG(group_member.group::text, ',')
            AS partner_ids
            FROM res_partner AS partner
            JOIN g2p_group_membership AS group_member ON partner.id = group_member.individual
            INNER JOIN g2p_reg_id AS reg_id ON reg_id.partner_id = partner.id
            JOIN g2p_id_type AS id_type ON id_type.id = reg_id.id_type
            WHERE partner.is_registrant = TRUE AND id_type.name IN {id_types}
            AND group_member.group IN ({group_ids})
            GROUP BY reg_id.value
            HAVING COUNT(partner.id) > 1
        """

        try:
            self._cr.execute(query)  # pylint: disable=sql-injection
            group_duplicates = self._cr.dictfetchall()
            return group_duplicates
        except Exception as e:
            _logger.error("Database Query Error: %s", e)
            raise UserError(_("Database Query Error: %s") % e) from None
