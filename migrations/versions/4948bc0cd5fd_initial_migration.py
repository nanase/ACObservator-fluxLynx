"""Initial migration

Revision ID: 4948bc0cd5fd
Revises: 
Create Date: 2024-11-27 23:31:26.004955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4948bc0cd5fd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sensor_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('unit', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_types_id'), 'sensor_types', ['id'], unique=False)
    op.create_table('observed_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('sensor_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['sensor_type_id'], ['sensor_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_observed_values_created_at'), 'observed_values', ['created_at'], unique=False)
    op.create_index(op.f('ix_observed_values_id'), 'observed_values', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_observed_values_id'), table_name='observed_values')
    op.drop_index(op.f('ix_observed_values_created_at'), table_name='observed_values')
    op.drop_table('observed_values')
    op.drop_index(op.f('ix_sensor_types_id'), table_name='sensor_types')
    op.drop_table('sensor_types')
    # ### end Alembic commands ###