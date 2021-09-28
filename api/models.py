import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT

from db import BaseModel, db
from id_generator import IDGenerator

id_generator = IDGenerator.create(1609459200, 1, 1)


class Club(BaseModel):
    __tablename__ = "clubs"

    id = db.Column(BIGINT, nullable=False, primary_key=True, default=id_generator.create_id)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    description = db.Column(db.String)
    money = db.Column(BIGINT, default=25000000)
    guild_id = db.Column(BIGINT, nullable=False)
    members = db.relationship("ClubMember", uselist=True, backref="clubs", lazy="select")

    # member_ids = db.Column(db.ARRAY(BIGINT), db.ARRAY(db.ForeignKey("club_members.id")))

    def __init__(self, name: str, description: str, guild_id: int):
        self.name = name
        self.description = description
        self.guild_id = guild_id
        print(self.id)


class User(BaseModel):
    __tablename__ = "users"
    id = db.Column(BIGINT, nullable=False, primary_key=True, default=id_generator.create_id)
    discord_id = db.Column(BIGINT, nullable=False, unique=True)
    money = db.Column(BIGINT, default=100000)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    guild_id = db.Column(BIGINT)
    name = db.Column(db.String)

    def __init__(self, name: str, discord_id: int, guild_id: int):
        self.name = name
        self.discord_id = discord_id
        self.guild_id = guild_id


class ClubMember(BaseModel):
    __tablename__ = "club_members"
    user = db.relationship("User")
    id = db.Column(BIGINT, ForeignKey("users.id"), primary_key=True)
    nick = db.Column(db.String)
    club_id = db.Column(BIGINT, ForeignKey("clubs.id"), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.now)

    # __table_args__ = (ForeignKeyConstraint((id, club_id), [User.id, Club.id]),)

    def __init__(self, _id, club_id):
        self.id = _id
        self.club_id = club_id

    # def __init__(self, _id, name, club, joined_at): ...

    # def create(self, name, ): ...

    # def __init__(self): ...

    # def create(self): ...
