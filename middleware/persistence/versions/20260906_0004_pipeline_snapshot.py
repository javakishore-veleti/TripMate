"""Store agentic pipeline snapshots per signed-in menu.

Revision ID: 20260906_0004
Revises: 20260906_0003
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260906_0004"
down_revision: Union[str, Sequence[str], None] = "20260906_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipeline_snapshot",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("pipeline_key", sa.String(length=80), nullable=False),
        sa.Column("context_json", sa.JSON(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], name="fk_pipeline_snapshot_user"),
        sa.UniqueConstraint("user_id", "pipeline_key", name="uq_pipeline_snapshot_user_key"),
    )
    op.create_index("ix_pipeline_snapshot_user_id", "pipeline_snapshot", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_snapshot_user_id", table_name="pipeline_snapshot")
    op.drop_table("pipeline_snapshot")
