"""add asic & mwh_revenue tables

Revision ID: 89cff00948cb
Revises: d817540773ca
Create Date: 2025-06-15 19:52:07.844030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '89cff00948cb'
down_revision: Union[str, None] = 'd817540773ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('asic',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('asic_slug', sa.String(), nullable=True),
    sa.Column('asic_name', sa.String(), nullable=False),
    sa.Column('asic_hash_rate', sa.Float(), nullable=False),
    sa.Column('asic_power', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asic_asic_slug'), 'asic', ['asic_slug'], unique=False)
    op.create_table('mwh_revenue',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('asic_id', sa.UUID(), nullable=False),
    sa.Column('mwh_btc_revenue', sa.Float(), nullable=False),
    sa.Column('mwh_usd_revenue', sa.Float(), nullable=False),
    sa.Column('mwh_revenue_timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['asic_id'], ['asic.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mwh_revenue')
    op.drop_index(op.f('ix_asic_asic_slug'), table_name='asic')
    op.drop_table('asic')
    # ### end Alembic commands ###
