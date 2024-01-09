import graphene

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.graphql_base import OdooObjectType

class Partner(OdooObjectType):
    name = graphene.String()
    email = graphene.String()

class Query(graphene.ObjectType):
    all_partners = graphene.List(
        graphene.NonNull(Partner),
        required=True,
        limit=graphene.Int()
    )

    @staticmethod
    def resolve_all_partners(root, info, limit=None):
        domain = []
        return info.context["env"]["res.partner"].search(
            domain, limit=limit
        )
    

schema = graphene.Schema(query=Query, mutation=None)