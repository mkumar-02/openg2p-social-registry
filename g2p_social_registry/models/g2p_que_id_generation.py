from odoo import models, fields, api
from datetime import datetime


class G2PQueIDGeneration(models.Model):
    _name = "g2p.que.id.generation"
    _description = "G2P Queue ID Generation"

    registrant_id = fields.Char(
        string="Registrant ID",
        required=True,
        unique=True,
    )

    id_generation_request_status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string="ID Generation Request Status",
        required=True,
        default='pending',
    )

    id_generation_update_status = fields.Selection(
        selection=[
            ('not_applicable', 'Not Applicable'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        string="ID Generation Update Status",
        required=True,
        default='not_applicable',
    )

    queued_datetime = fields.Datetime(
        string="Queued Datetime",
        required=True,
        default=fields.Datetime.now,
    )

    number_of_attempts_request = fields.Integer(
        string="Number of Attempts (Request)",
        required=True,
        default=0,
    )

    number_of_attempts_update = fields.Integer(
        string="Number of Attempts (Update)",
        required=True,
        default=0,
    )

    last_attempt_error_code_request = fields.Char(
        string="Last Attempt Error Code (Request)"
    )

    last_attempt_error_code_update = fields.Char(
        string="Last Attempt Error Code (Update)"
    )

    last_attempt_datetime_request = fields.Datetime(
        string="Last Attempt Datetime (Request)"
    )

    last_attempt_datetime_update = fields.Datetime(
        string="Last Attempt Datetime (Update)"
    )

