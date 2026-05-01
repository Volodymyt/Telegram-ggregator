from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("target_channel", sa.Text, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("state", sa.Text, nullable=False, server_default="open"),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canonical_message_id", sa.BigInteger, nullable=True),
        sa.Column("published_target_message_id", sa.BigInteger, nullable=True),
        sa.Column("publish_status", sa.Text, nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "tg_message",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("source_chat_id", sa.BigInteger, nullable=False),
        sa.Column("source_message_id", sa.BigInteger, nullable=False),
        sa.Column("source_title", sa.Text, nullable=True),
        sa.Column("source_link", sa.Text, nullable=True),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("normalized_text", sa.Text, nullable=True),
        sa.Column(
            "has_media", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("event_type", sa.Text, nullable=True),
        sa.Column("event_signal", sa.Text, nullable=True),
        sa.Column("candidate_signature", sa.Text, nullable=True),
        sa.Column("event_id", sa.BigInteger, nullable=True),
        sa.Column("classification_status", sa.Text, nullable=False, server_default="pending"),
        sa.Column("aggregation_status", sa.Text, nullable=False, server_default="new"),
        sa.Column("publish_status", sa.Text, nullable=False, server_default="new"),
        sa.Column("filter_reason", sa.Text, nullable=True),
        sa.Column("target_message_id", sa.BigInteger, nullable=True),
        sa.Column(
            "publish_attempts",
            sa.Integer,
            nullable=False,
            server_default="0",
        ),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["event.id"],
            name="fk_tg_message_event_id_event",
        ),
        sa.UniqueConstraint(
            "source_chat_id",
            "source_message_id",
            name="uq_tg_message_source_chat_id_source_message_id",
        ),
    )

    op.create_index(
        "ix_tg_message_classification_status",
        "tg_message",
        ["classification_status"],
    )
    op.create_index(
        "ix_tg_message_event_type_classification_status_received_at",
        "tg_message",
        ["event_type", "classification_status", "received_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tg_message_event_type_classification_status_received_at",
        table_name="tg_message",
    )
    op.drop_index(
        "ix_tg_message_classification_status",
        table_name="tg_message",
    )
    op.drop_table("tg_message")
    op.drop_table("event")
