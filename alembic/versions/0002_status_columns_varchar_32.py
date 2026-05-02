from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STATUS_COLUMNS = (
    ("event", "publish_status"),
    ("tg_message", "classification_status"),
    ("tg_message", "aggregation_status"),
    ("tg_message", "publish_status"),
)


def upgrade() -> None:
    for table_name, column_name in STATUS_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.Text(),
            type_=sa.String(32),
            existing_nullable=False,
        )


def downgrade() -> None:
    for table_name, column_name in STATUS_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.String(32),
            type_=sa.Text(),
            existing_nullable=False,
        )
