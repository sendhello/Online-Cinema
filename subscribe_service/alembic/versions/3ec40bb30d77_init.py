"""init

Revision ID: 3ec40bb30d77
Revises:
Create Date: 2023-10-05 19:47:42.506996

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "3ec40bb30d77"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "subscribe",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("subscribe_type", sa.Enum("MONTHLY", "QUARTERLY", "YEARLY", name="subscribetype"), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_payment", sa.DateTime(timezone=True), nullable=True),
        sa.Column("auto_payment", sa.Boolean(), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "CANCELED", "ACTIVE", "BLOCKED", name="subscribestatus"), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "payment",
        sa.Column("payment_type", sa.Enum("YOOKASSA", "SBER_PAY", name="paymenttype"), nullable=True),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "CREATE",
                "PENDING",
                "WAITING_FOR_CAPTURE",
                "SUCCEEDED",
                "CANCELED",
                "REFUND",
                "ERROR",
                name="paymentstatus",
            ),
            nullable=True,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("subscribe_id", sa.UUID(), nullable=True),
        sa.Column("amount", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.Enum("RUB", "USD", name="currency"), nullable=True),
        sa.Column("remote_id", sa.UUID(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["subscribe_id"], ["subscribe.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("payment")
    op.drop_table("subscribe")
    # ### end Alembic commands ###
