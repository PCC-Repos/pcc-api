from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_restx.reqparse import RequestParser

import db
from .models import *

bp_api = Blueprint("api", __name__)
api = Api(bp_api)
ns_api = api.namespace("api", path="/api/v1")

member_fields = api.model('ClubMember', {
    'id': fields.String(),
    'nick': fields.String(),
    'joined_at': fields.DateTime()
})

user_fields = api.model('User', {
    'id': fields.String(),
    'name': fields.String(),
    'discord_id': fields.String(),
    'money': fields.String(),
    'created_at': fields.DateTime(),
    'guild_id': fields.String()
})

club_fields = api.model('Club', {
    'id': fields.String(),
    'name': fields.String(),
    'description': fields.String(),
    'members': fields.List(fields.Nested(member_fields))
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
    @ns_api.marshal_list_with(member_fields)
    def get(club_id):
        return Club.query.filter_by(id=club_id).first_or_404().members

    @staticmethod
    @ns_api.expect(user_request_parser)
    @ns_api.marshal_with(member_fields)
    def post(club_id):
        data = user_request_parser.parse_args(strict=True)
        user = User.query.filter_by(id=data['id']).first()
        if not user:
            return {"message": "User not found"}, 404
        member = ClubMember(user.id, club_id)
        db.session.add(member)
        db.session.commit()
        return member, 201
    # @staticmethod
    # @ns_api.expect(member_fields)
    #


@ns_api.route("/clubs/<int:club_id>/members/<int:member_id>", endpoint="member")  # noqa
class ClubMemberResource(Resource):
    @staticmethod
    @ns_api.marshal_with(member_fields)
    def get(club_id, member_id):
        return ClubMember.query.filter_by(id=member_id, club_id=club_id).first_or_404()

    @staticmethod
    @ns_api.expect(member_patch_parser)
    @ns_api.marshal_with(member_fields)
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
    @ns_api.marshal_with(user_fields)
    def get(user_id):
        return User.query.filter_by(id=user_id).first_or_404()

    @staticmethod
    @ns_api.expect(user_patch_parser)
    @ns_api.marshal_with(user_fields)
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
            return ns_api.marshal(new_user, user_fields), 201
        else:
            return {"message": "User already exists"}, 400

    @staticmethod
    @ns_api.marshal_list_with(user_fields)
    def get():
        return User.query.all()
