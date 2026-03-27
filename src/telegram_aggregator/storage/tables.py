from __future__ import annotations

import sqlalchemy as sa

from telegram_aggregator.storage.metadata import metadata

MESSAGE_STATUSES = (
    "received",
    "filtered_out",
    "candidate",
    "suppressed_duplicate",
    "selected_for_publish",
    "publishing",
    "published",
    "publish_failed",
    "clear_processed",
    "orphan_clear",
)

EVENT_STATES = ("open", "closed")

EVENT_PUBLISH_STATUSES = ("pending", "published", "failed")

event_records = sa.Table(
    "event_records",
    metadata,
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
    sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False,
              server_default=sa.func.now()),
    sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("canonical_message_record_id", sa.BigInteger, nullable=True),
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
        onupdate=sa.func.now(),
    ),
)

message_records = sa.Table(
    "message_records",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("source_chat_id", sa.BigInteger, nullable=False),
    sa.Column("source_message_id", sa.BigInteger, nullable=False),
    sa.Column("source_title", sa.Text, nullable=True),
    sa.Column("source_link", sa.Text, nullable=True),
    sa.Column("raw_text", sa.Text, nullable=True),
    sa.Column("normalized_text", sa.Text, nullable=True),
    sa.Column("has_media", sa.Boolean, nullable=False, server_default="false"),
    sa.Column("event_type", sa.Text, nullable=True),
    sa.Column("event_signal", sa.Text, nullable=True),
    sa.Column("candidate_signature", sa.Text, nullable=True),
    sa.Column(
        "event_record_id",
        sa.BigInteger,
        sa.ForeignKey("event_records.id", name="fk_message_records_event_record_id_event_records"),
        nullable=True,
    ),
    sa.Column("status", sa.Text, nullable=False, server_default="received"),
    sa.Column("filter_reason", sa.Text, nullable=True),
    sa.Column("target_message_id", sa.BigInteger, nullable=True),
    sa.Column("publish_attempts", sa.Integer, nullable=False, server_default="0"),
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
        onupdate=sa.func.now(),
    ),
    sa.UniqueConstraint(
        "source_chat_id",
        "source_message_id",
        name="uq_message_records_source_chat_id_source_message_id",
    ),
    sa.Index("ix_message_records_status", "status"),
    sa.Index(
        "ix_message_records_event_type_status_received_at",
        "event_type",
        "status",
        "received_at",
    ),
)
