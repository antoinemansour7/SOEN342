"""Added attendees and capacity

Revision ID: fbfb96e1e09e
Revises: e1d182c596b9
Create Date: 2024-10-18 16:52:33.049474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbfb96e1e09e'
down_revision = 'e1d182c596b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('attendees', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('offering_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('offering', schema=None) as batch_op:
        batch_op.add_column(sa.Column('available_spots', sa.Integer(), nullable=False, server_default='0'))
        batch_op.alter_column('lesson_type',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.alter_column('location',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('start_time',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.DateTime(),
               existing_nullable=False)
        batch_op.alter_column('end_time',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.DateTime(),
               existing_nullable=False)
        batch_op.alter_column('maximum_capacity',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('is_available')
        batch_op.drop_column('mode')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offering', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mode', sa.VARCHAR(length=50), nullable=False))
        batch_op.add_column(sa.Column('is_available', sa.BOOLEAN(), nullable=True))
        batch_op.alter_column('maximum_capacity',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('end_time',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.alter_column('start_time',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.alter_column('location',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
        batch_op.alter_column('lesson_type',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('available_spots')

    with op.batch_alter_table('attendees', schema=None) as batch_op:
        batch_op.alter_column('offering_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###