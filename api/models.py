import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.ext.associationproxy import association_proxy

from db import BaseModel, db
from id_generator import IDGenerator

id_generator = IDGenerator.create(1609459200, 1, 1)


class ObjectType(Enum):
    MEMBER = 1

    def __int__(self):
        return self.value


class Club(BaseModel):
    __tablename__ = "clubs"

    id = db.Column(BIGINT, nullable=False, primary_key=True, default=id_generator.create_id)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    description = db.Column(db.String)
    money = db.Column(BIGINT, default=25000000)
    guild_id = db.Column(BIGINT, nullable=False)
    members = db.relationship("ClubMember", back_populates="club", uselist=True, lazy="select", cascade="all, delete")

    # member_ids = db.Column(db.ARRAY(BIGINT), db.ARRAY(db.ForeignKey("club_members.id")))

    def __init__(self, name: str, description: str, guild_id: int):
        self.name = name
        self.description = description
        self.guild_id = guild_id


class User(BaseModel):
    __tablename__ = "users"
    id = db.Column(BIGINT, nullable=False, primary_key=True, default=id_generator.create_id)
    discord_id = db.Column(BIGINT, nullable=False)
    money = db.Column(BIGINT, default=100000)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    guild_id = db.Column(BIGINT)
    name = db.Column(db.String)
    _clubs = db.relationship("ClubMember", uselist=True, back_populates="user", lazy="select", cascade="all, delete")
    clubs = association_proxy("_clubs", "club")

    def __init__(self, name: str, discord_id: int, guild_id: int):
        self.name = name
        self.discord_id = discord_id
        self.guild_id = guild_id


class ClubMember(BaseModel):
    __tablename__ = "club_members"
    user = db.relationship("User", back_populates="_clubs")
    id = db.Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    nick = db.Column(db.String)
    club = db.relationship("Club", back_populates="members")
    club_id = db.Column(BIGINT, ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.now)
    value = db.Column(BIGINT)

    def __init__(self, _id, club_id):
        self.id = _id
        self.club_id = club_id
        self.value = 0


class Item(BaseModel):
    __tablename__ = "items"
    id = db.Column(BIGINT, nullable=False, primary_key=True, default=id_generator.create_id)
    cost = db.Column(BIGINT)
    object_id = db.Column(BIGINT, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    object_type = db.Column(db.Enum(ObjectType), nullable=False)
    seller_id = db.Column(BIGINT, ForeignKey("users.id"), nullable=False)
    seller = db.relationship("User", lazy="select")
    stock = db.Column(db.Integer, default=1)

    def __init__(self, name: str, description: str, cost: int, object_id: int, object_type: ObjectType, seller_id: int):
        self.name = name
        self.description = description
        self.cost = cost
        self.object_id = object_id
        self.object_type = object_type
        self.seller_id = seller_id


class Transaction(BaseModel):
    __tablename__ = "transactions"
    id = db.Column(BIGINT, nullable=False, primary_key=True, default=id_generator.create_id)
    item_id = db.Column(BIGINT, ForeignKey("items.id"), nullable=False)
    seller_id = db.Column(BIGINT, ForeignKey("users.id"), nullable=False)
    buyer_id = db.Column(BIGINT, ForeignKey("users.id"), nullable=False)
    seller = db.relationship("User", foreign_keys=[seller_id])
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    item = db.relationship("Item", foreign_keys=[item_id])

    def __init__(self, item_id: int, seller_id: int, buyer_id: int):
        self.item_id = item_id
        self.seller_id = seller_id
        self.buyer_id = buyer_id

    def transact(self):
        self.seller.money += self.item.cost
        self.buyer.money -= self.item.cost
        self.item.stock -= 1
