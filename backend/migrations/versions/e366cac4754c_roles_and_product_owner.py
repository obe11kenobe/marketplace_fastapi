"""roles and product owner

Revision ID: e366cac4754c
Revises: 6fa096e79d60
Create Date: 2026-08-10 19:31:56.320111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e366cac4754c'
down_revision: Union[str, Sequence[str], None] = '6fa096e79d60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='user'))

    with op.batch_alter_table('products') as batch:
        batch.add_column(sa.Column('seller_id', sa.Integer(), nullable=False, server_default='0'))
        batch.create_index(batch.f('ix_products_seller_id'), ['seller_id'], unique=False)
        batch.create_foreign_key('fk_products_seller', 'users', ['seller_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('products') as batch:
        batch.drop_constraint('fk_products_seller', type_='foreignkey')
        batch.drop_index(batch.f('ix_products_seller_id'))
        batch.drop_column('seller_id')

    op.drop_column('users', 'role')
