"""generalize chat session

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-12-13 13:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Alter product_id to Allow Null
    op.alter_column('product_chat_sessions', 'product_id', nullable=True)
    
    # 2. Add project_id
    op.add_column('product_chat_sessions', sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'product_chat_sessions', 'projects', ['project_id'], ['id'], ondelete='CASCADE')
    
    # 3. Add session_type
    op.add_column('product_chat_sessions', sa.Column('session_type', sa.String(length=50), server_default='product_consult', nullable=False))

def downgrade() -> None:
    op.drop_column('product_chat_sessions', 'session_type')
    op.drop_constraint(None, 'product_chat_sessions', type_='foreignkey')
    op.drop_column('product_chat_sessions', 'project_id')
    op.alter_column('product_chat_sessions', 'product_id', nullable=False)
