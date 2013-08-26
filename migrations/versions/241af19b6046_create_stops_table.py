"""Create Stops table

Revision ID: 241af19b6046
Revises: None
Create Date: 2013-08-26 07:44:40.841232

"""

# revision identifiers, used by Alembic.
revision = '241af19b6046'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'stops',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('lat', sa.Float),
        sa.Column('lon', sa.Float),
        sa.Column('tag', sa.String),
        sa.Column('title', sa.String),
        sa.Column('stop_id', sa.Integer)
    )


def downgrade():
    op.drop_table('stops')
