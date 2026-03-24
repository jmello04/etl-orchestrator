"""Criação do schema inicial

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cotacoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("par_moeda", sa.String(10), nullable=False),
        sa.Column("data_referencia", sa.Date(), nullable=False),
        sa.Column("compra", sa.Numeric(12, 4), nullable=True),
        sa.Column("venda", sa.Numeric(12, 4), nullable=True),
        sa.Column("maximo", sa.Numeric(12, 4), nullable=True),
        sa.Column("minimo", sa.Numeric(12, 4), nullable=True),
        sa.Column("media_compra_periodo", sa.Numeric(12, 4), nullable=True),
        sa.Column("media_venda_periodo", sa.Numeric(12, 4), nullable=True),
        sa.Column("minimo_periodo", sa.Numeric(12, 4), nullable=True),
        sa.Column("maximo_periodo", sa.Numeric(12, 4), nullable=True),
        sa.Column("processado_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("par_moeda", "data_referencia", name="uq_par_data"),
    )
    op.create_index("ix_cotacoes_par_moeda", "cotacoes", ["par_moeda"])
    op.create_index("ix_cotacoes_data_referencia", "cotacoes", ["data_referencia"])

    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("iniciado_em", sa.DateTime(), nullable=False),
        sa.Column("finalizado_em", sa.DateTime(), nullable=True),
        sa.Column("duracao_segundos", sa.Float(), nullable=True),
        sa.Column("registros_processados", sa.Integer(), nullable=True),
        sa.Column("erro", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("pipeline_runs")
    op.drop_index("ix_cotacoes_data_referencia", table_name="cotacoes")
    op.drop_index("ix_cotacoes_par_moeda", table_name="cotacoes")
    op.drop_table("cotacoes")
