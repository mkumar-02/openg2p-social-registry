import itertools
import logging
from datetime import date

from odoo import models

_logger = logging.getLogger(__name__)


class g2p_social_registry_id_deduplication(models.Model):
    _inherit = "g2p.deduplication.manager.id_dedup"

    def deduplicate_beneficiaries(self, type_registry, beneficiaries, states):
        duplicate_beneficiaries = []
        # duplicates
        if str(type_registry) == "group":
            duplicate_beneficiaries = self._check_duplicate_by_group_with_individual(beneficiaries)
        else:
            duplicate_beneficiaries = self._check_duplicate_by_individual(beneficiaries)
        return len(duplicate_beneficiaries)

    def _check_duplicate_by_group_with_individual(self, beneficiaries):
        """
        This method is used to check if there are any duplicates among the individuals docs.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.info("-" * 100)
        group_ids = beneficiaries.mapped("id")
        group_memberships = self.env["g2p.group.membership"].search([("group", "in", group_ids)])

        group = beneficiaries
        _logger.info("group_memberships: %s", group_memberships)

        individuals_ids = [rec.individual.id for rec in group_memberships]
        _logger.info("Checking ID  Duplicates for: %s", individuals_ids)

        individual_id_docs = {}
        # Check ID Documents of each individual
        for i in group_memberships:
            for x in i.individual.reg_ids:
                if x.id_type in self.supported_id_document_types and (
                    (not x.expiry_date) or x.expiry_date > date.today()
                ):
                    # KEY : VALUE PAIR
                    id_doc_id_with_id_type_and_value = {x.id: x.id_type.name + "-" + x.value}
                    individual_id_docs.update(id_doc_id_with_id_type_and_value)

        # Check ID Docs of each group
        for ix in group:
            for x in ix.reg_ids:
                if x.id_type in self.supported_id_document_types and (
                    (not x.expiry_date) or x.expiry_date > date.today()
                ):
                    id_doc_id_with_id_type_and_value = {x.id: x.id_type.name + "-" + x.value}
                    individual_id_docs.update(id_doc_id_with_id_type_and_value)

        _logger.info("Individual ID Documents: %s", individual_id_docs)
        rev_dict = {}
        for key, value in individual_id_docs.items():
            rev_dict.setdefault(value, set()).add(key)

        duplicate_ids = filter(lambda x: len(x) > 1, rev_dict.values())
        duplicate_ids = list(duplicate_ids)
        duplicate_ids = list(itertools.chain.from_iterable(duplicate_ids))
        _logger.info("Reg_id IDS with Duplicated ID Documents: %s", duplicate_ids)

        duplicated_doc_ids = self.env["g2p.reg.id"].search([("id", "in", duplicate_ids)])
        individual_ids = [x.partner_id.id for x in duplicated_doc_ids]
        individual_ids = list(dict.fromkeys(individual_ids))
        self._update_duplicates(individual_ids)

        return individual_ids

    def _check_duplicate_by_individual(self, beneficiaries):
        """
        This method is used to check if there are any duplicates
        among the individuals id docs.
        :param beneficiary_ids: The beneficiaries.
        :return:
        """
        _logger.info("-" * 100)
        individuals = beneficiaries
        _logger.info("Checking ID Document Duplicates for: %s", individuals)

        individual_id_docs = {}
        # Check ID Documents of each individual
        for i in individuals:
            for x in i.reg_ids:
                if x.id_type in self.supported_id_document_types and (
                    (not x.expiry_date) or x.expiry_date > date.today()
                ):
                    id_doc_id_with_id_type_and_value = {x.id: x.id_type.name + "-" + x.value}
                    individual_id_docs.update(id_doc_id_with_id_type_and_value)

        _logger.info("Individual ID Documents: %s", individual_id_docs)
        rev_dict = {}
        for key, value in individual_id_docs.items():
            rev_dict.setdefault(value, set()).add(key)

        duplicate_ids = filter(lambda x: len(x) > 1, rev_dict.values())
        duplicate_ids = list(duplicate_ids)
        duplicate_ids = list(itertools.chain.from_iterable(duplicate_ids))
        _logger.info("Reg_id IDS with Duplicated ID Documents: %s", duplicate_ids)

        duplicated_doc_ids = self.env["g2p.reg.id"].search([("id", "in", duplicate_ids)])
        individual_ids = [x.partner_id.id for x in duplicated_doc_ids]
        individual_ids = list(dict.fromkeys(individual_ids))
        _logger.info("Individual IDS with Duplicated ID Documents: %s", individual_ids)
        self._update_duplicates(individual_ids)
        return individual_ids

    def _update_duplicates(self, duplicate_ids):
        """
        Update duplicate individual records.
        :param duplicate_ids: IDs of duplicate individuals.
        """
        individual_duplicates = self.env["res.partner"].sudo().browse(duplicate_ids)
        for duplicate in individual_duplicates:
            duplicate.write({"is_duplicate": True})
