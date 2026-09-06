"""Initial AppUser, session, and travel request schema.

Revision ID: 20260906_0001
Revises:
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_user",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_app_user_email"),
    )
    op.create_table(
        "app_session",
        sa.Column("token", sa.String(length=128), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], name="fk_app_session_user"),
    )
    op.create_index("ix_app_session_user_id", "app_session", ["user_id"])
    op.create_table(
        "travel_request",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("thread_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("agentic_adapter", sa.String(length=40), nullable=False),
        sa.Column("llm_provider", sa.String(length=40), nullable=False),
        sa.Column("llm_model", sa.String(length=120), nullable=False),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column("hitl", sa.JSON(), nullable=False),
        sa.Column("usage", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], name="fk_travel_request_user"),
        sa.UniqueConstraint("thread_id", name="uq_travel_request_thread_id"),
    )
    op.create_index("ix_travel_request_user_id", "travel_request", ["user_id"])
    op.create_index("ix_travel_request_updated_at", "travel_request", ["updated_at"])


def downgrade() -> None:
    op.drop_index("ix_travel_request_updated_at", table_name="travel_request")
    op.drop_index("ix_travel_request_user_id", table_name="travel_request")
    op.drop_table("travel_request")
    op.drop_index("ix_app_session_user_id", table_name="app_session")
    op.drop_table("app_session")
    op.drop_table("app_user")
