"""add team fields

Revision ID: add_team_fields
Revises: 
Create Date: 2024-12-18 10:08:17.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_team_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Agregar las columnas team y centro_cultivo a la tabla repairs
    op.add_column('repairs', sa.Column('team', sa.String(length=50), nullable=True))
    op.add_column('repairs', sa.Column('centro_cultivo', sa.String(length=100), nullable=True))

def downgrade():
    # Eliminar las columnas en caso de rollback
    op.drop_column('repairs', 'centro_cultivo')
    op.drop_column('repairs', 'team')
