from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_restx.reqparse import RequestParser

import db
from .models import *

bp_api = Blueprint("api", __name__)
api = Api(bp_api)
ns_api = api.namespace("api", path="/api/v1")

partial_user_fields = api.model('PartialUser', {
    'id': fields.String(),
    'name': fields.String(),
    'discord_id': fields.String(),
    'money': fields.String(),
    'created_at': fields.DateTime(),
    'guild_id': fields.String(),
})

member_fields = api.model('ClubMember', {
    'nick': fields.String(),
    'joined_at': fields.DateTime(),
    'user': fields.Nested(partial_user_fields)
})

partial_member_fields = api.model('PartialClubMember', {
    'id': fields.String(),
    'nick': fields.String(),
    'joined_at': fields.DateTime(),
})

club_fields = api.model('Club', {
    'id': fields.String(),
    'name': fields.String(),
    'description': fields.String(),
    'members': fields.List(fields.Nested(partial_member_fields))
})

partial_club_fields = api.model('PartialClub', {
    'id': fields.String(),
    'name': fields.String(),
    'description': fields.String(),
})
user_fields = api.model('User', {
    'id': fields.String(),
    'name': fields.String(),
    'discord_id': fields.String(),
    'money': fields.String(),
    'created_at': fields.DateTime(),
    'guild_id': fields.String(),
    'clubs': fields.List(fields.Nested(partial_club_fields))
})

item_fields = api.model('Item', {
    'id': fields.String(),
    'name': fields.String(),
    'description': fields.String(),
    'object_id': fields.String(),
    'seller': fields.Nested(partial_user_fields),
    'cost': fields.String(),
    'object_type': fields.Integer()
})
partial_item = api.model('PartialItem', {
    'id': fields.String(),
    'name': fields.String(),
    'description': fields.String(),
    'object_id': fields.String(),
    'cost': fields.String(),
    'object_type': fields.Integer()
})

transaction_fields = api.model('Transaction', {
    'id': fields.String(),
    'buyer': fields.Nested(partial_user_fields),
    'seller': fields.Nested(partial_user_fields),
    'item': fields.Nested(partial_item),
    'cost': fields.String(),
})

clubs_request_parser = RequestParser()
clubs_request_parser.add_argument("name", type=str, store_missing=False, location="json")
clubs_request_parser.add_argument("description", type=str, store_missing=False, location="json")
clubs_request_parser.add_argument("guild_id", type=int, store_missing=False, location="json", required=False)

user_request_parser = RequestParser()
user_request_parser.add_argument("id", type=int, store_missing=False, location="json")

user_create_req_parser = RequestParser()
user_create_req_parser.add_argument("discord_id", type=int, location="json")
user_create_req_parser.add_argument("name", type=str, location="json")
user_create_req_parser.add_argument("guild_id", type=int, location="json", required=False)

club_patch_parser = RequestParser()
club_patch_parser.add_argument("name", type=str, location="json")
club_patch_parser.add_argument("description", type=str, location="json")
club_patch_parser.add_argument("money", type=str, location="json")

user_patch_parser = RequestParser()
user_patch_parser.add_argument("money", type=str, location="json")

member_patch_parser = RequestParser()
member_patch_parser.add_argument("nick", type=str, location="json")

item_patch_parser = RequestParser()
item_patch_parser.add_argument("name", type=str, location="json", store_missing=False)
item_patch_parser.add_argument("description", type=str, location="json", store_missing=False)
item_patch_parser.add_argument("cost", type=int, location="json", store_missing=False)

item_add_parser = RequestParser()
item_add_parser.add_argument("object_id", type=int, location="json")
item_add_parser.add_argument("object_type", type=int, location="json")
item_add_parser.add_argument("cost", type=int, location="json")
item_add_parser.add_argument("seller_id", type=int, location="json")
item_add_parser.add_argument("name", type=str, location="json")
item_add_parser.add_argument("description", type=str, location="json")

transaction_create_parser = RequestParser()
transaction_create_parser.add_argument("item_id", type=int, location="json")
transaction_create_parser.add_argument("seller_id", type=int, location="json")
transaction_create_parser.add_argument("buyer_id", type=int, location="json")
# transaction_create_parser.add_argument("cost", type=int, location="json")


@ns_api.route("/clubs/<int:club_id>", endpoint="club")  # noqa
class ClubResource(Resource):
    @staticmethod
    @ns_api.marshal_with(club_fields, envelope="club")
    def get(club_id):
        return Club.query.filter_by(id=club_id).first_or_404()

    @staticmethod
    @ns_api.marshal_with(club_fields, envelope="club")
    @ns_api.expect(club_patch_parser)
    def patch(club_id):
        data = club_patch_parser.parse_args()
        Club.query.filter_by(id=club_id).update(data)
        db.session.commit()
        return Club.query.filter_by(id=club_id).first_or_404()

    @staticmethod
    def delete(club_id):
        club = Club.query.filter_by(id=club_id).first_or_404()
        db.session.delete(club)
        db.session.commit()
        return {"message": "Success"}, 200


@ns_api.route("/clubs/", endpoint="clubs")
class ClubsResource(Resource):
    @staticmethod
    @ns_api.expect(clubs_request_parser)
    @ns_api.marshal_with(club_fields, envelope="club")
    def post():
        data = clubs_request_parser.parse_args(strict=True)
        club = Club(data['name'], data['description'], data['guild_id'])
        db.session.add(club)
        db.session.commit()
        return club, 201

    @staticmethod
    @ns_api.marshal_list_with(club_fields, envelope="clubs")
    def get():
        return Club.query.all()


