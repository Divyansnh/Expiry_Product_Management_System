"""rename _email column to email

Revision ID: 40245329be70
Revises: 001
Create Date: 2024-04-02 12:21:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '40245329be70'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Rename the column
    op.execute('ALTER TABLE users RENAME COLUMN _email TO email')


def downgrade():
    # Rename the column back
    op.execute('ALTER TABLE users RENAME COLUMN email TO _email')
