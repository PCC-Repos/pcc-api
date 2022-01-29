"""Make Club -> User two way relationship

Revision ID: 6399928d5df7
Revises: baee1b1c27f8
Create Date: 2022-01-15 16:42:06.050071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6399928d5df7'
down_revision = 'baee1b1c27f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('stock', sa.Integer(), nullable=True))
    op.drop_column('transactions', 'cost')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('cost', sa.BIGINT(), autoincrement=False, nullable=False))
    op.drop_column('items', 'stock')
    # ### end Alembic commands ###