@ns_api.route("/clubs/<int:club_id>/members", endpoint="members")  # noqa
class ClubMembersResource(Resource):
    @staticmethod
    @ns_api.marshal_list_with(member_fields, envelope="members")
    def get(club_id):
        return Club.query.filter_by(id=club_id).first_or_404().members

    @staticmethod
    @ns_api.expect(user_request_parser)
    @ns_api.marshal_with(member_fields, envelope="member")
    def post(club_id):
        data = user_request_parser.parse_args(strict=True)
        user = User.query.filter_by(id=data['id']).first()
        if not user:
            return {"message": "User not found"}, 404
        member = ClubMember(user.id, club_id)
        db.session.add(member)
        db.session.commit()
        return member, 201


@ns_api.route("/clubs/<int:club_id>/members/<int:member_id>", endpoint="member")  # noqa
class ClubMemberResource(Resource):
    @staticmethod
    @ns_api.marshal_with(member_fields, envelope="member")
    def get(club_id, member_id):
        return ClubMember.query.filter_by(id=member_id, club_id=club_id).first_or_404()

    @staticmethod
    @ns_api.expect(member_patch_parser)
    @ns_api.marshal_with(member_fields, envelope="member")
    def patch(club_id, member_id):
        data = member_patch_parser.parse_args()
        ClubMember.query.filter_by(id=member_id, club_id=club_id).update(data)
        db.session.commit()
        return ClubMember.query.filter_by(id=member_id, club_id=club_id).first_or_404()

    @staticmethod
    def delete(club_id, member_id):
        member = ClubMember.query.filter_by(id=member_id, club_id=club_id).first_or_404()
        db.session.delete(member)
        db.session.commit()
        return {"message": "Success"}, 200


@ns_api.route("/users/<int:user_id>", endpoint="user")  # noqa
class UserResource(Resource):
    @staticmethod
    @ns_api.marshal_with(user_fields, envelope="user")
    def get(user_id):
        return User.query.filter_by(id=user_id).first_or_404()

    @staticmethod
    @ns_api.expect(user_patch_parser)
    @ns_api.marshal_with(user_fields, envelope="user")
    def patch(user_id):
        data = user_patch_parser.parse_args()
        User.query.filter_by(id=user_id).update(data)
        db.session.commit()
        return User.query.filter_by(id=user_id).first_or_404()

    @staticmethod
    def delete(user_id):
        user = User.query.filter_by(id=user_id).first_or_404()
        db.session.delete(user)
        db.session.commit()
        return {"message": "Success"}, 200


@ns_api.route("/users/", endpoint="users")
class UsersResource(Resource):
    @staticmethod
    @ns_api.expect(user_create_req_parser)
    def post():
        data = user_create_req_parser.parse_args(strict=True)
        if not User.query.filter_by(discord_id=data['discord_id']).first():
            new_user = User(data['name'], data['discord_id'], data['guild_id'])
            db.session.add(new_user)
            db.session.commit()
            return ns_api.marshal(new_user, user_fields, envelope="user"), 201
        else:
            return {"message": "User already exists"}, 400

    @staticmethod
    @ns_api.marshal_list_with(user_fields, envelope="users")
    def get():
        return User.query.all()


@ns_api.route("/marketplace/items/", endpoint="items")
class MarketplaceItemsResource(Resource):
    @staticmethod
    @ns_api.marshal_with(item_fields, as_list=True)
    def get():
        return Item.query.all()

    @staticmethod
    @ns_api.expect(item_add_parser)
    @ns_api.marshal_with(item_fields)
    def post():
        data = item_add_parser.parse_args(strict=True)
        new_item = Item(data["name"], data["description"], data["cost"], data["object_id"], ObjectType(data["object_type"]), data["seller_id"])
        db.session.add(new_item)
        db.session.commit()
        return new_item


@ns_api.route("/marketplace/items/<int:item_id>", endpoint="item")  # noqa
class MarketplaceItemResource(Resource):
    @staticmethod
    @ns_api.marshal_with(item_fields)
    def get(item_id):
        return Item.query.filter_by(id=item_id).first_or_404()

    @staticmethod
    @ns_api.expect(item_patch_parser)
    @ns_api.marshal_with(item_fields)
    def patch(item_id):
        data = item_patch_parser.parse_args()
        Item.query.filter_by(id=item_id).update(data)
        db.session.commit()
        return Item.query.filter_by(id=item_id).first_or_404()

    @staticmethod
    def delete(item_id):
        new_item = Item.query.filter_by(id=item_id).first_or_404()
        db.session.delete(new_item)
        db.session.commit()
        return {'message': "Success!"}


@ns_api.route("/marketplace/transactions")
class TransactionsResource(Resource):
    @staticmethod
    @ns_api.expect(transaction_create_parser)
    @ns_api.marshal_with(transaction_fields)
    def post():
        data = transaction_create_parser.parse_args(strict=True)
        new_transaction = Transaction(data["item_id"], data["seller_id"], data["buyer_id"])
        db.session.add(new_transaction)
        db.session.flush()
        new_transaction.transact()
        db.session.commit()
        return new_transaction, 201

    @staticmethod
    @ns_api.marshal_with(transaction_fields, as_list=True)
    def get():
        return Transaction.query.all()


@ns_api.route("/marketplace/transactions/<int:transaction_id>")
class TransactionResource(Resource):
    @staticmethod
    @ns_api.marshal_with(transaction_fields)
    def get(transaction_id):
        return Transaction.query.filter_by(id=transaction_id).first_or_404()
