"""Create the initial Synclone schema without disturbing existing tables.

Revision ID: 20261109_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20261109_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # Existing installations may already contain tables created manually with
    # SQLAlchemy metadata.create_all(). Preserve them and add only missing objects.
    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("full_name", sa.String(length=150), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_email" not in indexes:
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "clone_backups" not in tables:
        op.create_table(
            "clone_backups",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("clone_identifier", sa.String(length=100), nullable=False),
            sa.Column("resident_name", sa.String(length=150), nullable=False),
            sa.Column("memory_payload_hash", sa.String(length=255), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("clone_backups")}
    expected = {
        "ix_clone_backups_id": ["id"],
        "ix_clone_backups_owner_id": ["owner_id"],
        "ix_clone_backups_clone_identifier": ["clone_identifier"],
        "ix_clone_backups_owner_clone": ["owner_id", "clone_identifier"],
    }
    for name, columns in expected.items():
        if name not in indexes:
            op.create_index(name, "clone_backups", columns, unique=False)


def downgrade() -> None:
    # This baseline can be adopted by databases containing pre-existing user data.
    # Do not drop application tables as an automatic downgrade would destroy data.
    pass
