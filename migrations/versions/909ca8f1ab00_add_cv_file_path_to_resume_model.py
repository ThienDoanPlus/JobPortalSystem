"""Add cv_file_path to Resume model

Revision ID: 909ca8f1ab00
Revises: c5881929d07e
Create Date: 2025-07-23 13:14:39.287582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '909ca8f1ab00'
down_revision = 'c5881929d07e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resume', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cv_file_path', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resume', schema=None) as batch_op:
        batch_op.drop_column('cv_file_path')

    # ### end Alembic commands ###
