from odoo import fields
from odoo.tests import TransactionCase


class TestG2PQueIDGeneration(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create test partners to be used as registrants
        self.partner1 = self.env["res.partner"].create({"name": "Test Partner 1"})
        self.partner2 = self.env["res.partner"].create({"name": "Test Partner 2"})

        # Create an instance of the G2PQueIDGeneration model
        self.g2p_queue = self.env["g2p.que.id.generation"].create(
            {
                "registrant_id": self.partner1.id,
                "id_generation_request_status": "pending",
                "id_generation_update_status": "not_applicable",
            }
        )

    def test_create_g2p_queue_record(self):
        """
        Test that a G2PQueIDGeneration record is created successfully with valid data.
        """
        self.assertTrue(self.g2p_queue, "G2PQueIDGeneration record was not created.")
        self.assertEqual(
            self.g2p_queue.registrant_id,
            str(self.partner1.id),
            "Registrant ID does not match the expected partner.",
        )
        self.assertEqual(
            self.g2p_queue.id_generation_request_status,
            "pending",
            "Default ID Generation Request Status should be 'pending'.",
        )
        self.assertEqual(
            self.g2p_queue.id_generation_update_status,
            "not_applicable",
            "Default ID Generation Update Status should be 'not_applicable'.",
        )
        self.assertEqual(
            self.g2p_queue.number_of_attempts_request, 0, "Default number_of_attempts_request should be 0."
        )
        self.assertEqual(
            self.g2p_queue.number_of_attempts_update, 0, "Default number_of_attempts_update should be 0."
        )
        self.assertFalse(
            self.g2p_queue.last_attempt_error_code_request,
            "last_attempt_error_code_request should be empty by default.",
        )
        self.assertFalse(
            self.g2p_queue.last_attempt_error_code_update,
            "last_attempt_error_code_update should be empty by default.",
        )
        self.assertFalse(
            self.g2p_queue.last_attempt_datetime_request,
            "last_attempt_datetime_request should be empty by default.",
        )
        self.assertFalse(
            self.g2p_queue.last_attempt_datetime_update,
            "last_attempt_datetime_update should be empty by default.",
        )
        self.assertTrue(self.g2p_queue.queued_datetime, "queued_datetime should be set by default.")

    def test_multiple_g2p_queue_records(self):
        """
        Test creating multiple G2PQueIDGeneration records with unique registrant_ids.
        """
        record2 = self.env["g2p.que.id.generation"].create(
            {
                "registrant_id": self.partner2.id,
                "id_generation_request_status": "approved",
                "id_generation_update_status": "in_progress",
                "last_attempt_error_code_request": "ERR001",
                "last_attempt_datetime_request": fields.Datetime.now(),
            }
        )

        self.assertTrue(record2, "Second G2PQueIDGeneration record was not created.")
        self.assertEqual(
            record2.registrant_id,
            str(self.partner2.id),
            "Registrant ID for the second record does not match the expected partner.",
        )
        self.assertEqual(
            record2.id_generation_request_status,
            "approved",
            "ID Generation Request Status should be 'approved'.",
        )
        self.assertEqual(
            record2.id_generation_update_status,
            "in_progress",
            "ID Generation Update Status should be 'in_progress'.",
        )

        self.assertEqual(
            record2.last_attempt_error_code_request,
            "ERR001",
            "last_attempt_error_code_request should be 'ERR001'.",
        )
        self.assertTrue(record2.last_attempt_datetime_request, "last_attempt_datetime_request should be set.")

    def test_field_assignments(self):
        """
        Test that fields can be updated correctly after record creation.
        """
        self.g2p_queue.write(
            {
                "id_generation_request_status": "approved",
                "id_generation_update_status": "completed",
                "number_of_attempts_request": 1,
            }
        )

        self.assertEqual(
            self.g2p_queue.id_generation_request_status,
            "approved",
            "ID Generation Request Status should be updated to 'approved'.",
        )
        self.assertEqual(
            self.g2p_queue.id_generation_update_status,
            "completed",
            "ID Generation Update Status should be updated to 'completed'.",
        )
        self.assertEqual(
            self.g2p_queue.number_of_attempts_request, 1, "number_of_attempts_request should be updated to 1."
        )

    def test_default_values_on_creation(self):
        """
        Test that default values are correctly set when creating a new record without specifying them.
        """
        new_record = self.env["g2p.que.id.generation"].create(
            {
                "registrant_id": self.partner2.id,
            }
        )

        self.assertEqual(
            new_record.id_generation_request_status,
            "pending",
            "Default ID Generation Request Status should be 'pending'.",
        )
        self.assertEqual(
            new_record.id_generation_update_status,
            "not_applicable",
            "Default ID Generation Update Status should be 'not_applicable'.",
        )
        self.assertEqual(
            new_record.number_of_attempts_request, 0, "Default number_of_attempts_request should be 0."
        )
        self.assertEqual(
            new_record.number_of_attempts_update, 0, "Default number_of_attempts_update should be 0."
        )
        self.assertFalse(
            new_record.last_attempt_error_code_request,
            "last_attempt_error_code_request should be empty by default.",
        )
        self.assertFalse(
            new_record.last_attempt_error_code_update,
            "last_attempt_error_code_update should be empty by default.",
        )
        self.assertFalse(
            new_record.last_attempt_datetime_request,
            "last_attempt_datetime_request should be empty by default.",
        )
        self.assertFalse(
            new_record.last_attempt_datetime_update,
            "last_attempt_datetime_update should be empty by default.",
        )
        self.assertTrue(new_record.queued_datetime, "queued_datetime should be set by default.")
