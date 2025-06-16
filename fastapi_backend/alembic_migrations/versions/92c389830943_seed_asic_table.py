"""seed asic table

Revision ID: 92c389830943
Revises: 89cff00948cb
Create Date: 2025-06-15 19:52:31.463906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy

from uuid import uuid4
from app.models import Base


asic = sa.Table(
    'asic',
    Base.metadata,
    sa.Column('id', sa.UUID, primary_key=True),
    sa.Column('asic_slug', sa.String, index=True, nullable=False),
    sa.Column('asic_name', sa.String, nullable=False),
    sa.Column('asic_hash_rate', sa.Float, nullable=False),
    sa.Column('asic_power', sa.Float, nullable=False),
    schema=None,  # omit or set if you use a non-default schema
    extend_existing=True
)

# revision identifiers, used by Alembic.
revision: str = '92c389830943'
down_revision: Union[str, None] = '89cff00948cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(asic, [
        {'id': uuid4(), 'asic_slug': 's23_hyd', 'asic_name': 'Antminer S23 Hyd', 'asic_hash_rate': 580*1000000000000, 'asic_power': 5510},
        {'id': uuid4(), 'asic_slug': 's21_pro', 'asic_name': 'Antminer S21 Pro', 'asic_hash_rate': 234*1000000000000, 'asic_power': 3510},
        {'id': uuid4(), 'asic_slug': 's19j_xp', 'asic_name': 'Antminer S19j XP', 'asic_hash_rate': 151*1000000000000, 'asic_power': 3247},
    ])


def downgrade() -> None:
    op.execute("DELETE FROM asic")

