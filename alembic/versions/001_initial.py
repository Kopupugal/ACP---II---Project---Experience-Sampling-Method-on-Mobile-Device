"""Create users, studies, and immutable study versions.

Revision ID: 001_initial
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="researcher"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "studies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("study_id", sa.String(length=64), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.UniqueConstraint("study_id"),
    )
    op.create_index("ix_studies_study_id", "studies", ["study_id"], unique=True)
    op.create_index("ix_studies_owner_id", "studies", ["owner_id"], unique=False)
    op.create_table(
        "study_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("study_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["study_id"], ["studies.id"]),
        sa.UniqueConstraint("study_id", "version", name="uq_study_version"),
    )
    op.create_index("ix_study_versions_study_id", "study_versions", ["study_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_study_versions_study_id", table_name="study_versions")
    op.drop_table("study_versions")
    op.drop_index("ix_studies_owner_id", table_name="studies")
    op.drop_index("ix_studies_study_id", table_name="studies")
    op.drop_table("studies")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
