"""rename _email column to email

Revision ID: 001
Revises: 
Create Date: 2024-04-01 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Rename the column
    op.alter_column('users', '_email',
                    new_column_name='email',
                    existing_type=sa.String(120))

def downgrade():
    # Rename the column back
    op.alter_column('users', 'email',
                    new_column_name='_email',
                    existing_type=sa.String(120)) 