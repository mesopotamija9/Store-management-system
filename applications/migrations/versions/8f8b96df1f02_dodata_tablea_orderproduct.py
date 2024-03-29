"""Dodata tablea OrderProduct

Revision ID: 8f8b96df1f02
Revises: 1df1e9373404
Create Date: 2022-06-19 20:17:22.669476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f8b96df1f02'
down_revision = '1df1e9373404'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orderproduct',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('orderId', sa.Integer(), nullable=False),
    sa.Column('productId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['orderId'], ['order.id'], ),
    sa.ForeignKeyConstraint(['productId'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orderproduct')
    # ### end Alembic commands ###
