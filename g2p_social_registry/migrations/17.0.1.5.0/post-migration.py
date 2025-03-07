import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if version == "17.0.1.3.0":
        _logger.info(f"Post-migration started for {version}")
        # Step 1: Check if temp_unique_id exists before updating unique_id
        cr.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = 'res_partner'
            AND column_name = 'temp_unique_id'
        """
        )
        if cr.fetchone()[0] > 0:
            _logger.info("Updating unique_id with values from temp_unique_id...")
            cr.execute("UPDATE res_partner SET unique_id = temp_unique_id WHERE temp_unique_id IS NOT NULL")

            # Step 2: Drop temp_unique_id column only if it exists
            cr.execute("ALTER TABLE res_partner DROP COLUMN temp_unique_id")

        _logger.info(f"Post-migration completed successfully for version {version}")
