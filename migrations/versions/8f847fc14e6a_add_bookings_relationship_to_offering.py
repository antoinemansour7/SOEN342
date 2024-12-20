"""Add bookings relationship to Offering

Revision ID: 8f847fc14e6a
Revises: 1cdd746b64c5
Create Date: 2024-11-03 15:38:43.368055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f847fc14e6a'
down_revision = '1cdd746b64c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offering', schema=None) as batch_op:
        batch_op.alter_column('instructor_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offering', schema=None) as batch_op:
        batch_op.alter_column('instructor_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
