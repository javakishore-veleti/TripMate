"""Store in-progress trip drafts until the traveler saves.

Revision ID: 20260906_0005
Revises: 20260906_0004
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0005"
down_revision: Union[str, Sequence[str], None] = "20260906_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "draft_plan",
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
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], name="fk_draft_plan_user"),
        sa.UniqueConstraint("thread_id", name="uq_draft_plan_thread"),
    )
    op.create_index("ix_draft_plan_user_id", "draft_plan", ["user_id"])
    op.create_index("ix_draft_plan_updated_at", "draft_plan", ["updated_at"])


def downgrade() -> None:
    op.drop_index("ix_draft_plan_updated_at", table_name="draft_plan")
    op.drop_index("ix_draft_plan_user_id", table_name="draft_plan")
    op.drop_table("draft_plan")
