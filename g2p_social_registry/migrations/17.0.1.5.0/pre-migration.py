import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("Migration started................................... ")

    # Step 1: Migrate pending reference_id records to new queue system
    cr.execute(
        """
        SELECT id, registrant_id
        FROM g2p_pending_reference_id
        WHERE status = 'failed'
        """
    )
    pending_records = cr.fetchall()

    if pending_records:
        _logger.info(f"Migrating {len(pending_records)} pending reference ID records to queue system")
        for record in pending_records:
            pending, registrant_id = record
            current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert the pending ID generation into the new background task queue
            cr.execute(
                """
                INSERT INTO g2p_que_background_task (
                create_date,
                write_date,
                worker_type,
                worker_payload,
                task_status,
                number_of_attempts,
                queued_datetime
                )
                VALUES (
                now(),
                now(),
                'id_generation_request_worker',
                '{"registrant_id": %s}',
                'PENDING',
                0,
                %s
                )
                """,
                (registrant_id, current_date_time),
            )

    # Step 2: Add a temporary column to store ref_id values (if not exists)
    cr.execute(
        """
        DO $$
        BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
            WHERE table_name = 'res_partner'
            AND column_name = 'temp_unique_id')
        THEN
            ALTER TABLE res_partner ADD COLUMN temp_unique_id VARCHAR;
        END IF;
        END $$;
        """
    )

    # Step 3: Copy all values from ref_id to temp_unique_id
    cr.execute("UPDATE res_partner SET temp_unique_id = ref_id")

    # Step 4: Removing cron details and related server actions
    cr.execute(
        """
        DELETE FROM ir_cron
        WHERE cron_name = 'Reference ID Generation Cron Job'
    """
    )

    cr.execute(
        """
        DELETE FROM ir_act_server
        WHERE model_name = 'g2p.pending.reference_id'
    """
    )

    # Step 5: Remove all the fields related to res.config.settings model
    cr.execute(
        """
        DELETE FROM ir_model_fields
        WHERE model = 'res.config.settings'
        AND name IN (
            'id_generator_base_api_url',
            'id_generator_auth_url',
            'id_generator_auth_client_id',
            'id_generator_auth_client_secret',
            'id_generator_auth_grant_type',
            'id_generator_api_timeout'
        )
    """
    )

    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.model.fields'
        AND module = 'g2p_social_registry'
        AND name LIKE 'field_res_config_settings_id_generator%'
    """
    )

    cr.execute(
        """
        DELETE FROM ir_config_parameter
        WHERE key LIKE 'id_generator_%'
    """
    )

    # Step 6: Remove XML-defined records for both models
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE model IN ('g2p.pending.reference_id', 'g2p.reference_id.config')
        OR (model = 'ir.cron' AND res_id IN (
            SELECT id FROM ir_cron
            WHERE cron_name = 'Reference ID Generation Cron Job'
        ))
    """
    )

    # Step 7: Remove from ir_model
    cr.execute(
        """
        DELETE FROM ir_model
        WHERE model IN ('g2p.pending.reference_id', 'g2p.reference_id.config')
    """
    )

    # Step 8: Drop the tables with CASCADE
    cr.execute("DROP TABLE IF EXISTS g2p_pending_reference_id CASCADE")
    cr.execute("DROP TABLE IF EXISTS g2p_reference_id_config CASCADE")

    _logger.info("Migration completed successfully....................")
