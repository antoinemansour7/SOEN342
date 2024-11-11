"""Added maximum capacity to Offering

Revision ID: 423a5c8f2045
Revises: 
Create Date: 2024-10-18 15:58:38.355840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '423a5c8f2045'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attendees',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('offering_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['offering_id'], ['offering.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    with op.batch_alter_table('offering', schema=None) as batch_op:
        batch_op.add_column(sa.Column('maximum_capacity', sa.Integer(), nullable=True))
        
        batch_op.drop_column('instructor_id')
        batch_op.drop_column('schedule')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('offering', schema=None) as batch_op:
        batch_op.add_column(sa.Column('schedule', sa.VARCHAR(length=100), nullable=False))
        batch_op.add_column(sa.Column('instructor_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_offering_instructor_id', 'user', ['instructor_id'], ['id'])  # Ensure the foreign key name matches
        batch_op.drop_column('maximum_capacity')

    op.drop_table('attendees')
    # ### end Alembic commands ###
