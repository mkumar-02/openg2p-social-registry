import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if version == "17.0.1.3.0":
        _logger.info(f"Pre-Migration started for version {version}")
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
                pending_id, registrant_id = record
                cr.execute(
                    """
                    INSERT INTO g2p_que_background_task (
                        create_date, write_date, worker_type, worker_payload,
                        task_status, number_of_attempts, queued_datetime
                    ) VALUES (
                        now(), now(), 'id_generation_request_worker',
                        %s, 'PENDING', 0, now()
                    )
                """,
                    (f'{{"registrant_id": {registrant_id}}}',),
                )

        # Step 2: Add temp_unique_id column if not exists
        cr.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'res_partner'
                    AND column_name = 'temp_unique_id'
                ) THEN
                    ALTER TABLE res_partner ADD COLUMN temp_unique_id VARCHAR;
                END IF;
            END $$;
        """
        )

        # Step 3: Copy ref_id to temp_unique_id only if ref_id exists
        cr.execute(
            """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'res_partner' AND column_name = 'ref_id'
            """
        )
        if cr.fetchone()[0] > 0:
            cr.execute("UPDATE res_partner SET temp_unique_id = ref_id WHERE ref_id IS NOT NULL")

        # Step 4: Remove cron job if it exists
        cr.execute("SELECT COUNT(*) FROM ir_cron WHERE cron_name = 'Reference ID Generation Cron Job'")
        if cr.fetchone()[0] > 0:
            cr.execute("DELETE FROM ir_cron WHERE cron_name = 'Reference ID Generation Cron Job'")

        # Step 5: Remove related server actions if they exist
        cr.execute("SELECT COUNT(*) FROM ir_act_server WHERE model_name = 'g2p.pending.reference_id'")
        if cr.fetchone()[0] > 0:
            cr.execute("DELETE FROM ir_act_server WHERE model_name = 'g2p.pending.reference_id'")

        # Step 6: Remove fields from res.config.settings if they exist
        cr.execute("SELECT COUNT(*) FROM ir_model_fields WHERE model = 'res.config.settings'")
        if cr.fetchone()[0] > 0:
            cr.execute(
                """
                DELETE FROM ir_model_fields
                WHERE model = 'res.config.settings'
                AND name IN (
                    'id_generator_base_api_url', 'id_generator_auth_url',
                    'id_generator_auth_client_id', 'id_generator_auth_client_secret',
                    'id_generator_auth_grant_type', 'id_generator_api_timeout'
                )
            """
            )

        # Step 7: Remove ir_config_parameter keys if they exist
        cr.execute("SELECT COUNT(*) FROM ir_config_parameter WHERE key LIKE 'id_generator_%'")
        if cr.fetchone()[0] > 0:
            cr.execute("DELETE FROM ir_config_parameter WHERE key LIKE 'id_generator_%'")

        # Step 8: Remove XML-defined records if they exist
        cr.execute(
            """
            SELECT COUNT(*) FROM ir_model_data
            WHERE model IN ('g2p.pending.reference_id', 'g2p.reference_id.config')
        """
        )
        if cr.fetchone()[0] > 0:
            cr.execute(
                """
                DELETE FROM ir_model_data
                WHERE model IN ('g2p.pending.reference_id', 'g2p.reference_id.config')
            """
            )

        # Step 9: Remove models from ir_model if they exist
        cr.execute(
            """
            SELECT COUNT(*) FROM ir_model
            WHERE model IN ('g2p.pending.reference_id', 'g2p.reference_id.config')
        """
        )
        if cr.fetchone()[0] > 0:
            cr.execute(
                """
                DELETE FROM ir_model
                WHERE model IN ('g2p.pending.reference_id', 'g2p.reference_id.config')
            """
            )

        # Step 10: Drop tables if they exist
        cr.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'g2p_pending_reference_id'"
        )
        if cr.fetchone()[0] > 0:
            cr.execute("DROP TABLE g2p_pending_reference_id CASCADE")

        cr.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'g2p_reference_id_config'"
        )
        if cr.fetchone()[0] > 0:
            cr.execute("DROP TABLE g2p_reference_id_config CASCADE")

        _logger.info(f"Pre-Migration completed successfully for version {version}")
