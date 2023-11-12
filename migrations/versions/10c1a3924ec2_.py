"""empty message

Revision ID: 10c1a3924ec2
Revises: 873798e30658
Create Date: 2023-11-12 10:48:51.492644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10c1a3924ec2'
down_revision = '873798e30658'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('first_name', sa.String(length=64), nullable=False),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('photo_url', sa.String(length=128), nullable=True),
    sa.Column('auth_date', sa.String(length=16), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_auth_date'), ['auth_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_last_name'), ['last_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_photo_url'), ['photo_url'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('monthly_payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('is_income', sa.Boolean(), nullable=False),
    sa.Column('is_paid', sa.Boolean(), nullable=False),
    sa.Column('added', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('notification', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('monthly_payment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_monthly_payment_added'), ['added'], unique=False)
        batch_op.create_index(batch_op.f('ix_monthly_payment_datetime'), ['datetime'], unique=False)
        batch_op.create_index(batch_op.f('ix_monthly_payment_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_monthly_payment_updated'), ['updated'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('monthly_payment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_monthly_payment_updated'))
        batch_op.drop_index(batch_op.f('ix_monthly_payment_name'))
        batch_op.drop_index(batch_op.f('ix_monthly_payment_datetime'))
        batch_op.drop_index(batch_op.f('ix_monthly_payment_added'))

    op.drop_table('monthly_payment')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_photo_url'))
        batch_op.drop_index(batch_op.f('ix_user_last_name'))
        batch_op.drop_index(batch_op.f('ix_user_id'))
        batch_op.drop_index(batch_op.f('ix_user_first_name'))
        batch_op.drop_index(batch_op.f('ix_user_auth_date'))

    op.drop_table('user')
    # ### end Alembic commands ###