import graphene
from graphene import List

from odoo.addons.graphql_base import OdooObjectType


class RegIds(OdooObjectType):
    id_type_as_str = graphene.String(required=True)
    value = graphene.String(required=True)


class Partner(OdooObjectType):
    name = graphene.String(required=True)
    given_name = graphene.String()
    family_name = graphene.String()
    addl_name = graphene.String()
    registration_date = graphene.Date()
    address = graphene.String()
    email = graphene.String()
    district = graphene.String()
    birthplace = graphene.String()
    birthdate = graphene.Date()
    gender = graphene.String()
    reg_ids = graphene.Field(List(RegIds))
    phone_no = graphene.String()
    is_group = graphene.Boolean(required=True)


class Query(graphene.ObjectType):
    all_partners = graphene.List(
        Partner,
        required=True,
        limit=graphene.Int(),
        **{key: graphene.String() for key in Partner._meta.fields if key != "reg_ids"}
    )

    total_partners = graphene.Int()

    @staticmethod
    def resolve_all_partners(root, info, limit=None, **kwargs):
        global count
        domain = [(("is_registrant", "=", True))]
        for key, value in kwargs.items():
            if value is not None:
                domain.append((key, "=", value))
        partners = info.context["env"]["res.partner"].sudo().search(domain, limit=limit)

        count = len(partners)
        return partners

    @staticmethod
    def resolve_total_partners(root, info):
        return count


schema = graphene.Schema(query=Query, mutation=None)
