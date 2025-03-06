import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute("UPDATE res_partner SET unique_id = temp_unique_id ")
    cr.execute("ALTER TABLE res_partner DROP COLUMN temp_unique_id")
    _logger.info("Post Migration Sucessfully........................")
