"""mwh revenue block_number should not be unique

Revision ID: d0a062963ccc
Revises: 3561ae89f72e
Create Date: 2025-06-15 21:56:22.754086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'd0a062963ccc'
down_revision: Union[str, None] = '3561ae89f72e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_mwh_revenue_block_number'), table_name='mwh_revenue')
    op.create_index(op.f('ix_mwh_revenue_block_number'), 'mwh_revenue', ['block_number'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_mwh_revenue_block_number'), table_name='mwh_revenue')
    op.create_index(op.f('ix_mwh_revenue_block_number'), 'mwh_revenue', ['block_number'], unique=True)
    # ### end Alembic commands ###
