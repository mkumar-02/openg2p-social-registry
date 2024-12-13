from odoo import fields, models


class G2PQueIDGeneration(models.Model):
    _name = "g2p.que.id.generation"
    _description = "G2P Queue ID Generation"

    registrant_id = fields.Char(
        required=True,
    )

    id_generation_request_status = fields.Selection(
        selection=[
            ("PENDING", "PENDING"),
            ("COMPLETED", "COMPLETED"),
            ("FAILED", "FAILED"),
        ],
        required=True,
        default="PENDING",
    )

    id_generation_update_status = fields.Selection(
        selection=[
            ("NOT_APPLICABLE", "NOT_APPLICABLE"),
            ("PENDING", "PENDING"),
            ("COMPLETED", "COMPLETED"),
            ("FAILED", "FAILED"),
        ],
        required=True,
        default="NOT_APPLICABLE",
    )

    queued_datetime = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
    )

    number_of_attempts_request = fields.Integer(
        required=True,
        default=0,
    )

    number_of_attempts_update = fields.Integer(
        required=True,
        default=0,
    )

    last_attempt_error_code_request = fields.Char()

    last_attempt_error_code_update = fields.Char()

    last_attempt_datetime_request = fields.Datetime()

    last_attempt_datetime_update = fields.Datetime()

    _sql_constraints = [
        ("registrant_id_uniq", "UNIQUE(registrant_id)", "registrant_id is an unique identifier!"),
    ]
