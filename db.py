from typing import TYPE_CHECKING

from flask_sqlalchemy import Model, SQLAlchemy

# M = TypeVar("M", bound='CompletionModel')
#
#
# class CompletionModel(Model):
#     @classmethod
#     def cquery(cls: Type[M]) -> BaseQuery[M]:
#         return cls.query


db = SQLAlchemy()

if TYPE_CHECKING:
    BaseModel = db.make_declarative_base(Model)
else:
    BaseModel = db.Model
