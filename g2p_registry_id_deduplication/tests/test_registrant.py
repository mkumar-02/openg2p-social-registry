from odoo.tests.common import TransactionCase


class TestResPartnerIDDeduplication(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner_model = self.env["res.partner"]
        self.id_type_model = self.env["g2p.id.type"]
        self.reg_id_model = self.env["g2p.reg.id"]
        self.group_membership_model = self.env["g2p.group.membership"]
        self.dedup_criteria_model = self.env["g2p.registry.id.deduplication_criteria"]
        self.config_parameter_model = self.env["ir.config_parameter"]

        self.individual_1 = self.partner_model.create(
            {"name": "Individual 1", "is_registrant": True, "is_group": False}
        )
        self.individual_2 = self.partner_model.create(
            {"name": "Individual 2", "is_registrant": True, "is_group": False}
        )

        self.group_1 = self.partner_model.create(
            {
                "name": "Group 1",
                "is_registrant": True,
                "is_group": True,
                "group_membership_ids": [(0, 0, {"individual": self.individual_1.id})],
            }
        )
        self.group_2 = self.partner_model.create(
            {
                "name": "Group 2",
                "is_registrant": True,
                "is_group": True,
                "group_membership_ids": [(0, 0, {"individual": self.individual_1.id})],
            }
        )

        self.id_type_1 = self.id_type_model.create({"name": "Household ID"})
        self.id_type_2 = self.id_type_model.create({"name": "National ID"})

        self.reg_id_1 = self.reg_id_model.create(
            {
                "partner_id": self.individual_1.id,
                "id_type": self.id_type_2.id,
                "value": 12345,
                "status": "invalid",
                "description": "Failed",
            }
        )
        self.reg_id_2 = self.reg_id_model.create(
            {
                "partner_id": self.individual_2.id,
                "id_type": self.id_type_2.id,
                "value": 12345,
                "status": "invalid",
                "description": "Failed",
            }
        )
        self.reg_id_3 = self.reg_id_model.create(
            {
                "partner_id": self.group_1.id,
                "id_type": self.id_type_1.id,
                "value": 123,
                "status": "invalid",
                "description": "Failed",
            }
        )
        self.reg_id_4 = self.reg_id_model.create(
            {
                "partner_id": self.group_2.id,
                "id_type": self.id_type_1.id,
                "value": 123,
                "status": "invalid",
                "description": "Failed",
            }
        )

        self.dedup_criteria = self.dedup_criteria_model.create(
            {
                "name": "Test Criteria",
                "ind_id_types": [self.id_type_2.id],
                "grp_id_types": [self.id_type_1.id],
            }
        )

        self.config_parameter_model.set_param(
            "g2p_registry_id_deduplication.dedup_criteria_id", self.dedup_criteria.id
        )

    def test_deduplicate_registrants_individuals(self):
        self.partner_model.with_context(default_is_group=False).deduplicate_registrants()

        self.assertTrue(self.individual_1.is_duplicate)
        self.assertTrue(self.individual_2.is_duplicate)
        self.assertFalse(self.group_1.is_duplicate)
        self.assertFalse(self.group_2.is_duplicate)

    def test_deduplicate_registrants_groups(self):
        self.partner_model.with_context(default_is_group=True).deduplicate_registrants()

        self.assertFalse(self.individual_1.is_duplicate)
        self.assertFalse(self.individual_2.is_duplicate)
        self.assertTrue(self.group_1.is_duplicate)
        self.assertTrue(self.group_2.is_duplicate)
