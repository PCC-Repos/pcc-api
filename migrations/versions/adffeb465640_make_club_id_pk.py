"""Make club_id pk

Revision ID: adffeb465640
Revises: 089eb92b2b90
Create Date: 2021-09-17 17:28:22.850093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adffeb465640'
down_revision = '089eb92b2b90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('club_members', 'club_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('club_members', 'club_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    # ### end Alembic commands ###
